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
    """One request, expressed as the area and concern the model must recover."""

    area: str
    concern: str

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


def build_past_messages(case: InnerCase) -> list[str]:
    """The conversation the inner layer sees: the human turn, then surface's reply.

    Surface is not under test here, so its reply is fixed rather than generated.
    That keeps a surface failure from being scored against inner.
    """
    concern = case.concern.lower()
    query = f"Show me {concern} in {case.area}"
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


def _concern_matches(written: str, expected: str) -> bool:
    """Plural and singular both count; "Pharmacies" may come back as "Pharmacy"."""
    stem = expected.lower()
    if stem.endswith("ies"):
        stem = stem[:-3]  # pharmacies -> pharmac, matching pharmacy too
    elif stem.endswith("s"):
        stem = stem[:-1]
    return stem in written.lower()


def score_inner_output(text: str, case: InnerCase, *, error: str | None = None) -> InnerScore:
    """Score one reply. Never raises.

    Pass `error` when the request itself failed. A llama-server that ran out of
    VRAM returns nothing, and grading that as a wrong answer reports an
    infrastructure failure as a model result.
    """
    text = text or ""
    line = _area_with_concern_line(text)
    body = re.sub(r"^AreaWithConcern\s*:?\s*", "", line).strip()

    expected_area = [part.strip().lower() for part in case.area.split(",")]
    written = [part.strip().lower() for part in body.split(",")]

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


def ask_inner(trident_url: str, case: InnerCase, *, timeout: float = DEFAULT_TIMEOUT) -> str:
    """POST one case to TRIDENT's inner endpoint and return the raw reply."""
    response = httpx.post(
        f"{trident_url.rstrip('/')}/api/ai/inner",
        json={"pastMessages": build_past_messages(case)},
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


def run(
    label: str,
    trident_url: str,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    backend: str = "unspecified",
) -> dict:
    scores: list[InnerScore] = []
    for index, case in enumerate(INNER_CASES):
        error: str | None = None
        text = ""
        try:
            text = ask_inner(trident_url, case, timeout=timeout)
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
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
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

    print(f"Benchmarking inner layer: {args.label} via {args.trident_url}")
    report = run(args.label, args.trident_url, timeout=args.timeout, backend=args.backend)

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
