"""Tests for benchmark_inner.py — case set, scoring, and reporting."""

from benchmark_inner import (
    INNER_CASES,
    InnerCase,
    build_past_messages,
    render_markdown_table,
    score_inner_output,
    summarize,
)

TAITO_CAFES = InnerCase(area="Taito, Tokyo", concern="Cafes")

PERFECT = """ConfirmHelpful: Mapping has been completed.
TitleOfMap: Cafes in Taito, Tokyo
Area: Taito, Tokyo
AreaWithConcern: Taito, Tokyo, Cafes
EmojiForConcern: Cafes, coffee
ColorForConcern: Cafes, brown"""


class TestCaseSet:
    def test_has_ten_cases(self) -> None:
        assert len(INNER_CASES) == 10

    def test_every_case_is_unique(self) -> None:
        keys = [(c.area, c.concern) for c in INNER_CASES]
        assert len(set(keys)) == len(keys)

    def test_areas_mix_one_and_two_level_hierarchies(self) -> None:
        # "Fukuoka, Fukuoka" and "Kyoto, Kyoto" repeat the name at both levels,
        # which is where small models drop a level.
        repeated = [c for c in INNER_CASES if len(set(c.area.split(", "))) == 1]
        assert repeated, "keep at least one same-name hierarchy in the set"


class TestBuildPastMessages:
    def test_produces_the_user_turn_and_the_surface_reply(self) -> None:
        messages = build_past_messages(TAITO_CAFES)
        assert len(messages) == 2
        assert messages[0] == "Show me cafes in Taito, Tokyo"
        assert messages[1].startswith("Ability: overpass-api")

    def test_mentions_the_concern_and_area_in_the_surface_reply(self) -> None:
        reply = build_past_messages(TAITO_CAFES)[1]
        assert "cafes" in reply
        assert "Taito, Tokyo" in reply


class TestScoring:
    def test_accepts_a_perfect_answer(self) -> None:
        s = score_inner_output(PERFECT, TAITO_CAFES)
        assert s.keys_present and s.area_ok and s.concern_ok
        assert not s.runaway
        assert s.good

    def test_a_missing_colon_fails_keys_but_keeps_content(self) -> None:
        # Qwen3-0.6B drops it. The content is still right, which is the
        # distinction that decides whether fine-tuning can fix a model.
        text = PERFECT.replace("AreaWithConcern:", "AreaWithConcern").replace(
            "EmojiForConcern:", "EmojiForConcern"
        )
        s = score_inner_output(text, TAITO_CAFES)
        assert not s.keys_present
        assert s.area_ok and s.concern_ok
        assert not s.good

    def test_a_substituted_concern_fails_concern(self) -> None:
        # Qwen3.5-0.8B answered "Cafes" with "Ramen shops", copied from the
        # few-shot examples. No parser or fine-tune recovers from that.
        text = PERFECT.replace("Taito, Tokyo, Cafes", "Taito, Tokyo, Ramen shops")
        s = score_inner_output(text, TAITO_CAFES)
        assert not s.concern_ok
        assert not s.good

    def test_a_dropped_hierarchy_level_fails_area(self) -> None:
        case = InnerCase(area="Fukuoka, Fukuoka", concern="Libraries")
        text = "AreaWithConcern: Fukuoka, Libraries"
        assert not score_inner_output(text, case).area_ok

    def test_a_reordered_area_fails_area(self) -> None:
        text = PERFECT.replace(
            "AreaWithConcern: Taito, Tokyo, Cafes", "AreaWithConcern: Cafes in Taito, Tokyo"
        )
        assert not score_inner_output(text, TAITO_CAFES).area_ok

    def test_a_repetition_loop_is_flagged(self) -> None:
        text = PERFECT + "\n" + ("EmojiForConcern: Doctors, x\n" * 200)
        s = score_inner_output(text, TAITO_CAFES)
        assert s.runaway
        assert not s.good

    def test_an_empty_answer_scores_zero_without_raising(self) -> None:
        s = score_inner_output("", TAITO_CAFES)
        assert not (s.keys_present or s.area_ok or s.concern_ok or s.good)

    def test_singular_and_plural_concerns_both_count(self) -> None:
        case = InnerCase(area="Kobe, Hyogo", concern="Pharmacies")
        text = "AreaWithConcern: Kobe, Hyogo, Pharmacy"
        assert score_inner_output(text, case).concern_ok

    def test_case_differences_do_not_fail_the_area(self) -> None:
        text = "AreaWithConcern: taito, TOKYO, Cafes"
        assert score_inner_output(text, TAITO_CAFES).area_ok


class TestRequestFailures:
    def test_an_errored_case_is_not_scored_as_a_bad_answer(self) -> None:
        # A 500 from TRIDENT, or a llama-server that ran out of VRAM, produces
        # an empty string. Counting that as "the model answered wrongly" turns
        # an infrastructure failure into a model result.
        s = score_inner_output("", TAITO_CAFES, error="503 Service Unavailable")
        assert s.errored
        assert not s.good

    def test_summary_separates_errors_from_wrong_answers(self) -> None:
        scores = [
            score_inner_output(PERFECT, TAITO_CAFES),
            score_inner_output("", TAITO_CAFES, error="timeout"),
        ]
        s = summarize(scores)
        assert s["errors"] == 1
        assert s["answered"] == 1
        assert s["good"] == 1

    def test_a_run_that_wholly_failed_is_marked_invalid(self) -> None:
        scores = [score_inner_output("", TAITO_CAFES, error="boom") for _ in range(3)]
        s = summarize(scores)
        assert s["errors"] == 3
        assert s["answered"] == 0
        assert not s["valid"]

    def test_a_run_with_answers_is_valid(self) -> None:
        assert summarize([score_inner_output(PERFECT, TAITO_CAFES)])["valid"]


class TestSummarize:
    def test_counts_each_dimension(self) -> None:
        scores = [
            score_inner_output(PERFECT, TAITO_CAFES),
            score_inner_output(PERFECT.replace("AreaWithConcern:", "AreaWithConcern"), TAITO_CAFES),
        ]
        s = summarize(scores)
        assert s["n"] == 2
        assert s["keys_present"] == 1
        assert s["area_ok"] == 2
        assert s["good"] == 1

    def test_handles_an_empty_run(self) -> None:
        assert summarize([])["n"] == 0


class TestRendering:
    def test_table_has_one_row_per_model(self) -> None:
        base = {"errors": 0, "answered": 10, "valid": True}
        reports = [
            {"label": "a", "backend": "gpu", "summary": {**base, "n": 10, "keys_present": 5,
             "style_present": 6, "area_ok": 8, "concern_ok": 10, "runaway": 0, "good": 4}},
            {"label": "b", "backend": "gpu", "summary": {**base, "n": 10, "keys_present": 10,
             "style_present": 10, "area_ok": 10, "concern_ok": 10, "runaway": 0, "good": 10}},
        ]
        table = render_markdown_table(reports)
        assert table.count("\n") == 3  # header, separator, two rows minus trailing
        assert "gpu" in table
        assert "| a |" in table and "| b |" in table
        assert "4/10" in table and "10/10" in table
