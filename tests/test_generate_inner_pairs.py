"""Tests for generate_inner_pairs.py — the pure parts of the reverse pipeline."""

from generate_inner_pairs import (
    Seed,
    area_part,
    same_place,
    area_matches,
    area_with_concern_line,
    build_intermediate,
    looks_like_leak,
    parse_utterances,
)

TAITO = Seed("Taito, Tokyo", "Cafes")


class TestBuildIntermediate:
    def test_carries_every_line_the_inner_layer_emits(self) -> None:
        block = build_intermediate(TAITO)
        for key in ("TitleOfMap:", "Area:", "AreaWithConcern:",
                    "EmojiForConcern:", "ColorForConcern:"):
            assert key in block

    def test_area_and_concern_land_in_the_right_line(self) -> None:
        assert "AreaWithConcern: Taito, Tokyo, Cafes" in build_intermediate(TAITO)

    def test_an_unlisted_concern_still_gets_a_style(self) -> None:
        block = build_intermediate(Seed("Taito, Tokyo", "Falconries"))
        assert "EmojiForConcern: Falconries," in block
        assert "ColorForConcern: Falconries," in block


class TestParseUtterances:
    def test_reads_a_plain_array(self) -> None:
        reply = '[{"lang":"ja","utterance":"台東区のカフェ"},{"lang":"en","utterance":"cafes"}]'
        assert parse_utterances(reply) == [
            {"lang": "ja", "utterance": "台東区のカフェ"},
            {"lang": "en", "utterance": "cafes"},
        ]

    def test_digs_the_array_out_of_surrounding_prose(self) -> None:
        reply = 'Sure!\n```json\n[{"lang":"ja","utterance":"台東区のカフェ"}]\n```\n'
        assert parse_utterances(reply)[0]["utterance"] == "台東区のカフェ"

    def test_marks_an_unexpected_language_rather_than_dropping_it(self) -> None:
        assert parse_utterances('[{"lang":"fr","utterance":"cafés"}]')[0]["lang"] == "unknown"

    def test_skips_entries_with_no_utterance(self) -> None:
        assert parse_utterances('[{"lang":"ja"},{"lang":"ja","utterance":" "}]') == []

    def test_returns_nothing_for_junk(self) -> None:
        for reply in ["", "no json here", "[not json]"]:
            assert parse_utterances(reply) == []


class TestLooksLikeLeak:
    def test_catches_the_internal_vocabulary(self) -> None:
        assert looks_like_leak("AreaWithConcern: Taito, Tokyo, Cafes")
        assert looks_like_leak("show me the titleofmap for Taito")

    def test_leaves_an_ordinary_request_alone(self) -> None:
        assert not looks_like_leak("台東区の喫茶店一覧")
        assert not looks_like_leak("Where can I get coffee in Taito?")


class TestAreaMatches:
    def test_accepts_the_seed_area(self) -> None:
        assert area_matches("AreaWithConcern: Taito, Tokyo, Cafes", TAITO)

    def test_accepts_a_drifted_concern(self) -> None:
        # "Cafes" comes back as "Coffee shops" more often than not, and that
        # is allowed: the Overpass check decides whether it is useful.
        assert area_matches("AreaWithConcern: Taito, Tokyo, Coffee shops", TAITO)

    def test_rejects_a_different_place(self) -> None:
        # Osaka has cafes too, so only the area check catches this.
        assert not area_matches("AreaWithConcern: Osaka, Cafes", TAITO)

    def test_rejects_a_dropped_level(self) -> None:
        assert not area_matches("AreaWithConcern: Taito, Cafes", TAITO)

    def test_tolerates_a_missing_colon_and_odd_spacing(self) -> None:
        assert area_matches("AreaWithConcern  Taito ,  Tokyo , Cafes", TAITO)

    def test_ignores_letter_case(self) -> None:
        assert area_matches("AreaWithConcern: taito, TOKYO, Cafes", TAITO)

    def test_rejects_an_empty_line(self) -> None:
        assert not area_matches("", TAITO)


class TestAreaWithConcernLine:
    def test_finds_the_line_among_the_others(self) -> None:
        block = "TitleOfMap: x\nArea: Taito, Tokyo\nAreaWithConcern: Taito, Tokyo, Cafes"
        assert area_with_concern_line(block) == "AreaWithConcern: Taito, Tokyo, Cafes"

    def test_does_not_mistake_the_bare_area_line_for_it(self) -> None:
        assert area_with_concern_line("Area: Taito, Tokyo") == ""

    def test_returns_empty_when_there_is_none(self) -> None:
        assert area_with_concern_line("No map specified.") == ""


class TestParseUtterancesSalvage:
    def test_salvages_the_objects_from_a_truncated_array(self) -> None:
        # max_tokens cut the reply mid-array. json.loads fails on the whole
        # thing, and dropping it lost every utterance in the batch.
        reply = (
            '[\n  {"lang": "ja", "utterance": "新宿のカフェを教えて"},\n'
            '  {"lang": "en", "utterance": "Show me coffee shops"},\n'
            '  {"lang": "ja", "utterance": "新宿の喫'
        )
        got = parse_utterances(reply)
        assert [item["utterance"] for item in got] == [
            "新宿のカフェを教えて",
            "Show me coffee shops",
        ]

    def test_a_complete_array_still_takes_the_fast_path(self) -> None:
        reply = '[{"lang":"en","utterance":"cafes in Taito"}]'
        assert len(parse_utterances(reply)) == 1


class TestAreaIdentity:
    def test_a_shorter_but_compatible_area_is_the_same_place(self) -> None:
        # "札幌のカフェを教えて" cannot be expected to say Hokkaido. The seed
        # is the redundant one; the model is being faithful to the utterance.
        resolver = {"Sapporo": 123, "Sapporo, Hokkaido": 123}.get
        assert same_place("Sapporo", "Sapporo, Hokkaido", resolver)

    def test_a_different_place_is_not(self) -> None:
        resolver = {"Osaka": 999, "Taito, Tokyo": 111}.get
        assert not same_place("Osaka", "Taito, Tokyo", resolver)

    def test_identical_strings_need_no_geocoder(self) -> None:
        calls: list[str] = []

        def resolver(name: str) -> int | None:
            calls.append(name)
            return 1

        assert same_place("Taito, Tokyo", "Taito, Tokyo", resolver)
        assert calls == []

    def test_an_unresolvable_name_is_rejected_rather_than_assumed(self) -> None:
        resolver = {"Taito, Tokyo": 111}.get
        assert not same_place("Nowhereville", "Taito, Tokyo", resolver)


class TestAreaPart:
    def test_takes_as_many_parts_as_the_seed_has(self) -> None:
        seed = Seed("Taito, Tokyo", "Cafes")
        assert area_part("AreaWithConcern: Taito, Tokyo, Cafes", seed) == "Taito, Tokyo"

    def test_never_swallows_the_concern_when_the_model_writes_fewer_areas(self) -> None:
        # "札幌のカフェを教えて" gives "Sapporo, Cafe" against a two-part seed.
        seed = Seed("Sapporo, Hokkaido", "Cafes")
        assert area_part("AreaWithConcern: Sapporo, Cafe", seed) == "Sapporo"

    def test_handles_a_single_part_seed(self) -> None:
        seed = Seed("Japan", "Castles")
        assert area_part("AreaWithConcern: Japan, Castles", seed) == "Japan"

    def test_returns_empty_for_an_empty_line(self) -> None:
        assert area_part("", Seed("Taito, Tokyo", "Cafes")) == ""
