"""Benchmark a model's fitness for the TRIDENT inner layer.

The inner layer turns a conversation into a fixed block of labelled lines:

    ConfirmHelpful: ...
    TitleOfMap: ...
    Area: Sendai, Miyagi
    AreaWithConcern: Sendai, Miyagi, Schools
    EmojiForConcern: Schools, <emoji>
    ColorForConcern: Schools, orange

That is a mapping task, not free generation, so it is a plausible target for a
small fine-tuned model in the same way the deep layer already is. This script
measures how close an off-the-shelf model gets before any fine-tuning.

Scoring keeps format and content apart, because they have different remedies.
A model that writes the right area and concern but forgets a colon is a
fine-tuning candidate. A model that answers "Cafes" with "Ramen shops" copied
from the few-shot examples is not, however tidy its formatting looks. Counting
only whether the labels appear ranks the second model above the first.

The system under test is TRIDENT's inner endpoint, not a prompt kept here.
TRIDENT owns that prompt and selects the few-shot examples from its own vector
store, so duplicating it in this repo would measure something else within a
week. Point TRIDENT at the model you want to measure and run this against it:

    # 1. serve the candidate
    llama-server -hf unsloth/Qwen3-0.6B-GGUF:Q4_K_M -a trident-inner \\
        -c 8192 -n 512 --host 127.0.0.1 --port 18091

    # 2. in TRIDENT, point the inner role at it and start the app
    #    .env.local: USE_LLAMA_CPP=1
    #                LLAMA_CPP_INNER_BASE_URL=http://127.0.0.1:18091/v1

    # 3. score it
    uv run python src/benchmark_inner.py --label Qwen3-0.6B \\
        --trident-url http://127.0.0.1:3000

Repeat per candidate, then compare the JSON reports:

    uv run python src/benchmark_inner.py --compare tmp/benchmark-inner-*.json

Output:
    One JSON report per run in tmp/benchmark-inner-{slug}-{timestamp}.json
    A summary table printed after the run.
"""

from __future__ import annotations

import argparse
import unicodedata
from typing import Literal
import glob
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import httpx

DEFAULT_TRIDENT_URL = "http://127.0.0.1:3000"
DEFAULT_TIMEOUT = 300.0

# Above this many characters the model is repeating itself rather than
# answering. A well-formed reply for these cases is under 500.
RUNAWAY_CHARS = 1500

REQUIRED_KEYS = (
    "TitleOfMap:",
    "Area:",
    "AreaWithConcern:",
    "EmojiForConcern:",
    "ColorForConcern:",
)


@dataclass(frozen=True)
class InnerCase:
    """One request, expressed as the area and concern the model must recover.

    `utterance` carries the words when they matter. The original ten are
    templated from area and concern; the field set below is made of sentences
    somebody actually wrote, which is a different thing to measure.
    """

    area: str
    concern: str
    utterance: str | None = None
    source: str = "template"
    expect_empty: bool = False

    @property
    def slug(self) -> str:
        return f"{self.concern}@{self.area}".replace(", ", "-").replace(" ", "_").lower()


# Ten requests of the same shape, varying the hierarchy and the concern.
# "Fukuoka, Fukuoka" and "Kyoto, Kyoto" repeat the name at city and prefecture
# level, which is where small models silently drop a level.
INNER_CASES: list[InnerCase] = [
    InnerCase("Taito, Tokyo", "Cafes"),
    InnerCase("Shinjuku, Tokyo", "Hotels"),
    InnerCase("Shibuya, Tokyo", "Bakeries"),
    InnerCase("Naha, Okinawa", "Hospitals"),
    InnerCase("Sendai, Miyagi", "Schools"),
    InnerCase("Kobe, Hyogo", "Pharmacies"),
    InnerCase("Sapporo, Hokkaido", "Parks"),
    InnerCase("Fukuoka, Fukuoka", "Libraries"),
    InnerCase("Nagoya, Aichi", "Convenience stores"),
    InnerCase("Kyoto, Kyoto", "Restaurants"),
]


_JAPANESE = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")


def _has_japanese(text: str) -> bool:
    return bool(_JAPANESE.search(text))


# A second set, kept alongside the first rather than replacing it.
#
# The ten above ask "Show me {concern} in {area}" in English and nothing else.
# Every figure in the findings rests on them, so they are frozen. But the
# inner layer is being fine-tuned for Japanese and for area strings four
# levels deep, and a set that contains neither cannot say whether that worked.
#
# recorded    words somebody actually typed or spoke, taken from the session
#             memos and the pi5-deck voice tests. Small, but nobody's habits
#             are in them except a real user's.
# constructed written to cover a case the recorded ones miss. Each says why.
FIELD_CASES: list[InnerCase] = [
    # --- recorded -------------------------------------------------------
    InnerCase("Taito, Tokyo", "Soba noodle shops",
              "台東区の蕎麦屋を表示して", "recorded"),
    InnerCase("Taito, Tokyo", "Cafes", "台東区を表示して", "recorded"),
    InnerCase("Hiroshima", "Cafes", "広島のカフェを表示して", "recorded"),
    InnerCase("広島市", "Cafes", "広島市のカフェを表示して", "recorded"),
    InnerCase("Kyoto", "Bakeries", "Find bakeries in Kyoto.", "recorded"),
    InnerCase("Shibuya, Tokyo", "Bakeries",
              "Show me bakeries in Shibuya, Tokyo", "recorded"),
    InnerCase("Shinjuku, Tokyo", "Hotels",
              "Show me hotels in Shinjuku, Tokyo.", "recorded"),
    # The suffix is what lets the geocoding ladder ask for a settlement rather
    # than take Nominatim's best guess, which is the prefecture. Preserved, it
    # resolves to area 3604097196 (admin_level 7) and finds 123 cafes.
    InnerCase("Hiroshima City", "Cafes", "Show me cafes in Hiroshima City.", "recorded"),
    InnerCase("Taito, Tokyo", "Cafes", "Show me cafes in Taito, Tokyo", "recorded"),

    # --- constructed ----------------------------------------------------
    # Four levels. Broke the generator twice: the seed resolves and the
    # model's shorter reading does not.
    InnerCase("Chuo Ward, Niigata, Niigata Prefecture, Japan", "Airports",
              "新潟県新潟市中央区の空港を教えてください", "constructed",
              expect_empty=True),
    # The same place named the way a person writes it, with -ku.
    InnerCase("Chuo Ward, Niigata, Niigata Prefecture, Japan", "Airports",
              "chuo-ku niigata airports", "constructed", expect_empty=True),
    # A concern that finds nothing where it is asked for. zero_results pairs
    # are in the training set, so the ability has to be measured.
    InnerCase("Taito, Tokyo", "Mosques", "台東区のモスクを教えて", "constructed",
              expect_empty=True),
    # An island group; the geocoder does not resolve the plural form.
    InnerCase("Ogasawara, Tokyo, Japan", "Aquariums",
              "小笠原諸島にある水族館を教えてください", "constructed",
              expect_empty=True),
    # Two wards whose names differ by one character. 西成区 is not 西区.
    InnerCase("Nishinari Ward, Osaka, Osaka Prefecture, Japan", "Bakeries",
              "西成区のパン屋さんを教えてください", "constructed"),
    # Politeness and word order a template never produces.
    InnerCase("Sapporo, Hokkaido", "Cafes", "札幌の喫茶店、どこかいいとこある？",
              "constructed"),
    InnerCase("Naha, Okinawa", "Hotels", "那覇 ホテル 一覧", "constructed"),
]


PastMessageStyle = Literal["production", "with-reply"]


def build_past_messages(
    case: InnerCase, *, style: PastMessageStyle = "production"
) -> list[str]:
    """The conversation the inner layer sees.

    "production" is what the browser sends. /api/ai/surface returns `history`
    as the prior turns plus the query and never appends its own reply, so the
    first turn arrives as one human utterance. Appending a fixed surface reply
    built a prompt the system never builds, and a longer one: the inner layer
    answers faster without it.

    "with-reply" keeps the two-element form the earlier reports were measured
    with, so those numbers stay reproducible. Every report records which style
    produced it; do not compare across styles.
    """
    concern = case.concern.lower()
    query = case.utterance or f"Show me {concern} in {case.area}"
    if style == "production":
        return [query]
    reply = (
        "Ability: overpass-api\n"
        f"Reply: I copy. I'm generating maps that shows {concern} in {case.area} "
        "based on OpenStreetMap data. Please wait a while..."
    )
    return [query, reply]


@dataclass
class InnerScore:
    """How one reply did, split into format and content."""

    case: str
    keys_present: bool
    style_present: bool
    area_ok: bool
    concern_ok: bool
    runaway: bool
    length: int
    area_with_concern: str
    error: str | None = None

    @property
    def errored(self) -> bool:
        """The request never produced an answer, so there is nothing to grade."""
        return self.error is not None

    @property
    def good(self) -> bool:
        return (
            not self.errored
            and self.keys_present
            and self.area_ok
            and self.concern_ok
            and not self.runaway
        )


def _area_with_concern_line(text: str) -> str:
    for line in text.split("\n"):
        if line.strip().startswith("AreaWithConcern"):
            return line.strip()
    return ""


def _fold(text: str) -> str:
    """Lowercase and drop accents.

    Qwen3-0.6B writes "Cafés" where the examples write "Cafes". Fed straight
    to the deep layer that still produces amenity=cafe and the correct area
    ids, so the accent changes nothing downstream. Scoring it as a wrong
    answer measured the scorer's strictness, not the model's.
    """
    stripped = unicodedata.normalize("NFKD", text)
    return "".join(c for c in stripped if not unicodedata.combining(c)).lower()


def _concern_matches(written: str, expected: str) -> bool:
    """Plural and singular both count; "Pharmacies" may come back as "Pharmacy"."""
    stem = _fold(expected)
    if stem.endswith("ies"):
        stem = stem[:-3]  # pharmacies -> pharmac, matching pharmacy too
    elif stem.endswith("s"):
        stem = stem[:-1]
    return stem in _fold(written)


def score_inner_output(text: str, case: InnerCase, *, error: str | None = None) -> InnerScore:
    """Score one reply. Never raises.

    Pass `error` when the request itself failed. A llama-server that ran out of
    VRAM returns nothing, and grading that as a wrong answer reports an
    infrastructure failure as a model result.
    """
    text = text or ""
    line = _area_with_concern_line(text)
    body = re.sub(r"^AreaWithConcern\s*:?\s*", "", line).strip()

    expected_area = [_fold(part.strip()) for part in case.area.split(",")]
    written = [_fold(part.strip()) for part in body.split(",")]

    return InnerScore(
        case=case.slug,
        keys_present=all(key in text for key in REQUIRED_KEYS),
        style_present="EmojiForConcern" in text and "ColorForConcern" in text,
        # The area must lead, in the order given. A model that writes
        # "Cafes in Taito, Tokyo" has understood the request and lost the format.
        area_ok=bool(body) and written[: len(expected_area)] == expected_area,
        concern_ok=bool(body) and _concern_matches(body, case.concern),
        runaway=len(text) > RUNAWAY_CHARS,
        length=len(text),
        area_with_concern=line,
        error=error,
    )


def summarize(scores: list[InnerScore]) -> dict:
    answered = [s for s in scores if not s.errored]
    return {
        "n": len(scores),
        "errors": sum(1 for s in scores if s.errored),
        "answered": len(answered),
        # A run where nothing answered says nothing about the model.
        "valid": bool(answered),
        "keys_present": sum(1 for s in scores if s.keys_present),
        "style_present": sum(1 for s in scores if s.style_present),
        "area_ok": sum(1 for s in scores if s.area_ok),
        "concern_ok": sum(1 for s in scores if s.concern_ok),
        "runaway": sum(1 for s in scores if s.runaway),
        "good": sum(1 for s in scores if s.good),
    }


def ask_inner(
    trident_url: str,
    case: InnerCase,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    style: PastMessageStyle = "production",
) -> str:
    """POST one case to TRIDENT's inner endpoint and return the raw reply."""
    response = httpx.post(
        f"{trident_url.rstrip('/')}/api/ai/inner",
        json={"pastMessages": build_past_messages(case, style=style)},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json().get("inner", "")


def render_markdown_table(reports: list[dict]) -> str:
    """One row per model, format and content columns kept separate.

    Errors get their own column so a run that failed to reach the model is not
    read as a model that answered badly.
    """
    header = (
        "| model | backend | n | errors | keys | style | area | concern | runaway | all correct |\n"
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"
    )
    rows = []
    for report in reports:
        s = report["summary"]
        n = s["n"]
        answered = s.get("answered", n)
        backend = report.get("backend", "?")
        if not s.get("valid", True):
            rows.append(
                f"| {report['label']} | {backend} | {n} | {s.get('errors', 0)}/{n} "
                "| - | - | - | - | - | INVALID |"
            )
            continue
        rows.append(
            f"| {report['label']} | {backend} | {answered} | {s.get('errors', 0)}/{n} "
            f"| {s['keys_present']}/{answered} | {s['style_present']}/{answered} "
            f"| {s['area_ok']}/{answered} | {s['concern_ok']}/{answered} "
            f"| {s['runaway']}/{answered} | {s['good']}/{answered} |"
        )
    return header + "\n" + "\n".join(rows)


def cases_for(name: str) -> list[InnerCase]:
    if name == "field":
        return FIELD_CASES
    if name == "both":
        return INNER_CASES + FIELD_CASES
    return INNER_CASES


def run(
    label: str,
    trident_url: str,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    backend: str = "unspecified",
    case_set: str = "template",
    style: PastMessageStyle = "production",
) -> dict:
    scores: list[InnerScore] = []
    for index, case in enumerate(cases_for(case_set)):
        error: str | None = None
        text = ""
        try:
            text = ask_inner(trident_url, case, timeout=timeout, style=style)
            if not text.strip():
                error = "empty reply"
        except Exception as exc:  # a hang or a 500 is a result, not a crash
            error = f"{type(exc).__name__}: {exc}"
        score = score_inner_output(text, case, error=error)
        scores.append(score)
        verdict = "ERR" if score.errored else ("ok " if score.good else "BAD")
        detail = score.error if score.errored else score.area_with_concern[:58]
        print(f"  case {index} {verdict} {score.length:6d}ch | {detail}")
    return {
        "label": label,
        "backend": backend,
        "case_set": case_set,
        "past_message_style": style,
        "trident_url": trident_url,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summarize(scores),
        "scores": [asdict(s) | {"good": s.good} for s in scores],
    }


def _slug(label: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", label).strip("-").lower()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--label", help="Name of the model behind TRIDENT's inner role")
    parser.add_argument("--trident-url", default=DEFAULT_TRIDENT_URL)
    parser.add_argument(
        "--set",
        choices=("template", "field", "both"),
        default="template",
        help="template: the frozen ten every earlier figure was measured on. "
        "field: recorded and constructed utterances, Japanese included. "
        "Report both after fine-tuning; a drop on template means something broke.",
    )
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument(
        "--format",
        dest="style",
        choices=("production", "with-reply"),
        default="production",
        help=(
            "What to put in pastMessages. 'production' is the single utterance "
            "the browser sends; 'with-reply' appends a fixed surface reply, as "
            "the reports before 2026-08-28 did. Never compare across the two."
        ),
    )
    parser.add_argument("--out-dir", default="tmp")
    parser.add_argument(
        "--backend",
        default="unspecified",
        help='Where the model ran, e.g. "gpu" or "cpu". Recorded in the report.',
    )
    parser.add_argument(
        "--compare",
        nargs="+",
        help="Render a table from existing JSON reports instead of running",
    )
    args = parser.parse_args()

    if args.compare:
        paths = sorted(p for pattern in args.compare for p in glob.glob(pattern))
        reports = [json.loads(Path(p).read_text()) for p in paths]
        print(render_markdown_table(reports))
        return

    if not args.label:
        parser.error("--label is required unless --compare is given")

    print(f"Benchmarking inner layer: {args.label} via {args.trident_url} "
          f"[{args.set}, {len(cases_for(args.set))} cases, {args.style} format]")
    report = run(
        args.label,
        args.trident_url,
        timeout=args.timeout,
        backend=args.backend,
        case_set=args.set,
        style=args.style,
    )

    if not report["summary"]["valid"]:
        print("\nEvery request failed — this says nothing about the model.")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    out_path = out_dir / f"benchmark-inner-{_slug(args.label)}-{stamp}.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")

    print()
    print(render_markdown_table([report]))
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
