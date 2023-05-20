#!/usr/bin/env python

from unittest import TestCase, mock
from unittest.mock import patch
from dth.utilities import locations, statblocks, ai


# locations test data
TREASURE = "Treasure: 13 sp; 15 cp; 16 cp; 15 sp"
MAGICAL_ITEM = "Potion of Fire Breath (uncommon, dmg 187)"
MANY_MAGICAL_ITEM = "5 x Potion of Healing (common, dmg 187)"
MULTI_MONSTER_LIST_4E = "3 x Half-Orc Death Mage (mm2 140, 250 xp) and 2 x Half-Orc Hunter (mm2 140, 200 xp)"
MULTI_MONSTER_LIST_5E = "Firenewt Warlock of Imix (cr 1, vgm 143) and 1 x Firenewt Warrior (cr 1/2, vgm 142); medium, 300 xp"
MONSTER_DETAIL_4E = "Dragonkin Kobold Pact-Bound Adept (dr1 227, 250 xp)"
MONSTER_DETAIL_5E = "Firenewt Warlock of Imix (cr 1, vgm 143)"
MULTI_MONSTER_DETAIL_5E = "Drow House Captain (cr 9, mtf 184, vgm 154)"

# statblocks test data
SAVING_THROW = {"proficiencies": [
		{
			"value": 7,
			"proficiency": {
				"index": "saving-throw-dex",
				"name": "Saving Throw: DEX",
				"url": "/api/proficiencies/saving-throw-dex"
			}
		}
	]}
SKILL_CHECK = {"proficiencies": [
		{
			"value": 11,
			"proficiency": {
				"index": "skill-perception",
				"name": "Skill: Perception",
				"url": "/api/proficiencies/skill-perception"
			}
		}
	]}
BOTH = {"proficiencies": [
		{
			"value": 10,
			"proficiency": {
				"index": "saving-throw-con",
				"name": "Saving Throw: CON",
				"url": "/api/proficiencies/saving-throw-con"
			}
		},
		{
			"value": 7,
			"proficiency": {
				"index": "skill-stealth",
				"name": "Skill: Stealth",
				"url": "/api/proficiencies/skill-stealth"
			}
		}
	]}


class Locations(TestCase):
    """ Test cases for locations helper functions """
    # sum up treasure
    def test_sum_up_treasure_returns_none(self):
        no_currencies = locations.sum_up_treasure(TREASURE, "foo")

        self.assertEqual(no_currencies, None)


    def test_sum_up_treasure_returns_summed_totals(self):
        currencies = locations.sum_up_treasure(TREASURE, "dnd_5e")

        self.assertEqual(currencies, "28 sp, 31 cp")


    # add magical item to list
    def test_add_magical_items_to_list_return_empty_dict(self):
        no_magic_items = locations.add_magical_items_to_list("5 gp", 5)

        self.assertEqual(no_magic_items, {})


    def test_add_magical_items_to_list_return_dict(self):
        magic_items = locations.add_magical_items_to_list(MAGICAL_ITEM, 10)

        self.assertEqual(magic_items, {'Potion of Fire Breath **U**': 'dmg p.187/10'})


    def test_add_magical_items_to_list_return_dict_with_quantity(self):
        # also tests nicely formatted magic item helper function
        magic_items = locations.add_magical_items_to_list(MANY_MAGICAL_ITEM, 5)

        self.assertEqual(magic_items, {'Potion of Healing **C** (5)': 'dmg p.187/5'})


    # compile_monster_and_combat_details for 4e and 5e
    def test_compile_monster_return_correct_response_for_4e(self):
        monster_list, combat_list, xp_list = locations.compile_monster_and_combat_details(
                                                            MULTI_MONSTER_LIST_4E,
                                                            "dnd_4e",
                                                            [],
                                                            [],
                                                            []
                                                        )

        self.assertEqual(monster_list, [
                                        'Half-Orc Death Mage (mm2 140',
                                        'Half-Orc Hunter (mm2 140'
                                        ]
                                    )
        # combat type
        self.assertEqual(combat_list, [])
        # xp amount
        self.assertEqual(xp_list, ['250', '200'])


    def test_compile_monster_return_correct_response_for_fantasy(self):
        # should never happen
        monster_list, combat_list, xp_list = locations.compile_monster_and_combat_details(
                                                            MULTI_MONSTER_LIST_4E,
                                                            "fantasy",
                                                            [],
                                                            [],
                                                            []
                                                        )
        
        self.assertEqual(monster_list, [])
        self.assertEqual(combat_list, [])
        self.assertEqual(xp_list, [])


    def test_compile_monster_return_correct_response_for_5e(self):
        monster_list, combat_list, xp_list = locations.compile_monster_and_combat_details(
                                                                        MULTI_MONSTER_LIST_5E,
                                                                        "dnd_5e",
                                                                        [],
                                                                        [],
                                                                        []
                                                                    )

        # monster list
        self.assertEqual(monster_list, [
                                        'Firenewt Warlock of Imix (cr 1, vgm 143)',
                                        'Firenewt Warrior (cr 1/2, vgm 142)'
                                        ]
                                    )
        # combat type
        self.assertEqual(combat_list, ['medium'])
        # xp amount
        self.assertEqual(xp_list, ['300'])


    # extract book details for 4e and 5e
    def test_extract_book_details_correct_response_for_4e(self):
        book, name = locations.extract_book_details(MONSTER_DETAIL_4E, "dnd_4e")

        self.assertEqual(book, "Dragonkin Kobold Pact-Bound Adept")
        self.assertEqual(name, "dr1 p.227, p.250 p.xp)")



    def test_extract_book_details_correct_response_for_5e(self):
        book, name = locations.extract_book_details(MONSTER_DETAIL_5E, "dnd_5e")

        self.assertEqual(book, "Firenewt Warlock of Imix")
        self.assertEqual(name, "vgm p.143")


    def test_extract_book_details_correct_response_multi_sourcebooks_for_5e(self):
        book, name = locations.extract_book_details(MULTI_MONSTER_DETAIL_5E, "dnd_5e")

        self.assertEqual(book, "Drow House Captain")
        self.assertEqual(name, "mtf p.184 / vgm p.154")


    def test_extract_book_details_empty_response_for_fantasy(self):
        # should never happen
        response = locations.extract_book_details(MONSTER_DETAIL_5E, "fantasy")

        self.assertEqual(response, None)


class Statblocks(TestCase):
    """ Test cases for statblocks helper functions """
    # Mocking request to dnd api
    def mocked_requests_get(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

        if args[0] == 'https://www.dnd5eapi.co/api/monsters/foobar':
            return MockResponse("not found", 404)
        elif args[0] == 'https://www.dnd5eapi.co/api/monsters/goblin':
            return MockResponse("goblin", 200)

        return MockResponse(None, 404)

    #request monster statblock
    @patch('requests.get', side_effect=mocked_requests_get)
    def test_request_monster_statblock_returns_404(self, mock_get):
        response = statblocks.request_monster_statblock("foobar")
        self.assertIn(response, "not found")
    
        # We can even assert that our mocked method was called with the right parameters
        self.assertIn(mock.call('https://www.dnd5eapi.co/api/monsters/foobar'), mock_get.call_args_list)


    @patch('requests.get', side_effect=mocked_requests_get)
    def test_request_monster_statblock_returns_monster(self, mock_get):
        response = statblocks.request_monster_statblock("goblin")
        self.assertIn(response, "goblin")
    
        # We can even assert that our mocked method was called with the right parameters
        self.assertIn(mock.call('https://www.dnd5eapi.co/api/monsters/goblin'), mock_get.call_args_list)


    # get abiltity modifier
    def test_get_ability_modifier_returns_large_positive_value(self):
        ability_modifier = statblocks.get_ability_modifier(20)

        self.assertIn(ability_modifier, "+5")


    def test_get_ability_modifier_returns_zero_value(self):
        ability_modifier = statblocks.get_ability_modifier(10)

        self.assertIn(ability_modifier, "+0")


    def test_get_ability_modifier_returns_zero_value(self):
        ability_modifier = statblocks.get_ability_modifier(8)

        self.assertIn(ability_modifier, "-1")


    # extract proficiencies from api response
    def test_extract_proficiencies_from_api_returns_skill(self):
        save, skill = statblocks.extract_proficiencies_from_api_response(SKILL_CHECK)

        self.assertEqual(save, [])
        self.assertEqual(skill, [('Perception', 11)])


    def test_extract_proficiencies_from_api_returns_saving_throw(self):
        save, skill = statblocks.extract_proficiencies_from_api_response(SAVING_THROW)

        self.assertEqual(save, [('DEX', 7)])
        self.assertEqual(skill, [])


    def test_extract_proficiencies_from_api_returns_both(self):
        save, skill = statblocks.extract_proficiencies_from_api_response(BOTH)

        self.assertEqual(save, [('CON', 10)])
        self.assertEqual(skill, [('Stealth', 7)])


    # convert low cr to fraction
    def test_convert_low_cr_to_fraction_returns_integer(self):
        response = statblocks.convert_low_cr_to_fraction(10)

        self.assertIn(response, "10")


    def test_convert_low_cr_to_fraction_returns_eigth(self):
        response = statblocks.convert_low_cr_to_fraction(0.125)

        self.assertIn(response, "1/8")


    def test_convert_low_cr_to_fraction_returns_quarter(self):
        response = statblocks.convert_low_cr_to_fraction(0.25)

        self.assertIn(response, "1/4")


    def test_convert_low_cr_to_fraction_returns_half(self):
        response = statblocks.convert_low_cr_to_fraction(0.5)

        self.assertIn(response, "1/2")


class AI(TestCase):
    """ Test cases for AI helper functions """    
    # send prompt to chatgpt
    @patch("ai.openai.ChatCompletion.create")
    def test_send_prompt_to_chatgpt(self, mock_openai):
        response = ai.send_prompt_to_chatgpt("foobar")

        # We can even assert that our mocked method was called with the right parameters
        self.assertIn(mock.call(model='gpt-3.5-turbo', messages=[{'role': 'user', 'content': 'foobar'}]), mock_openai.call_args_list)
        mock_openai.assert_called_once()


    # expand dungeon overview via ai
    @patch.object(ai, "send_prompt_to_chatgpt")
    def test_expand_dungeon_overview_via_ai(self, mock_send_prompt):
        mock_send_prompt.return_value = "I am an AI response!"
        response = ai.expand_dungeon_overview_via_ai("foobar", "foo", "bar")

        self.assertIn(response, "I am an AI response!")


    @patch.object(ai, "send_prompt_to_chatgpt")
    def test_expand_dungeon_overview_via_ai_raises_system_error(self, mock_send_prompt):
        mock_send_prompt.side_effect = SystemError("error")
        with self.assertRaises(SystemError):
            ai.expand_dungeon_overview_via_ai("foobar", "foo", "bar")


    # suggest a bbeg via ai
    @patch.object(ai, "send_prompt_to_chatgpt")
    def test_suggest_a_bbeg_via_ai(self, mock_send_prompt):
        mock_send_prompt.return_value = "I am an AI response!"
        response = ai.suggest_a_bbeg_via_ai("foobar", "foo", "bar")

        self.assertIn(response, "I am an AI response!")


    @patch.object(ai, "send_prompt_to_chatgpt")
    def test_suggest_a_bbeg_via_ai_raises_system_error(self, mock_send_prompt):
        mock_send_prompt.side_effect = SystemError("error")
        with self.assertRaises(SystemError):
            ai.suggest_a_bbeg_via_ai("foobar", "foo", "bar")


    # suggest adventure hooks via ai
    @patch.object(ai, "send_prompt_to_chatgpt")
    def test_suggest_adventure_hooks_via_ai(self, mock_send_prompt):
        mock_send_prompt.return_value = "I am an AI response!"
        response = ai.suggest_adventure_hooks_via_ai("foobar", "foo", "bar")

        self.assertIn(response, "I am an AI response!")


    @patch.object(ai, "send_prompt_to_chatgpt")
    def test_suggest_adventure_hooks_via_ai_raises_system_error(self, mock_send_prompt):
        mock_send_prompt.side_effect = SystemError("error")
        with self.assertRaises(SystemError):
            ai.suggest_adventure_hooks_via_ai("foobar", "foo", "bar")
