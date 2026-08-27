"""Tests for benchmark_inner.py — case set, scoring, and reporting."""

from benchmark_inner import (
    describe_commit,
    with_elements,
    UNSEEN_CASES,
    FIELD_CASES,
    _has_japanese,
    cases_for,
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
        messages = build_past_messages(TAITO_CAFES, style="with-reply")
        assert len(messages) == 2
        assert messages[0] == "Show me cafes in Taito, Tokyo"
        assert messages[1].startswith("Ability: overpass-api")

    def test_mentions_the_concern_and_area_in_the_surface_reply(self) -> None:
        reply = build_past_messages(TAITO_CAFES, style="with-reply")[1]
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


class TestFieldCases:
    def test_the_original_set_is_untouched(self) -> None:
        # Every number in the findings so far was measured on these ten.
        # Replacing them would make the before and after incomparable.
        assert len(INNER_CASES) == 10
        assert INNER_CASES[0] == InnerCase("Taito, Tokyo", "Cafes")

    def test_the_field_set_carries_its_own_words(self) -> None:
        # The template set asks "Show me {concern} in {area}" and nothing else.
        # These are sentences somebody actually typed or said.
        assert all(case.utterance for case in FIELD_CASES)

    def test_every_case_records_where_it_came_from(self) -> None:
        for case in FIELD_CASES:
            assert case.source in ("recorded", "constructed")

    def test_it_contains_japanese(self) -> None:
        # The point of fine-tuning the inner layer. An English-only set
        # cannot measure it.
        assert any(_has_japanese(c.utterance or "") for c in FIELD_CASES)

    def test_it_contains_a_four_level_area(self) -> None:
        # Already the cause of two separate failures.
        assert any(len(c.area.split(",")) >= 4 for c in FIELD_CASES)

    def test_it_contains_a_concern_that_finds_nothing(self) -> None:
        assert any(c.expect_empty for c in FIELD_CASES)

    def test_it_contains_the_forms_the_geocoder_trips_on(self) -> None:
        joined = " ".join(c.utterance or "" for c in FIELD_CASES)
        assert "-ku" in joined or "区" in joined


class TestBuildPastMessagesWithUtterance:
    def test_uses_the_recorded_words_when_there_are_any(self) -> None:
        case = InnerCase("Taito, Tokyo", "Soba noodle shops",
                         utterance="台東区の蕎麦屋を表示して", source="recorded")
        assert build_past_messages(case)[0] == "台東区の蕎麦屋を表示して"

    def test_falls_back_to_the_template(self) -> None:
        assert build_past_messages(InnerCase("Taito, Tokyo", "Cafes"))[0] == (
            "Show me cafes in Taito, Tokyo"
        )


class TestCasesFor:
    def test_template_is_the_default_and_is_the_frozen_ten(self) -> None:
        assert cases_for("template") == INNER_CASES

    def test_field_is_the_new_set(self) -> None:
        assert cases_for("field") == FIELD_CASES

    def test_both_keeps_the_frozen_ten_first(self) -> None:
        combined = cases_for("both")
        assert combined[: len(INNER_CASES)] == INNER_CASES
        assert len(combined) == len(INNER_CASES) + len(FIELD_CASES)


class TestTheYardstickItself:
    """Two ways the scorer was wrong about the system it measures.

    Both were found by measuring: the demo query resolved to the right area
    and the right element count while the scorer called it a failure.
    """

    def test_an_accented_concern_still_counts(self) -> None:
        # Qwen3-0.6B writes "Cafés". Fed to the deep layer that produces
        # amenity=cafe and the correct area ids, so the accent changes
        # nothing downstream and must not be scored as a wrong answer.
        case = InnerCase(area="Taito, Tokyo", concern="Cafes")
        text = "AreaWithConcern: Taito, Tokyo, Cafés"
        assert score_inner_output(text, case).concern_ok

    def test_an_accented_area_still_counts(self) -> None:
        case = InnerCase(area="Kyoto, Kyoto", concern="Restaurants")
        text = "AreaWithConcern: Kyōto, Kyoto, Restaurants"
        assert score_inner_output(text, case).area_ok

    def test_a_wrong_concern_is_still_wrong(self) -> None:
        # The relaxation must not swallow a substituted concern.
        case = InnerCase(area="Taito, Tokyo", concern="Cafes")
        assert not score_inner_output(
            "AreaWithConcern: Taito, Tokyo, Ramen shops", case
        ).concern_ok

    def test_the_demo_query_expects_the_city_not_the_prefecture(self) -> None:
        # "Show me cafes in Hiroshima City." The suffix is what lets the
        # geocoding ladder pick admin_level 7 (area 3604097196, 123 cafes).
        # Expecting the bare name scored dropping the suffix as correct.
        demo = [c for c in FIELD_CASES if c.utterance == "Show me cafes in Hiroshima City."]
        assert len(demo) == 1
        assert demo[0].area == "Hiroshima City"

    def test_the_japanese_city_form_expects_the_city_too(self) -> None:
        demo = [c for c in FIELD_CASES if c.utterance == "広島市のカフェを表示して"]
        assert len(demo) == 1
        assert demo[0].area == "広島市"


class TestTheFormatProductionActuallySends:
    """The browser sends one element, not two.

    /api/ai/surface returns `history` as the prior turns plus the query. It
    never appends its own reply, so the first turn reaches the inner layer as
    a single human utterance. Measuring with a fixed surface reply appended
    was measuring a prompt the system never builds.
    """

    def test_production_sends_the_utterance_alone(self) -> None:
        case = InnerCase("Taito, Tokyo", "Cafes")
        assert build_past_messages(case, style="production") == [
            "Show me cafes in Taito, Tokyo"
        ]

    def test_production_keeps_the_recorded_words(self) -> None:
        case = InnerCase("Taito, Tokyo", "Cafes", "台東区を表示して", "recorded")
        assert build_past_messages(case, style="production") == ["台東区を表示して"]

    def test_with_reply_is_still_available_for_the_older_numbers(self) -> None:
        case = InnerCase("Taito, Tokyo", "Cafes")
        assert len(build_past_messages(case, style="with-reply")) == 2

    def test_production_is_the_default(self) -> None:
        case = InnerCase("Taito, Tokyo", "Cafes")
        assert build_past_messages(case) == build_past_messages(case, style="production")


class TestTheUnseenSet:
    """Places that appear nowhere in the training data.

    The frozen sets cannot measure generalization any more: three of their
    four-level cases name areas the pairs were generated from, and one field
    case's utterance is in the training file verbatim. A fine-tune that
    learned the shape of a hierarchy without learning any geography scores
    well on those and badly here, which is the distinction worth measuring.

    Checked against data/inner at the time of writing: none of Matsuyama,
    Kumamoto, Nagasaki, Aomori, Toyama, Okayama, Gifu, Nara, Akita or
    Hiroshima occurs in a seed area or an utterance.
    """

    def test_it_has_ten_cases(self) -> None:
        assert len(UNSEEN_CASES) == 10

    def test_every_case_is_unique(self) -> None:
        assert len({c.slug for c in UNSEEN_CASES}) == len(UNSEEN_CASES)

    def test_it_mixes_japanese_and_english(self) -> None:
        japanese = [c for c in UNSEEN_CASES if any(ord(ch) > 0x3000 for ch in c.utterance or "")]
        assert 3 <= len(japanese) <= 7

    def test_every_case_names_a_city(self) -> None:
        # The demo's shape: a municipality, which is where the parent gets
        # invented. A prefecture-level case would not exercise it.
        for case in UNSEEN_CASES:
            assert case.area

    def test_none_of_its_areas_are_in_the_frozen_sets(self) -> None:
        frozen = {c.area for c in INNER_CASES + FIELD_CASES}
        assert not ({c.area for c in UNSEEN_CASES} & frozen)

    def test_cases_for_can_select_it(self) -> None:
        assert cases_for("unseen") == UNSEEN_CASES

    def test_it_is_not_folded_into_both(self) -> None:
        # "both" is the frozen pair; the unseen set is reported separately so
        # a number measured on it is never mistaken for one of those.
        assert cases_for("both") == INNER_CASES + FIELD_CASES


class TestReturningRealResults:
    """The column that catches an invented parent.

    "Hiroshima City, Tokyo, Japan" is a perfectly formed four-level area and
    passes the prefix rule, because the prefix is right. Intersected, it
    returns nothing. Scoring cannot see that without running the query, which
    is the third of the three checks the work promises: resolving place
    names, checking tag validity, and confirming that queries return real
    results.

    The prefix rule is left alone. This is a separate column, so every figure
    measured before it stays comparable.
    """

    def test_a_score_starts_with_the_query_unrun(self) -> None:
        s = score_inner_output("AreaWithConcern: Taito, Tokyo, Cafes", TAITO_CAFES)
        assert s.elements is None

    def test_elements_found_marks_the_answer_real(self) -> None:
        s = score_inner_output("AreaWithConcern: Taito, Tokyo, Cafes", TAITO_CAFES)
        assert with_elements(s, 368).returns_results

    def test_no_elements_marks_it_empty(self) -> None:
        s = score_inner_output("AreaWithConcern: Taito, Tokyo, Cafes", TAITO_CAFES)
        assert not with_elements(s, 0).returns_results

    def test_an_unrun_query_is_not_counted_either_way(self) -> None:
        s = score_inner_output("AreaWithConcern: Taito, Tokyo, Cafes", TAITO_CAFES)
        assert not s.returns_results

    def test_the_prefix_rule_is_untouched_by_the_new_column(self) -> None:
        # An invented parent still passes area_ok; that is the point of
        # measuring the query separately rather than tightening the rule.
        case = InnerCase("Hiroshima City", "Cafes")
        s = score_inner_output(
            "AreaWithConcern: Hiroshima City, Tokyo, Japan, Cafes", case
        )
        assert s.area_ok
        assert not with_elements(s, 0).returns_results

    def test_the_summary_counts_the_column(self) -> None:
        good = with_elements(
            score_inner_output("AreaWithConcern: Taito, Tokyo, Cafes", TAITO_CAFES), 368
        )
        empty = with_elements(
            score_inner_output("AreaWithConcern: Taito, Tokyo, Cafes", TAITO_CAFES), 0
        )
        assert summarize([good, empty])["returns_results"] == 1


class TestRecordingWhatWasMeasured:
    """Every report says which TRIDENT it was measured against.

    The prompt lives in TRIDENT, not here, and TRIDENT's working tree is
    shared with other agents. A commit that changed the few-shot examples
    landed between two of these runs and moved the numbers; nothing in either
    report said so, and the difference read as model variance for an hour.
    """

    def test_it_reports_the_commit_of_a_repository(self, tmp_path) -> None:
        import subprocess

        subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
        (tmp_path / "f.txt").write_text("x")
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
        subprocess.run(
            ["git", "-c", "user.email=t@t", "-c", "user.name=t",
             "commit", "-qm", "one"],
            cwd=tmp_path, check=True,
        )
        head = describe_commit(tmp_path)
        assert head and len(head) >= 7

    def test_a_path_that_is_not_a_repository_reports_nothing(self, tmp_path) -> None:
        assert describe_commit(tmp_path / "nowhere") is None

    def test_it_never_raises(self) -> None:
        assert describe_commit("/definitely/not/here") is None
