"""The step between the generator's record and a training set.

The generator writes what happened, with a verdict. This turns that into
pairs, and the two judgements it makes are the ones worth testing: which
verdicts are usable, and what the target should say.
"""

from __future__ import annotations

import pytest

from build_inner_trainset import (
    repaired_confirmation,
    Pair,
    area_levels,
    build_target,
    concern_is_faithful,
    reply_language,
    reply_language_matches,
    select,
    split,
    written_area,
)

ACCEPTED = {
    "seed_area": "Higashi Ward, Niigata, Niigata Prefecture, Japan",
    "seed_concern": "Airports",
    "lang": "ja",
    "utterance": "新潟市東区内の空港一覧を出して",
    "inner_output": (
        "```\n"
        "ConfirmHelpful: 地図の作成が完了しました。\n"
        "TitleOfMap: 新潟市東区内の空港\n"
        "Area: Higashi-ku, Niigata\n"
        "AreaWithConcern: Higashi-ku, Niigata, Airports\n"
        "EmojiForConcern: Airports, ✈️\n"
        "ColorForConcern: Airports, lightblue\n"
        "```"
    ),
    "area_with_concern": "AreaWithConcern: Higashi-ku, Niigata, Airports",
    "element_count": 1,
    "verdict": "accepted",
}


def row(**overrides):
    return {**ACCEPTED, **overrides}


class TestAreaLevels:
    def test_counts_comma_separated_parts(self) -> None:
        assert area_levels("Higashi Ward, Niigata, Niigata Prefecture, Japan") == 4

    def test_ignores_empty_parts(self) -> None:
        assert area_levels("Taito, Tokyo, ") == 2

    def test_an_empty_area_has_no_levels(self) -> None:
        assert area_levels("") == 0


class TestWrittenArea:
    def test_drops_the_concern_from_the_line(self) -> None:
        assert written_area(ACCEPTED) == "Higashi-ku, Niigata"

    def test_a_line_with_only_a_concern_leaves_nothing(self) -> None:
        assert written_area(row(area_with_concern="AreaWithConcern: Cafes")) == ""


class TestReplyLanguage:
    def test_kana_marks_japanese(self) -> None:
        assert reply_language("地図の作成が完了しました。") == "ja"

    def test_hangul_marks_korean(self) -> None:
        assert reply_language("매핑이 완료되었습니다.") == "ko"

    def test_han_without_kana_marks_chinese(self) -> None:
        # The 35B drifts here: 地图的制作已经完成了 has no kana.
        assert reply_language("地图的制作已经完成了。你还有其他要求吗？") == "zh"

    def test_plain_latin_marks_english(self) -> None:
        assert reply_language("Mapping has been completed.") == "en"

    def test_a_japanese_row_with_a_korean_reply_is_rejected(self) -> None:
        bad = row(inner_output=ACCEPTED["inner_output"].replace(
            "地図の作成が完了しました。", "매핑이 완료되었습니다."))
        assert not reply_language_matches(bad)

    def test_a_japanese_row_with_a_japanese_reply_is_kept(self) -> None:
        assert reply_language_matches(ACCEPTED)

    def test_an_english_row_with_an_english_reply_is_kept(self) -> None:
        english = row(
            lang="en",
            utterance="List airports in Higashi Ward.",
            inner_output=ACCEPTED["inner_output"].replace(
                "地図の作成が完了しました。", "Mapping has been completed."),
        )
        assert reply_language_matches(english)


class TestBuildTarget:
    """The target carries the seed's hierarchy, not the model's shortening.

    41% of accepted rows drop a level: the seed names four and the reply
    names two. Overpass still returns something, so the verdict is accepted,
    but training on the reply teaches the model to collapse hierarchies —
    the exact weakness the fine-tune is meant to remove.
    """

    def test_the_area_comes_from_the_validated_seed(self) -> None:
        target = build_target(ACCEPTED)
        assert "Area: Higashi Ward, Niigata, Niigata Prefecture, Japan" in target

    def test_the_concern_comes_from_the_validated_seed(self) -> None:
        target = build_target(ACCEPTED)
        assert (
            "AreaWithConcern: Higashi Ward, Niigata, Niigata Prefecture, Japan, Airports"
            in target
        )

    def test_the_decorative_lines_are_kept_from_the_model(self) -> None:
        target = build_target(ACCEPTED)
        assert "TitleOfMap: 新潟市東区内の空港" in target
        assert "EmojiForConcern: Airports, ✈️" in target
        assert "ColorForConcern: Airports, lightblue" in target

    def test_the_fences_are_stripped(self) -> None:
        assert "```" not in build_target(ACCEPTED)

    def test_the_six_keys_appear_once_each(self) -> None:
        target = build_target(ACCEPTED)
        for key in ("ConfirmHelpful", "TitleOfMap", "Area", "AreaWithConcern",
                    "EmojiForConcern", "ColorForConcern"):
            assert target.count(f"{key}:") == 1, key

    def test_the_order_is_the_intermediate_language_order(self) -> None:
        keys = [line.split(":")[0] for line in build_target(ACCEPTED).splitlines()]
        assert keys == ["ConfirmHelpful", "TitleOfMap", "Area", "AreaWithConcern",
                        "EmojiForConcern", "ColorForConcern"]


class TestConcernIsFaithful:
    def test_the_seed_concern_written_back_counts(self) -> None:
        assert concern_is_faithful(ACCEPTED)

    def test_a_substituted_concern_does_not(self) -> None:
        assert not concern_is_faithful(
            row(area_with_concern="AreaWithConcern: Higashi-ku, Niigata, Amusement parks")
        )

    def test_singular_counts(self) -> None:
        assert concern_is_faithful(
            row(seed_concern="Airports",
                area_with_concern="AreaWithConcern: Higashi-ku, Niigata, Airport")
        )


class TestSelect:
    def test_accepted_is_taken(self) -> None:
        chosen, _ = select([ACCEPTED])
        assert len(chosen) == 1

    def test_zero_results_is_taken(self) -> None:
        # Area and concern are both right; the emptiness is OSM's, not the
        # model's. Overpass returning nothing is not evidence of a misreading.
        chosen, _ = select([row(verdict="zero_results", element_count=0)])
        assert len(chosen) == 1

    def test_a_wrong_area_is_dropped(self) -> None:
        chosen, reasons = select([row(verdict="wrong_area")])
        assert not chosen
        assert reasons["wrong_area"] == 1

    def test_an_invented_name_is_dropped(self) -> None:
        chosen, _ = select([row(verdict="invented_name")])
        assert not chosen

    def test_a_deep_gap_with_a_faithful_concern_is_taken(self) -> None:
        chosen, _ = select([row(verdict="deep_gap")])
        assert len(chosen) == 1

    def test_a_deep_gap_with_a_substituted_concern_is_dropped(self) -> None:
        chosen, reasons = select([row(
            verdict="deep_gap",
            area_with_concern="AreaWithConcern: Higashi-ku, Niigata, Amusement parks",
        )])
        assert not chosen
        assert reasons["deep_gap_unfaithful"] == 1

    def test_a_drifting_reply_language_is_dropped(self) -> None:
        chosen, reasons = select([row(inner_output=ACCEPTED["inner_output"].replace(
            "地図の作成が完了しました。", "매핑이 완료되었습니다."))])
        assert not chosen
        assert reasons["reply_language"] == 1

    def test_the_same_utterance_is_kept_once(self) -> None:
        chosen, reasons = select([ACCEPTED, dict(ACCEPTED)])
        assert len(chosen) == 1
        assert reasons["duplicate"] == 1


class TestSplit:
    def test_every_pair_lands_in_exactly_one_side(self) -> None:
        pairs = [Pair(input=f"q{i}", output="o", lang="en", levels=2, verdict="accepted")
                 for i in range(100)]
        train, valid = split(pairs, valid_fraction=0.1)
        assert len(train) + len(valid) == 100
        assert not ({p.input for p in train} & {p.input for p in valid})

    def test_the_split_is_the_same_every_run(self) -> None:
        pairs = [Pair(input=f"q{i}", output="o", lang="en", levels=2, verdict="accepted")
                 for i in range(100)]
        assert split(pairs, valid_fraction=0.1) == split(pairs, valid_fraction=0.1)

    def test_an_empty_set_splits_into_nothing(self) -> None:
        assert split([], valid_fraction=0.1) == ([], [])


class TestRepairingTheConfirmation:
    """The drifting reply is decorative, so it is replaced rather than dropped.

    The golden model answers Japanese input in Korean, Chinese or English in
    1188 rows. Area and concern come from the seed regardless, so the only
    thing wrong with those rows is one line. Substituting a confirmation in
    the right language keeps the pair and teaches the matching outright.
    """

    def test_a_drifting_reply_is_replaced_not_dropped(self) -> None:
        drifted = row(inner_output=ACCEPTED["inner_output"].replace(
            "地図の作成が完了しました。", "매핑이 완료되었습니다."))
        chosen, _ = select([drifted], repair_confirmation=True)
        assert len(chosen) == 1
        assert reply_language(chosen[0].output.splitlines()[0]) == "ja"

    def test_the_rest_of_the_block_survives_the_repair(self) -> None:
        drifted = row(inner_output=ACCEPTED["inner_output"].replace(
            "地図の作成が完了しました。", "매핑이 완료되었습니다."))
        chosen, _ = select([drifted], repair_confirmation=True)
        assert "TitleOfMap: 新潟市東区内の空港" in chosen[0].output
        assert "Airports" in chosen[0].output

    def test_a_matching_reply_is_left_alone(self) -> None:
        chosen, _ = select([ACCEPTED], repair_confirmation=True)
        assert "地図の作成が完了しました。" in chosen[0].output

    def test_repair_does_not_rescue_a_wrong_area(self) -> None:
        chosen, _ = select([row(verdict="wrong_area")], repair_confirmation=True)
        assert not chosen

    def test_dropping_is_still_available(self) -> None:
        drifted = row(inner_output=ACCEPTED["inner_output"].replace(
            "地図の作成が完了しました。", "매핑이 완료되었습니다."))
        chosen, reasons = select([drifted], repair_confirmation=False)
        assert not chosen
        assert reasons["reply_language"] == 1


class TestTheStyleLinesCarryTheSameLabel:
    """TRIDENT keys the colour and the emoji by the concern's name.

    "AreaWithConcern: ..., Airports" with "EmojiForConcern: Airport, ✈️" does
    not match, and the style is silently dropped at render time. The golden
    model varies the label in 26.7% of rows — singular for plural, lower case
    for title case — so the training data was reproducing the bug it was
    meant to help remove. The glyph and the colour name come from the model;
    the label comes from the seed, exactly as the area does.
    """

    def test_the_emoji_label_matches_the_concern(self) -> None:
        target = build_target(row(inner_output=ACCEPTED["inner_output"].replace(
            "EmojiForConcern: Airports, ✈️", "EmojiForConcern: Airport, ✈️")))
        assert "EmojiForConcern: Airports, ✈️" in target

    def test_the_colour_label_matches_the_concern(self) -> None:
        target = build_target(row(inner_output=ACCEPTED["inner_output"].replace(
            "ColorForConcern: Airports, lightblue",
            "ColorForConcern: airport, lightblue")))
        assert "ColorForConcern: Airports, lightblue" in target

    def test_the_glyph_still_comes_from_the_model(self) -> None:
        target = build_target(row(inner_output=ACCEPTED["inner_output"].replace(
            "EmojiForConcern: Airports, ✈️", "EmojiForConcern: Airport, 🛬")))
        assert "EmojiForConcern: Airports, 🛬" in target

    def test_the_colour_name_still_comes_from_the_model(self) -> None:
        target = build_target(row(inner_output=ACCEPTED["inner_output"].replace(
            "ColorForConcern: Airports, lightblue", "ColorForConcern: Airports, teal")))
        assert "ColorForConcern: Airports, teal" in target

    def test_a_style_line_with_no_comma_is_left_as_the_seed_label(self) -> None:
        target = build_target(row(inner_output=ACCEPTED["inner_output"].replace(
            "EmojiForConcern: Airports, ✈️", "EmojiForConcern: ✈️")))
        assert "EmojiForConcern: Airports, ✈️" in target
