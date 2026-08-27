"""Tests for generate_inner_pairs.py — the pure parts of the reverse pipeline."""

from generate_inner_pairs import (
    Seed,
    area_part,
    dedupe,
    is_suspicious,
    same_place,
    strip_area_suffix,
    utterance_names_place,
    area_matches,
    area_with_concern_line,
    build_intermediate,
    build_area_searches,
    build_seeds,
    completed_seeds,
    load_concerns,
    load_validated_seeds,
    name_forms,
    parse_trident_input,
    looks_like_leak,
    parse_utterances,
    remaining_seeds,
    reverse_system_prompt,
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

    def test_replaces_an_unexpected_language_label_with_a_guess(self) -> None:
        # The label is only a hint; the script is the evidence.
        assert parse_utterances('[{"lang":"fr","utterance":"cafés"}]')[0]["lang"] == "en"
        assert parse_utterances('[{"lang":"fr","utterance":"カフェ"}]')[0]["lang"] == "ja"

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


class TestSuspiciousRatio:
    def test_a_comparable_count_is_not_suspicious(self) -> None:
        assert not is_suspicious(368, 368)
        assert not is_suspicious(343, 368)

    def test_a_count_far_below_the_seed_is(self) -> None:
        # "Coffee shops" found 4 where "Cafes" found 343. Non-empty, but not
        # the map anyone asked for.
        assert is_suspicious(4, 343)
        assert is_suspicious(6, 282)

    def test_more_than_the_seed_is_fine(self) -> None:
        assert not is_suspicious(900, 368)

    def test_nothing_to_compare_against_is_not_suspicious(self) -> None:
        # Without a working control there is no ratio to judge.
        assert not is_suspicious(4, 0)

    def test_an_empty_result_is_judged_elsewhere(self) -> None:
        assert not is_suspicious(0, 368)


class TestDedupe:
    def test_drops_repeats_keeping_the_first(self) -> None:
        items = [
            {"lang": "ja", "utterance": "台東区のカフェ"},
            {"lang": "en", "utterance": "cafes in Taito"},
            {"lang": "ja", "utterance": "台東区のカフェ"},
        ]
        assert [i["utterance"] for i in dedupe(items)] == [
            "台東区のカフェ",
            "cafes in Taito",
        ]

    def test_ignores_case_and_surrounding_space(self) -> None:
        items = [
            {"lang": "en", "utterance": "Cafes in Taito"},
            {"lang": "en", "utterance": "  cafes in taito  "},
        ]
        assert len(dedupe(items)) == 1


class TestParseUtterancesShapes:
    def test_accepts_a_bare_array_of_strings(self) -> None:
        # The teacher ignores the object shape about as often as it obeys it.
        reply = '["Taitoのカフェを教えて", "Cafes in Taito, Tokyo"]'
        assert parse_utterances(reply) == [
            {"lang": "ja", "utterance": "Taitoのカフェを教えて"},
            {"lang": "en", "utterance": "Cafes in Taito, Tokyo"},
        ]

    def test_guesses_the_language_from_the_script(self) -> None:
        assert parse_utterances('["新宿のカフェ"]')[0]["lang"] == "ja"
        assert parse_utterances('["cafes in Shinjuku"]')[0]["lang"] == "en"

    def test_a_mixed_array_keeps_both_shapes(self) -> None:
        reply = '["台東区のカフェ", {"lang":"en","utterance":"cafes in Taito"}]'
        assert len(parse_utterances(reply)) == 2

    def test_skips_empty_strings(self) -> None:
        assert parse_utterances('["", "  "]') == []


class TestAreaSearchTerm:
    def test_strips_a_level_naming_suffix(self) -> None:
        # OSM writes 札幌市 as name:en "Sapporo", so "Sapporo City" resolves
        # to nothing and the pair was rejected as a wrong place.
        assert strip_area_suffix("Sapporo City") == "Sapporo"
        assert strip_area_suffix("Miyagi Prefecture") == "Miyagi"
        assert strip_area_suffix("Taito Ward") == "Taito"

    def test_handles_the_romanised_japanese_suffixes(self) -> None:
        assert strip_area_suffix("Hiroshima-shi") == "Hiroshima"
        assert strip_area_suffix("Miyagi-ken") == "Miyagi"

    def test_leaves_a_plain_name(self) -> None:
        assert strip_area_suffix("Sapporo") == "Sapporo"
        assert strip_area_suffix("Japan") == "Japan"

    def test_only_strips_the_last_part(self) -> None:
        assert strip_area_suffix("Sapporo City, Hokkaido") == "Sapporo, Hokkaido"


class TestReverseSystemPrompt:
    def test_states_the_count_twice(self) -> None:
        # Without a number the teacher returns two utterances, one per
        # language, however many were asked for.
        prompt = reverse_system_prompt(8)
        assert prompt.count("8") == 2

    def test_keeps_the_format_ban(self) -> None:
        assert "AreaWithConcern" in reverse_system_prompt(6)


class TestBuildSeeds:
    def test_pairs_concerns_with_areas_round_robin(self) -> None:
        seeds = build_seeds(["Cafes", "Parks", "Hotels"], ["A", "B"], 4)
        assert [(s.concern, s.area) for s in seeds] == [
            ("Cafes", "A"),
            ("Parks", "B"),
            ("Hotels", "A"),
            ("Cafes", "B"),
        ]

    def test_walks_every_concern_before_repeating_one(self) -> None:
        seeds = build_seeds(["Cafes", "Parks"], ["A"], 2)
        assert {s.concern for s in seeds} == {"Cafes", "Parks"}

    def test_stops_at_the_requested_count(self) -> None:
        assert len(build_seeds(["Cafes"], ["A", "B"], 5)) == 5

    def test_returns_nothing_without_material(self) -> None:
        assert build_seeds([], ["A"], 3) == []
        assert build_seeds(["Cafes"], [], 3) == []


class TestLoadConcerns:
    def test_reads_the_names_from_the_yaml(self, tmp_path) -> None:
        path = tmp_path / "c.yaml"
        path.write_text(
            "# comment\n"
            "Airports: data/concerns/aeroway/aerodrome\n"
            "Cafes: data/concerns/amenity/cafe\n"
        )
        assert load_concerns(path) == ["Airports", "Cafes"]

    def test_skips_comments_and_blank_lines(self, tmp_path) -> None:
        path = tmp_path / "c.yaml"
        path.write_text("\n# only a comment\n\n")
        assert load_concerns(path) == []


class TestParseTridentInput:
    def test_reads_the_semicolon_form_the_dataset_uses(self) -> None:
        seed = parse_trident_input("AreaWithConcern: Taito, Tokyo, Japan; Cafes")
        assert seed == Seed("Taito, Tokyo, Japan", "Cafes")

    def test_reads_a_single_level_area(self) -> None:
        assert parse_trident_input("AreaWithConcern: Japan; Castles") == Seed(
            "Japan", "Castles"
        )

    def test_reads_the_area_prefixed_form(self) -> None:
        # A handful of entries are written "Area: ...; <feature>".
        assert parse_trident_input("Area: Tokyo, Japan; Sumida River") == Seed(
            "Tokyo, Japan", "Sumida River"
        )

    def test_tolerates_extra_whitespace(self) -> None:
        assert parse_trident_input("  AreaWithConcern:  Japan ;  Castles \n") == Seed(
            "Japan", "Castles"
        )

    def test_rejects_anything_without_a_concern(self) -> None:
        for line in ["AreaWithConcern: Japan", "", "Cafes", "AreaWithConcern: ; Cafes"]:
            assert parse_trident_input(line) is None


class TestLoadValidatedSeeds:
    def _pair(self, root, tag, area, line, *, validated=True):
        d = root / "data" / "concerns" / tag / area
        d.mkdir(parents=True)
        (d / "input-trident.txt").write_text(line)
        if validated:
            (d / "output-001.overpassql").write_text("[out:json];")

    def test_takes_only_pairs_that_produced_a_query(self, tmp_path) -> None:
        # 18,231 directories hold an input; 4,599 produced a query. Only those
        # are known to work end to end.
        self._pair(tmp_path, "amenity/cafe", "Taito", "AreaWithConcern: Taito, Tokyo; Cafes")
        self._pair(tmp_path, "amenity/bar", "Nowhere", "AreaWithConcern: Nowhere; Bars",
                   validated=False)
        seeds = load_validated_seeds(tmp_path / "data" / "concerns")
        assert seeds == [Seed("Taito, Tokyo", "Cafes")]

    def test_skips_an_unreadable_line(self, tmp_path) -> None:
        self._pair(tmp_path, "amenity/x", "A", "nonsense")
        assert load_validated_seeds(tmp_path / "data" / "concerns") == []

    def test_returns_them_sorted_so_a_short_run_is_reproducible(self, tmp_path) -> None:
        self._pair(tmp_path, "a/b", "Z", "AreaWithConcern: Zed; Zoos")
        self._pair(tmp_path, "a/c", "A", "AreaWithConcern: Ay; Airports")
        seeds = load_validated_seeds(tmp_path / "data" / "concerns")
        assert [s.concern for s in seeds] == ["Airports", "Zoos"]


class TestAreaSearchLadder:
    def test_a_multi_level_name_tries_the_structured_search_first(self) -> None:
        # "Isogo, Yokohama" finds nothing as free text but resolves as
        # city=Isogo&state=Yokohama, which is what the seed resolves to.
        attempts = build_area_searches("Isogo, Yokohama")
        assert attempts[0] == {"city": "Isogo", "state": "Yokohama"}

    def test_carries_the_outermost_part_as_the_country(self) -> None:
        assert build_area_searches("Isogo, Yokohama, Japan")[0] == {
            "city": "Isogo",
            "state": "Yokohama",
            "country": "Japan",
        }

    def test_uses_the_level_a_suffix_declares(self) -> None:
        assert {"q": "Sapporo", "featureType": "settlement"} in build_area_searches(
            "Sapporo City"
        )

    def test_always_ends_with_the_plain_search(self) -> None:
        for name in ["Isogo, Yokohama", "Sapporo City", "Japan"]:
            assert "q" in build_area_searches(name)[-1]

    def test_a_single_plain_name_has_only_the_plain_search(self) -> None:
        assert build_area_searches("Japan") == [{"q": "Japan"}]


class TestReverseSystemPromptGrounding:
    def test_requires_the_place_to_be_named(self) -> None:
        prompt = reverse_system_prompt(8)
        assert "MUST name the place" in prompt

    def test_bans_the_phrasings_that_cannot_be_recovered(self) -> None:
        prompt = reverse_system_prompt(8)
        for phrase in ["nearby", "near me", "this area", "このあたり"]:
            assert phrase in prompt


class TestUtteranceNamesThePlace:
    NAMES = {"磯子区", "Isogo Ward", "Isogo"}

    def test_accepts_the_official_name(self) -> None:
        assert utterance_names_place("磯子区の喫茶店を教えて", self.NAMES)

    def test_accepts_the_english_name(self) -> None:
        assert utterance_names_place("Show me cafes in Isogo Ward", self.NAMES)
        assert utterance_names_place("cafes in isogo", self.NAMES)

    def test_rejects_a_typo(self) -> None:
        # 磯谷 is a real place in Hokkaido. Teaching 磯谷区 = Isogo, Yokohama
        # would put a false mapping into the data, not robustness to typos.
        assert not utterance_names_place("磯谷区の喫茶店を教えて", self.NAMES)

    def test_rejects_a_translation_the_map_does_not_use(self) -> None:
        assert not utterance_names_place("ソウル北エリアの宿", {"강북구", "Gangbuk-gu"})

    def test_accepts_a_longer_form_that_contains_the_name(self) -> None:
        assert utterance_names_place("新潟市中央区にある空港はどこですか", {"中央区", "Chuo Ward"})

    def test_without_known_names_it_cannot_judge_and_says_so(self) -> None:
        # No names means the geocoder failed, not that the utterance is good.
        assert not utterance_names_place("anything", set())


class TestJapaneseNameForms:
    def test_allows_the_municipal_suffix_to_be_dropped(self) -> None:
        # OSM records 小金井市; people write 小金井.
        assert "小金井" in name_forms("小金井市")
        assert "磯子" in name_forms("磯子区")

    def test_keeps_the_full_form_too(self) -> None:
        assert "小金井市" in name_forms("小金井市")

    def test_refuses_to_shorten_a_name_to_one_character(self) -> None:
        # 港区 would become 港, which appears in 空港, 港町 and most harbours.
        assert name_forms("港区") == {"港区"}

    def test_leaves_a_name_without_a_suffix_alone(self) -> None:
        assert name_forms("渋谷") == {"渋谷"}

    def test_handles_the_english_suffixes_as_before(self) -> None:
        assert "Isogo" in name_forms("Isogo Ward")

    def test_does_not_shorten_a_prefecture_to_something_ambiguous(self) -> None:
        # 京都府 -> 京都 is fine; it is the same place at a coarser level.
        assert "京都" in name_forms("京都府")


class TestCompletedSeeds:
    def test_reads_back_which_seeds_a_file_already_covers(self, tmp_path) -> None:
        path = tmp_path / "pairs.jsonl"
        path.write_text(
            '{"seed_area": "Taito, Tokyo", "seed_concern": "Cafes"}\n'
            '{"seed_area": "Taito, Tokyo", "seed_concern": "Cafes"}\n'
            '{"seed_area": "Naha, Okinawa", "seed_concern": "Hotels"}\n'
        )
        assert completed_seeds(path) == {
            ("Taito, Tokyo", "Cafes"),
            ("Naha, Okinawa", "Hotels"),
        }

    def test_a_missing_file_covers_nothing(self, tmp_path) -> None:
        assert completed_seeds(tmp_path / "nothing.jsonl") == set()

    def test_a_half_written_last_line_does_not_stop_the_rest(self, tmp_path) -> None:
        # A nine-hour run killed mid-write leaves a truncated line. Losing the
        # other 4,000 pairs over it would defeat the point of resuming.
        path = tmp_path / "pairs.jsonl"
        path.write_text(
            '{"seed_area": "Taito, Tokyo", "seed_concern": "Cafes"}\n'
            '{"seed_area": "Naha, Oki'
        )
        assert completed_seeds(path) == {("Taito, Tokyo", "Cafes")}

    def test_ignores_a_line_missing_its_seed(self, tmp_path) -> None:
        path = tmp_path / "pairs.jsonl"
        path.write_text('{"utterance": "orphan"}\n')
        assert completed_seeds(path) == set()


class TestRemainingSeeds:
    def test_drops_the_ones_already_done(self) -> None:
        seeds = [Seed("A", "Cafes"), Seed("B", "Parks"), Seed("C", "Bars")]
        done = {("B", "Parks")}
        assert [s.area for s in remaining_seeds(seeds, done)] == ["A", "C"]

    def test_keeps_the_order(self) -> None:
        seeds = [Seed("A", "x"), Seed("B", "y")]
        assert remaining_seeds(seeds, set()) == seeds
