"""Generate training pairs for the TRIDENT inner layer by working backwards.

The inner layer turns a conversation into a block of labelled lines. Collecting
that pairing the obvious way means writing utterances first and hoping the
label is right. Going the other way is easier to keep correct: the label is the
seed, built by template from an (area, concern) pair the dataset already
trusts, and a large model is asked what a person would have typed to get it.

    (Taito, Tokyo) + Cafes
        -> AreaWithConcern: Taito, Tokyo, Cafes          the label, by template
        -> "台東区の喫茶店一覧"                            invented by the model

Nothing about the utterance is trusted yet, so each one is put back through
TRIDENT's own inner layer, driven by the same large model, with the real prompt
and its retrieved examples. What comes out is judged on two things:

  the area must match the seed
      A wrong place passes an Overpass check easily, because Osaka has cafes
      too. Area matching is what catches it, and it is reliable: in a six-way
      test every reconstruction recovered "Taito, Tokyo", including from
      "台東でカフェを探して", where the prefecture is not written down.

  the concern must actually find something
      The concern is free to drift. "Cafes" comes back as "Coffee shops" or
      "Cafe" more often than not, and all three are fair readings. Rather than
      arbitrate, hand the AreaWithConcern line to the deep layer and run the
      query: a concern that returns features is a concern worth learning.

This inherits a known bias. A correct answer that legitimately finds nothing —
mosques in Taito, airports in a small city — is rejected, and a model trained
only on what returns features learns to avoid rare concerns. Those pairs are
kept separately rather than thrown away, so the bias is a choice and not an
accident.

Usage:
    uv run python src/generate_inner_pairs.py --limit 3 --variants 6
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import httpx

from nominatim import get_osm_relation_id

TEACHER_URL = "http://10.108.45.102:8080/v1/chat/completions"
TRIDENT_URL = "http://127.0.0.1:3399"
OVERPASS_URL = "http://127.0.0.1:30112/api/interpreter"

DEFAULT_TIMEOUT = 300.0

# Enough to seed a reconstruction. The emoji and colour barely steer the
# utterance, so a fallback is fine where the concern is not listed.
CONCERN_STYLE: dict[str, tuple[str, str]] = {
    "Cafes": ("coffee", "brown"),
    "Restaurants": ("fork_and_knife", "pink"),
    "Hotels": ("hotel", "lightblue"),
    "Hospitals": ("hospital", "red"),
    "Schools": ("school", "orange"),
    "Parks": ("park", "green"),
    "Libraries": ("books", "purple"),
    "Bakeries": ("bread", "wheat"),
    "Pharmacies": ("pill", "lightgreen"),
    "Convenience stores": ("convenience_store", "skyblue"),
}
DEFAULT_STYLE = ("round_pushpin", "gray")

# Vocabulary that only appears in the internal format. An utterance carrying it
# is the label with a verb bolted on, and teaches the model nothing.
LEAK_TOKENS = (
    "areawithconcern",
    "emojiforconcern",
    "colorforconcern",
    "titleofmap",
    "confirmhelpful",
)

REVERSE_SYSTEM = (
    "You reconstruct the human utterance that a map assistant was answering. "
    "You are given the assistant's internal map definition. "
    'Output ONLY a JSON array of objects, each {"lang":"ja"|"en","utterance":"..."}. '
    "The utterance must be what an ordinary person would type into a map app. "
    "It MUST NOT contain the words Area, AreaWithConcern, Emoji, Color, or any "
    "part of the internal format. Vary politeness, length and phrasing. "
    "Half Japanese, half English."
)


@dataclass(frozen=True)
class Seed:
    """One (area, concern) pair the dataset already trusts."""

    area: str
    concern: str

    @property
    def area_parts(self) -> list[str]:
        return [part.strip() for part in self.area.split(",") if part.strip()]


def build_intermediate(seed: Seed) -> str:
    """The label, assembled rather than generated."""
    emoji, color = CONCERN_STYLE.get(seed.concern, DEFAULT_STYLE)
    return "\n".join(
        [
            f"TitleOfMap: {seed.concern} in {seed.area}",
            f"Area: {seed.area}",
            f"AreaWithConcern: {seed.area}, {seed.concern}",
            f"EmojiForConcern: {seed.concern}, {emoji}",
            f"ColorForConcern: {seed.concern}, {color}",
        ]
    )


def _as_item(raw: object) -> dict[str, str] | None:
    if not isinstance(raw, dict):
        return None
    utterance = str(raw.get("utterance", "")).strip()
    if not utterance:
        return None
    lang = str(raw.get("lang", "")).strip().lower()
    return {"lang": lang if lang in ("ja", "en") else "unknown", "utterance": utterance}


def parse_utterances(reply: str) -> list[dict[str, str]]:
    """Read the teacher's JSON array, tolerating whatever it wraps around it.

    A reply cut off by max_tokens leaves the array unclosed, and json.loads
    rejects the whole thing. Losing a batch that way cost every utterance for
    one seed in the first run, so fall back to reading the objects one by one.
    """
    if not reply:
        return []
    match = re.search(r"\[[\s\S]*\]", reply)
    parsed: object = None
    if match:
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError:
            parsed = None
    if parsed is None:
        salvaged = []
        for chunk in re.findall(r"\{[^{}]*\}", reply):
            try:
                item = _as_item(json.loads(chunk))
            except json.JSONDecodeError:
                continue
            if item:
                salvaged.append(item)
        return salvaged
    out = []
    for item in parsed if isinstance(parsed, list) else []:
        if not isinstance(item, dict):
            continue
        utterance = str(item.get("utterance", "")).strip()
        if not utterance:
            continue
        lang = str(item.get("lang", "")).strip().lower()
        out.append({"lang": lang if lang in ("ja", "en") else "unknown",
                    "utterance": utterance})
    return out


def looks_like_leak(utterance: str) -> bool:
    """True when the utterance is the label wearing a disguise."""
    lowered = utterance.lower()
    return any(token in lowered for token in LEAK_TOKENS)


def _normalise(part: str) -> str:
    return part.strip().lower()


def area_matches(written: str, seed: Seed) -> bool:
    """Whether an AreaWithConcern line names the seed's area, in order.

    The concern follows the areas, so only the leading parts are compared.
    """
    body = re.sub(r"^AreaWithConcern\s*:?\s*", "", (written or "").strip())
    parts = [_normalise(p) for p in body.split(",")]
    expected = [_normalise(p) for p in seed.area_parts]
    return bool(body) and parts[: len(expected)] == expected


AreaResolver = "Callable[[str], int | None]"


def same_place(written: str, seed_area: str, resolve) -> bool:
    """Whether two area strings name the same administrative relation.

    String equality is too strict. "札幌のカフェを教えて" produces
    "Sapporo" against a seed of "Sapporo, Hokkaido", and no one says the
    prefecture out loud. The seed is the redundant one; comparing the
    relations each name resolves to settles it without loosening the check
    enough to let Osaka through.
    """
    if _normalise(written) == _normalise(seed_area):
        return True
    written_id = resolve(written)
    if written_id is None:
        return False
    return written_id == resolve(seed_area)


def area_with_concern_line(inner_output: str) -> str:
    for line in (inner_output or "").split("\n"):
        if line.strip().startswith("AreaWithConcern"):
            return line.strip()
    return ""


@dataclass
class PairResult:
    """One utterance, and how far it got."""

    seed_area: str
    seed_concern: str
    lang: str
    utterance: str
    inner_output: str = ""
    area_with_concern: str = ""
    overpass_query: str = ""
    element_count: int = 0
    verdict: str = "pending"
    note: str = ""

    def as_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


def area_part(area_with_concern: str, seed: Seed) -> str:
    """The area half of an AreaWithConcern line, as many parts as the seed has.

    The concern trails the areas and has no marker, so the seed's shape is
    what says where to cut.
    """
    body = re.sub(r"^AreaWithConcern\s*:?\s*", "", (area_with_concern or "").strip())
    parts = [p.strip() for p in body.split(",") if p.strip()]
    if not parts:
        return ""
    # Never take the last part: that is the concern.
    take = min(len(seed.area_parts), max(len(parts) - 1, 1))
    return ", ".join(parts[:take])


def resolve_area(name: str) -> int | None:
    try:
        return get_osm_relation_id(name)
    except Exception:
        return None


@dataclass
class Counts:
    accepted: int = 0
    deep_gap: int = 0
    zero_results: int = 0
    wrong_area: int = 0
    leaked: int = 0
    no_area_line: int = 0
    failed: int = 0
    by_verdict: dict = field(default_factory=dict)

    def record(self, verdict: str) -> None:
        setattr(self, verdict, getattr(self, verdict, 0) + 1)
        self.by_verdict[verdict] = self.by_verdict.get(verdict, 0) + 1


def _post(url: str, payload: dict, timeout: float) -> dict:
    response = httpx.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()


def reverse_generate(
    seed: Seed, variants: int, *, timeout: float = DEFAULT_TIMEOUT
) -> list[dict[str, str]]:
    """Ask the teacher what a person would have typed to get this label."""
    payload = {
        "model": "gvt-llm",
        "temperature": 0.9,
        "max_tokens": 100 * variants + 200,
        "messages": [
            {"role": "system", "content": REVERSE_SYSTEM},
            {"role": "user", "content": build_intermediate(seed)},
        ],
    }
    reply = _post(TEACHER_URL, payload, timeout)["choices"][0]["message"]["content"]
    return parse_utterances(reply)[:variants]


def ask_inner(utterance: str, *, timeout: float = DEFAULT_TIMEOUT) -> str:
    """Read the utterance with TRIDENT's own inner layer and its real prompt."""
    reply = (
        "Ability: overpass-api\n"
        "Reply: I copy. I'm generating maps based on OpenStreetMap data. "
        "Please wait a while..."
    )
    payload = {"pastMessages": [utterance, reply]}
    return _post(f"{TRIDENT_URL}/api/ai/inner", payload, timeout).get("inner", "")


def ask_deep(area_with_concern: str, *, timeout: float = DEFAULT_TIMEOUT) -> str:
    payload = {"query": area_with_concern}
    return _post(f"{TRIDENT_URL}/api/ai/deep", payload, timeout).get("deep", "")


def count_elements(query: str, *, timeout: float = DEFAULT_TIMEOUT) -> int:
    response = httpx.post(OVERPASS_URL, content=query.encode(), timeout=timeout)
    response.raise_for_status()
    return len(response.json().get("elements", []))


def evaluate(seed: Seed, item: dict[str, str], *, timeout: float = DEFAULT_TIMEOUT) -> PairResult:
    """Take one reconstructed utterance as far as it will go."""
    result = PairResult(
        seed_area=seed.area,
        seed_concern=seed.concern,
        lang=item.get("lang", "unknown"),
        utterance=item["utterance"],
    )

    if looks_like_leak(result.utterance):
        result.verdict = "leaked"
        result.note = "utterance repeats the internal format"
        return result

    try:
        result.inner_output = ask_inner(result.utterance, timeout=timeout)
        result.area_with_concern = area_with_concern_line(result.inner_output)
        if not result.area_with_concern:
            result.verdict = "no_area_line"
            return result

        # A wrong place still finds cafes, so this is the guard that matters.
        # Compared by relation rather than by string: "Sapporo" and
        # "Sapporo, Hokkaido" are the same place and the shorter one is what
        # a person actually says.
        written_area = area_part(result.area_with_concern, seed)
        if not same_place(written_area, seed.area, resolve_area):
            result.verdict = "wrong_area"
            result.note = f"read as {written_area!r}"
            return result

        result.overpass_query = ask_deep(result.area_with_concern, timeout=timeout)
        if not result.overpass_query.strip():
            result.verdict = "failed"
            result.note = "deep returned nothing"
            return result

        result.element_count = count_elements(result.overpass_query, timeout=timeout)
        if result.element_count > 0:
            result.verdict = "accepted"
            return result

        # Nothing came back. That is only the utterance's fault if the seed
        # concern would have found something here. When the seed works and the
        # drifted concern does not, the inner reading was fine and the deep
        # layer could not express it: keep the pair and record the gap.
        seed_line = f"AreaWithConcern: {seed.area}, {seed.concern}"
        control = ask_deep(seed_line, timeout=timeout)
        control_count = (
            count_elements(control, timeout=timeout) if control.strip() else 0
        )
        if control_count > 0:
            result.verdict = "deep_gap"
            result.note = f"seed concern finds {control_count}"
        else:
            result.verdict = "zero_results"
            result.note = "seed concern finds nothing here either"
    except Exception as error:  # a hang or a 500 is a result, not a crash
        result.verdict = "failed"
        result.note = f"{type(error).__name__}: {error}"
    return result


DEFAULT_SEEDS = [
    Seed("Taito, Tokyo", "Cafes"),
    Seed("Shinjuku, Tokyo", "Cafes"),
    Seed("Sapporo, Hokkaido", "Cafes"),
]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--limit", type=int, default=len(DEFAULT_SEEDS))
    parser.add_argument("--variants", type=int, default=6)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--out-dir", default="tmp")
    args = parser.parse_args()

    seeds = DEFAULT_SEEDS[: args.limit]
    counts = Counts()
    results: list[PairResult] = []

    for seed in seeds:
        print(f"\n### {seed.area} / {seed.concern}")
        try:
            items = reverse_generate(seed, args.variants, timeout=args.timeout)
        except Exception as error:
            print(f"  reverse generation failed: {error}")
            continue
        for item in items:
            result = evaluate(seed, item, timeout=args.timeout)
            counts.record(result.verdict)
            results.append(result)
            print(
                f"  {result.verdict:<13} {result.element_count:>6}  "
                f"{result.utterance[:38]:<40} -> {result.area_with_concern[17:47]}"
            )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    out_path = out_dir / f"inner-pairs-{stamp}.jsonl"
    with out_path.open("w") as handle:
        for result in results:
            handle.write(json.dumps(result.as_dict(), ensure_ascii=False) + "\n")

    total = len(results)
    print(f"\n{'verdict':<15}{'n':>5}  share")
    for verdict, n in sorted(counts.by_verdict.items(), key=lambda kv: -kv[1]):
        print(f"{verdict:<15}{n:>5}  {n / total:.0%}" if total else verdict)
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
