"""Turn the generator's record into a training set for the inner layer.

`generate_inner_pairs.py` writes what happened to every utterance it made:
the reading the golden model produced, the query the deep layer built from
it, how many elements Overpass returned, and a verdict. That file is a
record, not a training set. This is the step between.

Two judgements are made here, and both are deliberate.

**Which verdicts are usable.** `accepted` and `zero_results` both describe a
correct reading; the second one merely names something OSM has no instance
of, which is the mapping's business and not the model's. `deep_gap` is a net
for readings that drifted (measured: 54% keep the concern), so it is taken
only when the concern survived. `wrong_area`, `invented_name`, `no_area_line`
and `leaked` are dropped: a place that is somewhere else, or nowhere, would
teach exactly the failure the fine-tune is meant to remove.

**What the target says.** Not the golden model's reply. 41% of accepted rows
name fewer levels than the seed does — "Higashi Ward, Niigata, Niigata
Prefecture, Japan" comes back as "Higashi-ku, Niigata". Overpass still finds
something, so the verdict is accepted, but the seed is the validated form and
the shortened one is the known weakness. The target carries the seed's area
and concern, and keeps the model's title, emoji and colour.

The reply language is checked too. The golden model drifts into Korean and
Chinese on Japanese input often enough to matter (242 rows), and a training
set that does that teaches it.

    uv run python src/build_inner_trainset.py tmp/inner-pairs-production.jsonl
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path

KEY_ORDER = (
    "ConfirmHelpful",
    "TitleOfMap",
    "Area",
    "AreaWithConcern",
    "EmojiForConcern",
    "ColorForConcern",
)

USABLE_OUTRIGHT = frozenset({"accepted", "zero_results"})

# One confirmation per language, taken from the most common form the golden
# model produced in that language. Used only to replace a line written in the
# wrong language; a matching line is never touched.
CONFIRMATIONS = {
    "ja": "地図の作成が完了しました。他にご要望はありますか？お役に立てましたでしょうか？",
    "en": "Mapping has been completed. Do you have any other requests? Were we helpful?",
}
USABLE_IF_FAITHFUL = frozenset({"deep_gap"})


@dataclass(frozen=True)
class Pair:
    """One training example, plus what it is made of.

    The metadata is kept so a later run can weight or filter without going
    back to the generator's record.
    """

    input: str
    output: str
    lang: str
    levels: int
    verdict: str


def area_levels(area: str) -> int:
    """How many administrative levels a comma-separated area names."""
    return len([part for part in (area or "").split(",") if part.strip()])


def written_area(row: dict) -> str:
    """The area the model wrote, with the trailing concern removed."""
    line = row.get("area_with_concern") or ""
    body = re.sub(r"^\s*AreaWithConcern\s*:?\s*", "", line).strip()
    parts = [part.strip() for part in body.split(",") if part.strip()]
    return ", ".join(parts[:-1])


def _fold(text: str) -> str:
    stripped = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in stripped if not unicodedata.combining(c)).lower()


def concern_is_faithful(row: dict) -> bool:
    """Did the concern survive the reading?

    Plural and singular both count, the same rule the benchmark uses.
    """
    stem = _fold(row.get("seed_concern") or "")
    if stem.endswith("ies"):
        stem = stem[:-3]
    elif stem.endswith("s"):
        stem = stem[:-1]
    return bool(stem) and stem in _fold(row.get("area_with_concern") or "")


def _lines(inner_output: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for line in (inner_output or "").splitlines():
        line = line.strip().strip("`").strip()
        for key in KEY_ORDER:
            if line.startswith(f"{key}:") and key not in found:
                found[key] = line[len(key) + 1 :].strip()
    return found


def reply_language(text: str) -> str:
    """Which script the confirmation is written in.

    Kana settles Japanese. Hangul settles Korean. Han with no kana is
    Chinese — the drift that matters, because a Japanese utterance answered
    in Chinese looks superficially plausible.
    """
    if not text:
        return "unknown"
    has_kana = any("぀" <= c <= "ヿ" for c in text)
    has_hangul = any("가" <= c <= "힯" for c in text)
    has_han = any("一" <= c <= "鿿" for c in text)
    if has_hangul:
        return "ko"
    if has_kana:
        return "ja"
    if has_han:
        return "zh"
    return "en"


def reply_language_matches(row: dict) -> bool:
    """The confirmation must be in the language the human wrote in."""
    confirm = _lines(row.get("inner_output", "")).get("ConfirmHelpful", "")
    if not confirm:
        return False
    return reply_language(confirm) == (row.get("lang") or "en")


def repaired_confirmation(row: dict) -> str:
    """The confirmation to train towards, in the language the human used."""
    written = _lines(row.get("inner_output", "")).get("ConfirmHelpful", "")
    lang = row.get("lang") or "en"
    if written and reply_language(written) == lang:
        return written
    return CONFIRMATIONS.get(lang, CONFIRMATIONS["en"])


def build_target(row: dict, *, repair_confirmation: bool = False) -> str:
    """The intermediate language block to train towards.

    Area and AreaWithConcern come from the validated seed. Title, emoji and
    colour come from the golden model, which is what it is good at.
    """
    written = _lines(row.get("inner_output", ""))
    area = (row.get("seed_area") or "").strip()
    concern = (row.get("seed_concern") or "").strip()
    values = {
        "ConfirmHelpful": (
            repaired_confirmation(row)
            if repair_confirmation
            else written.get("ConfirmHelpful", "")
        ),
        "TitleOfMap": written.get("TitleOfMap", ""),
        "Area": area,
        "AreaWithConcern": f"{area}, {concern}" if area else concern,
        "EmojiForConcern": written.get("EmojiForConcern", ""),
        "ColorForConcern": written.get("ColorForConcern", ""),
    }
    return "\n".join(f"{key}: {values[key]}" for key in KEY_ORDER)


def _usable(row: dict, *, repair_confirmation: bool = False) -> str | None:
    """None when the row is usable, otherwise why it was dropped."""
    verdict = row.get("verdict")
    if verdict in USABLE_IF_FAITHFUL:
        if not concern_is_faithful(row):
            return "deep_gap_unfaithful"
    elif verdict not in USABLE_OUTRIGHT:
        return verdict or "unknown"
    if not (row.get("utterance") or "").strip():
        return "no_utterance"
    if not (row.get("seed_area") or "").strip():
        return "no_seed_area"
    written = _lines(row.get("inner_output", ""))
    if not all(written.get(key) for key in ("TitleOfMap", "EmojiForConcern", "ColorForConcern")):
        return "incomplete_block"
    if not repair_confirmation and not reply_language_matches(row):
        return "reply_language"
    return None


def select(
    rows: list[dict], *, repair_confirmation: bool = False
) -> tuple[list[Pair], collections.Counter]:
    """The rows worth training on, and a tally of why the rest were not."""
    reasons: collections.Counter = collections.Counter()
    seen: set[str] = set()
    chosen: list[Pair] = []
    for row in rows:
        dropped = _usable(row, repair_confirmation=repair_confirmation)
        if dropped:
            reasons[dropped] += 1
            continue
        utterance = row["utterance"].strip()
        if utterance in seen:
            reasons["duplicate"] += 1
            continue
        seen.add(utterance)
        chosen.append(
            Pair(
                input=utterance,
                output=build_target(row, repair_confirmation=repair_confirmation),
                lang=row.get("lang") or "en",
                levels=area_levels(row.get("seed_area") or ""),
                verdict=row.get("verdict") or "",
            )
        )
    return chosen, reasons


def split(pairs: list[Pair], *, valid_fraction: float = 0.05) -> tuple[list[Pair], list[Pair]]:
    """A held-out slice chosen by hash, so the same input always lands the same side.

    Hashing the utterance rather than shuffling keeps the split stable when
    the generator is re-run and the file grows.
    """
    if not pairs:
        return [], []
    cutoff = int(valid_fraction * (1 << 32))
    train, valid = [], []
    for pair in pairs:
        digest = hashlib.sha256(pair.input.encode("utf-8")).digest()
        bucket = int.from_bytes(digest[:4], "big")
        (valid if bucket < cutoff else train).append(pair)
    return train, valid


def load(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def describe(pairs: list[Pair]) -> dict:
    return {
        "n": len(pairs),
        "by_lang": dict(collections.Counter(p.lang for p in pairs)),
        "by_levels": dict(sorted(collections.Counter(p.levels for p in pairs).items())),
        "by_verdict": dict(collections.Counter(p.verdict for p in pairs)),
    }


def write_jsonl(path: Path, pairs: list[Pair]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        for pair in pairs:
            handle.write(json.dumps(asdict(pair), ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("record", type=Path, help="JSONL written by generate_inner_pairs.py")
    parser.add_argument("--out-dir", type=Path, default=Path("data/inner"))
    parser.add_argument("--valid-fraction", type=float, default=0.05)
    parser.add_argument(
        "--drop-language-drift",
        action="store_true",
        help=(
            "Drop rows whose confirmation is in the wrong language instead of "
            "replacing that one line. The default keeps them: area and concern "
            "come from the seed, so only the decorative line was wrong."
        ),
    )
    args = parser.parse_args()

    rows = load(args.record)
    pairs, reasons = select(rows, repair_confirmation=not args.drop_language_drift)
    train, valid = split(pairs, valid_fraction=args.valid_fraction)

    write_jsonl(args.out_dir / "train.jsonl", train)
    write_jsonl(args.out_dir / "valid.jsonl", valid)

    report = {
        "record": str(args.record),
        "rows_read": len(rows),
        "pairs": describe(pairs),
        "train": describe(train),
        "valid": describe(valid),
        "dropped": dict(reasons.most_common()),
        "confirmation_repaired": (
            0
            if args.drop_language_drift
            else sum(1 for r in rows if not reply_language_matches(r) and not _usable(r, repair_confirmation=True))
        ),
    }
    (args.out_dir / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    )

    print(f"read {len(rows)} rows -> {len(pairs)} pairs "
          f"({len(train)} train / {len(valid)} valid)")
    print(f"  language  {report['pairs']['by_lang']}")
    print(f"  levels    {report['pairs']['by_levels']}")
    print("  dropped")
    for reason, count in reasons.most_common():
        print(f"    {reason:22s} {count:5d}")
    print(f"wrote {args.out_dir}/train.jsonl, valid.jsonl, report.json")


if __name__ == "__main__":
    main()
