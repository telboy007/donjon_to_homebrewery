#!/bin/python

"""Unit tests for utility modules"""

from unittest import TestCase, mock
from unittest.mock import patch
from requests import Session
from dth.utilities import locations, statblocks, ai, summary, overview

# locations test data
TREASURE = "Treasure: 13 sp; 15 cp; 16 cp; 15 sp"
TREASURE_HORDE = (
    "<html><body><div class='content'>10000 gp, 7000 sp</div></body></html>"
)
DUNGEON_GRAFFITI = '<div class="content">"Foo"</div><div class="content">"Bar"</div><div class="content">"Foobar"</div>'
MAGICAL_ITEM = "Potion of Fire Breath (uncommon, dmg 187)"
MANY_MAGICAL_ITEM = "5 x Potion of Healing (common, dmg 187)"
MIXED_MAGICAL_ITEM = "Potion of Fire Breath (uncommon, dmg 187), Cloak of Billowing (common, xge 136), Shadowfell Shard (rare, tce 135)"
MULTI_MONSTER_LIST_4E = "3 x Half-Orc Death Mage (mm2 140, 250 xp) and 2 x Half-Orc Hunter (mm2 140, 200 xp)"
MULTI_MONSTER_LIST_5E = "Firenewt Warlock of Imix (cr 1, vgm 143) and 1 x Firenewt Warrior (cr 1/2, vgm 142); medium, 300 xp"
MONSTER_DETAIL_4E = "Dragonkin Kobold Pact-Bound Adept (dr1 227, 250 xp)"
MONSTER_DETAIL_5E = "Firenewt Warlock of Imix (cr 1, vgm 143)"
MULTI_MONSTER_SOURCEBOOK_5E = "Drow House Captain (cr 9, mtf 184, vgm 154)"
MONSTER_LIST_OF_DICTS = [
    {
        "1": "Ogre Zombie (cr 2, mm 316) and 1 x Zombie (cr 1/4, mm 316); deadly, 500 xp, gathered around an evil shrine"
    }
]

# statblocks test data
SAVING_THROW = {
    "proficiencies": [
        {
            "value": 7,
            "proficiency": {
                "index": "saving-throw-dex",
                "name": "Saving Throw: DEX",
                "url": "/api/proficiencies/saving-throw-dex",
            },
        }
    ]
}
SKILL_CHECK = {
    "proficiencies": [
        {
            "value": 11,
            "proficiency": {
                "index": "skill-perception",
                "name": "Skill: Perception",
                "url": "/api/proficiencies/skill-perception",
            },
        }
    ]
}
BOTH = {
    "proficiencies": [
        {
            "value": 10,
            "proficiency": {
                "index": "saving-throw-con",
                "name": "Saving Throw: CON",
                "url": "/api/proficiencies/saving-throw-con",
            },
        },
        {
            "value": 7,
            "proficiency": {
                "index": "skill-stealth",
                "name": "Skill: Stealth",
                "url": "/api/proficiencies/skill-stealth",
            },
        },
        {
            "value": 11,
            "proficiency": {
                "index": "skill-perception",
                "name": "Skill: Perception",
                "url": "/api/proficiencies/skill-perception",
            },
        },
    ]
}
ARMOUR_TWO_PIECES = [
    {
        "type": "armor",
        "value": 15,
        "armor": [
            {
                "index": "leather-armor",
                "name": "Leather Armor",
                "url": "/api/equipment/leather-armor",
            },
            {"index": "shield", "name": "Shield", "url": "/api/equipment/shield"},
        ],
    }
]
ARMOUR_ONE_PIECE = [
    {
        "type": "armor",
        "value": 15,
        "armor": [
            {
                "index": "leather-armor",
                "name": "Leather Armor",
                "url": "/api/equipment/leather-armor",
            }
        ],
    }
]
NATURAL_ARMOUR = [{"type": "natural", "value": 19}]
NO_ARMOUR = [{"type": "dex", "value": 12}]

# summary test data
TEST_XP_LIST = [100, 100, 100, 100, 100]
TEST_MONSTER_LIST = [
    "Goblin",
    "Adult Black Dragon",
    "Goblin",
    "Beholder",
    "Roper",
    "Goblin",
]


class Locations(TestCase):
    """Test cases for locations helper functions"""

    # sum up treasure
    def test_sum_up_treasure_returns_none(self) -> None:
        no_currencies = locations.sum_up_treasure(TREASURE, "foo")

        self.assertEqual(no_currencies, None)

    def test_sum_up_treasure_returns_summed_totals(self) -> None:
        currencies = locations.sum_up_treasure(TREASURE, "dnd_5e")

        self.assertEqual(currencies, "28 sp, 31 cp")

    # add magical item to list
    def test_add_magical_items_to_list_return_empty_list(self) -> None:
        no_magic_items = locations.add_magical_items_to_list([], "5 gp", 5)

        self.assertEqual(no_magic_items, [])

    def test_add_magical_items_to_list_return_list_of_lists(self) -> None:
        magic_items = locations.add_magical_items_to_list([], MAGICAL_ITEM, 10)

        self.assertEqual(magic_items, [["Potion of Fire Breath **U**", "dmg p.187/10"]])

    def test_add_magical_items_to_list_return_list_of_lists_with_quantity(self) -> None:
        # also tests nicely formatted magic item helper function
        magic_items = locations.add_magical_items_to_list([], MANY_MAGICAL_ITEM, 5)

        self.assertEqual(magic_items, [["Potion of Healing **C** (5)", "dmg p.187/5"]])

    def test_magical_items_from_different_sourcebooks_returned(self) -> None:
        magic_items = locations.add_magical_items_to_list([], MIXED_MAGICAL_ITEM, 8)

        self.assertEqual(len(magic_items), 3)

    # compile monster and combat details
    def test_compile_monster_return_correct_response_for_4e(self) -> None:
        (
            monster_list,
            combat_list,
            xp_list,
        ) = locations.compile_monster_and_combat_details(
            MULTI_MONSTER_LIST_4E, "dnd_4e", [], [], []
        )

        self.assertEqual(
            monster_list, ["Half-Orc Death Mage (mm2 140", "Half-Orc Hunter (mm2 140"]
        )
        # combat type
        self.assertEqual(combat_list, [])
        # xp amount
        self.assertEqual(xp_list, ["250", "200"])

    def test_compile_monster_return_correct_response_for_fantasy(self) -> None:
        # should never happen
        (
            monster_list,
            combat_list,
            xp_list,
        ) = locations.compile_monster_and_combat_details(
            MULTI_MONSTER_LIST_4E, "fantasy", [], [], []
        )

        self.assertEqual(monster_list, [])
        self.assertEqual(combat_list, [])
        self.assertEqual(xp_list, [])

    def test_compile_monster_return_correct_response_for_5e(self) -> None:
        (
            monster_list,
            combat_list,
            xp_list,
        ) = locations.compile_monster_and_combat_details(
            MULTI_MONSTER_LIST_5E, "dnd_5e", [], [], []
        )

        # monster list
        self.assertEqual(
            monster_list,
            [
                "Firenewt Warlock of Imix (cr 1, vgm 143)",
                "Firenewt Warrior (cr 1/2, vgm 142)",
            ],
        )
        # combat type
        self.assertEqual(combat_list, ["medium"])
        # xp amount
        self.assertEqual(xp_list, ["300"])

    def test_compile_monster_return_correct_response_for_5e_wandering_monsters(
        self,
    ) -> None:
        (
            monster_list,
            combat_list,
            xp_list,
        ) = locations.compile_monster_and_combat_details(
            MONSTER_LIST_OF_DICTS, "dnd_5e", [], [], []
        )

        # monster list
        self.assertEqual(
            monster_list, ["Ogre Zombie (cr 2, mm 316)", "Zombie (cr 1/4, mm 316)"]
        )
        # combat type
        self.assertEqual(combat_list, ["deadly"])
        # xp amount
        self.assertEqual(xp_list, ["500"])

    # extract book details for 4e and 5e
    def test_extract_book_details_correct_response_for_4e(self) -> None:
        book, name = locations.extract_book_details(MONSTER_DETAIL_4E, "dnd_4e")

        self.assertEqual(book, "Dragonkin Kobold Pact-Bound Adept")
        self.assertEqual(name, "dr1 p.227, p.250 p.xp)")

    def test_extract_book_details_correct_response_for_5e(self) -> None:
        book, cr, name = locations.extract_book_details(MONSTER_DETAIL_5E, "dnd_5e")

        self.assertEqual(book, "Firenewt Warlock of Imix")
        self.assertEqual(cr, "1")
        self.assertEqual(name, "vgm p.143")

    def test_extract_book_details_correct_response_multi_sourcebooks_for_5e(
        self,
    ) -> None:
        book, cr, name = locations.extract_book_details(
            MULTI_MONSTER_SOURCEBOOK_5E, "dnd_5e"
        )

        self.assertEqual(book, "Drow House Captain")
        self.assertEqual(cr, "9")
        self.assertEqual(name, "mtf p.184, vgm p.154")

    def test_extract_book_details_empty_response_for_fantasy(self) -> None:
        # should never happen
        response = locations.extract_book_details(MONSTER_DETAIL_5E, "fantasy")

        self.assertEqual(response, None)


class Statblocks(TestCase):
    """Test cases for statblocks helper functions"""

    # Mocking request to dnd api
    def mocked_requests_get(*args, **kwargs) -> mock:
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

        if args[0] == "https://www.dnd5eapi.co/api/monsters/foobar":
            return MockResponse("not found", 404)
        if args[0] == "https://www.dnd5eapi.co/api/monsters/goblin":
            return MockResponse("goblin", 200)

        return MockResponse(None, 404)

    # request monster statblock
    @patch("requests.get", side_effect=mocked_requests_get)
    def test_request_monster_statblock_returns_404(self, mock_get) -> None:
        response = statblocks.request_monster_statblock("foobar")
        self.assertIn(response, "not found")

        # We can even assert that our mocked method was called with the right parameters
        self.assertIn(
            mock.call("https://www.dnd5eapi.co/api/monsters/foobar", timeout=5),
            mock_get.call_args_list,
        )

    @patch("requests.get", side_effect=mocked_requests_get)
    def test_request_monster_statblock_returns_monster(self, mock_get) -> None:
        response = statblocks.request_monster_statblock("goblin")
        self.assertIn(response, "goblin")

        # We can even assert that our mocked method was called with the right parameters
        self.assertIn(
            mock.call("https://www.dnd5eapi.co/api/monsters/goblin", timeout=5),
            mock_get.call_args_list,
        )

    # get abiltity modifier
    def test_get_ability_modifier_returns_large_positive_value(self) -> None:
        ability_modifier = statblocks.get_ability_modifier(20)

        self.assertIn(ability_modifier, "+5")

    def test_get_ability_modifier_returns_zero_value(self) -> None:
        ability_modifier = statblocks.get_ability_modifier(10)

        self.assertIn(ability_modifier, "+0")

    def test_get_ability_modifier_returns_negative_value(self) -> None:
        ability_modifier = statblocks.get_ability_modifier(8)

        self.assertIn(ability_modifier, "-1")

    # extract proficiencies from api response
    def test_extract_proficiencies_from_api_returns_skill(self) -> None:
        save, skill = statblocks.extract_proficiencies_from_api_response(SKILL_CHECK)

        self.assertEqual(save, "")
        self.assertEqual(skill, "Perception +11")

    def test_extract_proficiencies_from_api_returns_saving_throw(self) -> None:
        save, skill = statblocks.extract_proficiencies_from_api_response(SAVING_THROW)

        self.assertEqual(save, "Dex +7")
        self.assertEqual(skill, "")

    def test_extract_proficiencies_from_api_returns_both(self) -> None:
        save, skill = statblocks.extract_proficiencies_from_api_response(BOTH)

        self.assertEqual(save, "Con +10")
        self.assertEqual(skill, "Stealth +7, Perception +11")

    # convert low cr to fraction
    def test_convert_low_cr_to_fraction_returns_integer(self) -> None:
        response = statblocks.convert_low_cr_to_fraction(10)

        self.assertIn(response, "10")

    def test_convert_low_cr_to_fraction_returns_eigth(self) -> None:
        response = statblocks.convert_low_cr_to_fraction(0.125)

        self.assertIn(response, "1/8")

    def test_convert_low_cr_to_fraction_returns_quarter(self) -> None:
        response = statblocks.convert_low_cr_to_fraction(0.25)

        self.assertIn(response, "1/4")

    def test_convert_low_cr_to_fraction_returns_half(self) -> None:
        response = statblocks.convert_low_cr_to_fraction(0.5)

        self.assertIn(response, "1/2")

    # check correct armour types are returned
    def test_format_armour_types_for_two_pieces_armour(self) -> None:
        response = statblocks.format_armour_type(ARMOUR_TWO_PIECES)

        self.assertEqual(response, "(leather armor, shield)")

    def test_format_armour_types_for_one_piece_armour(self) -> None:
        response = statblocks.format_armour_type(ARMOUR_ONE_PIECE)

        self.assertEqual(response, "(leather armor)")

    def test_format_armour_types_for_natural_armour(self) -> None:
        response = statblocks.format_armour_type(NATURAL_ARMOUR)

        self.assertEqual(response, "(natural)")

    def test_format_armour_types_for_no_armour(self) -> None:
        response = statblocks.format_armour_type(NO_ARMOUR)

        self.assertEqual(response, "")

    # check full page
    def test_check_full_page_when_only_space_for_one(self) -> None:
        """cumulative total, current statblock size, previous statblock size"""
        cumulative_total, new_page_break_required = statblocks.check_for_full_pages(
            3, 2, 1
        )

        self.assertEqual(cumulative_total, 2)
        self.assertTrue(new_page_break_required)

    def test_check_full_page_when_space_for_one_but_last_block_was_two(self) -> None:
        cumulative_total, new_page_break_required = statblocks.check_for_full_pages(
            3, 1, 2
        )

        self.assertEqual(cumulative_total, 1)
        self.assertTrue(new_page_break_required)

    def test_check_full_page_when_full_page(self) -> None:
        cumulative_total, new_page_break_required = statblocks.check_for_full_pages(
            4, 1, 1
        )

        self.assertEqual(cumulative_total, 1)
        self.assertTrue(new_page_break_required)

    def test_check_full_page_when_there_is_space(self) -> None:
        cumulative_total, new_page_break_required = statblocks.check_for_full_pages(
            1, 2, 1
        )

        self.assertEqual(cumulative_total, 3)
        self.assertFalse(new_page_break_required)


class AI(TestCase):
    """Test cases for AI helper functions"""

    # expand dungeon overview via ai
    @patch.object(ai, "send_prompt_to_chatgpt")
    def test_expand_dungeon_overview_via_ai(self, mock_send_prompt) -> None:
        mock_send_prompt.return_value = "I am an AI response!"
        response = ai.expand_dungeon_overview_via_ai("foobar", "foo", "bar")

        mock_send_prompt.assert_called_once_with(
            "Enhance the dungeon description using maximum 3 paragraphs in present tense. Mention details, sights and sounds of the entrance but not inside the dungeon.  No reference to skill checks. Ruleset is foobar. Dungeon description is foo: bar"
        )
        self.assertIn(response, "I am an AI response!")

    @patch.object(ai, "send_prompt_to_chatgpt")
    def test_expand_dungeon_overview_via_ai_raises_system_error(
        self, mock_send_prompt
    ) -> None:
        mock_send_prompt.side_effect = SystemError("error")
        with self.assertRaises(SystemError):
            ai.expand_dungeon_overview_via_ai("foobar", "foo", "bar")

    # suggest a bbeg via ai
    @patch.object(ai, "send_prompt_to_chatgpt")
    def test_suggest_a_bbeg_via_ai(self, mock_send_prompt) -> None:
        mock_send_prompt.return_value = "I am an AI response!"
        response = ai.suggest_a_bbeg_via_ai("foobar", "foo", "bar", "oof", "rab")

        mock_send_prompt.assert_called_once_with(
            "Suggest a monster from the foobar ruleset to be the dungeon boss based on the dungeon's description of foo and features of bar.  It should be a challenge for a party size of oof, and average party level of rab.  Describe the lair and up to three lair actions the dungeon boss will use."
        )
        self.assertIn(response, "I am an AI response!")

    @patch.object(ai, "send_prompt_to_chatgpt")
    def test_suggest_a_bbeg_via_ai_raises_system_error(self, mock_send_prompt) -> None:
        mock_send_prompt.side_effect = SystemError("error")
        with self.assertRaises(SystemError):
            ai.suggest_a_bbeg_via_ai("foobar", "foo", "bar", "bar", "foo")

    # suggest adventure hooks via ai
    @patch.object(ai, "send_prompt_to_chatgpt")
    def test_suggest_adventure_hooks_via_ai(self, mock_send_prompt) -> None:
        mock_send_prompt.return_value = "I am an AI response!"
        response = ai.suggest_adventure_hooks_via_ai("foobar", "foo", "bar")

        mock_send_prompt.assert_called_once_with(
            "Suggest two adventure hooks for a foobar dungeon based on it's description of foo and features of bar, including named NPC contact points and their flavour text."
        )
        self.assertIn(response, "I am an AI response!")

    @patch.object(ai, "send_prompt_to_chatgpt")
    def test_suggest_adventure_hooks_via_ai_raises_system_error(
        self, mock_send_prompt
    ) -> None:
        mock_send_prompt.side_effect = SystemError("error")
        with self.assertRaises(SystemError):
            ai.suggest_adventure_hooks_via_ai("foobar", "foo", "bar")


class Summary(TestCase):
    """Test cases for summary helper functions"""

    # check xp and shared xp totals
    def test_calculate_total_and_shared_xp(self) -> None:
        total_xp, shared_xp = summary.calculate_total_and_shared_xp(
            TEST_XP_LIST, party_size=5
        )

        self.assertEqual(total_xp, 500)
        self.assertEqual(shared_xp, 100)

    # check list deduper and sorter
    def test_dedupe_and_sort_list_via_dict(self) -> None:
        sorted_list = summary.dedupe_and_sort_list_via_dict(TEST_MONSTER_LIST)

        self.assertEqual(
            sorted_list, ["Adult Black Dragon", "Beholder", "Goblin", "Roper"]
        )


class Overview(TestCase):
    """Test cases for overview helper functions"""

    # generate treasure horde
    @patch.object(Session, "get")
    def test_generate_boss_treasure_horde_okay(self, mock_get) -> None:
        mock_response = mock.Mock()
        mock_get.return_value = mock_response
        mock_response.html.html = TREASURE_HORDE

        response = overview.generate_boss_treasure_horde(10)
        self.assertIn(response, "10000 gp, 7000 sp")
        mock_get.assert_called_once()

    # generate treasure horde failure
    @patch.object(Session, "get")
    def test_generate_boss_treasure_horde_fail(self, mock_get) -> None:
        mock_response = mock.Mock()
        mock_get.return_value = mock_response
        mock_response.html.html = "<html><body></body></html>"

        response = overview.generate_boss_treasure_horde(10)
        self.assertIn(response, "")
        mock_get.assert_called_once()

    # generate dungeon graffiti
    @patch.object(Session, "get")
    def test_generate_dungeon_graffiti_okay(self, mock_get) -> None:
        mock_response = mock.Mock()
        mock_get.return_value = mock_response
        mock_response.html.html = DUNGEON_GRAFFITI

        response = overview.generate_dungeon_graffiti()
        self.assertIn(response[2].text, '"Foobar"')
        mock_get.assert_called_once()

    # generate dungeon graffiti failure
    @patch.object(Session, "get")
    def test_generate_dungeon_graffiti_fail(self, mock_get) -> None:
        mock_response = mock.Mock()
        mock_get.return_value = mock_response
        mock_response.html.html = "<html><body></body></html>"

        response = overview.generate_dungeon_graffiti()
        self.assertIn(response, "")
        mock_get.assert_called_once()
