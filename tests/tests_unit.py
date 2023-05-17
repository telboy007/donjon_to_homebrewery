#!/usr/bin/env python

from unittest import TestCase
from unittest.mock import patch, mock_open
from utilities import locations, statblocks, ai

# locations test data
TREASURE = "Treasure: 13 sp; 15 cp; 16 cp; 15 sp"
MAGICAL_ITEM = "Potion of Fire Breath (uncommon, dmg 187)"
MANY_MAGICAL_ITEM = "5 x Potion of Healing (common, dmg 187)"
MULTI_MONSTER_LIST = "Firenewt Warlock of Imix (cr 1, vgm 143) and 1 x Firenewt Warrior (cr 1/2, vgm 142); medium, 300 xp"
MONSTER_DETAIL_4E = "Dragonkin Kobold Pact-Bound Adept (dr1 227, 250 xp)"
MONSTER_DETAIL_5E = "Firenewt Warlock of Imix (cr 1, vgm 143)"
MULTI_MONSTER_DETAIL_5E = "Drow House Captain (cr 9, mtf 184, vgm 154)"


class Locations(TestCase):
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
    def test_compile_monster_return_correct_reposnse_for_4e(self):
        monster_list = locations.compile_monster_and_combat_details(
                                                            MULTI_MONSTER_LIST,
                                                            "dnd_4e"
                                                        )

        self.assertEqual(monster_list, [
                                        'Firenewt Warlock of Imix (cr 1',
                                        'Firenewt Warrior (cr 1/2'
                                        ]
                                    )


    def test_compile_monster_return_correct_reposnse_for_5e(self):
        monster_list, combat_list, xp_list = locations.compile_monster_and_combat_details(
                                                                        MULTI_MONSTER_LIST,
                                                                        "dnd_5e"
                                                                    )

        # monster list
        self.assertEqual(monster_list, [
                                        'Firenewt Warlock of Imix (cr 1',
                                        'Firenewt Warrior (cr 1/2',
                                        'Firenewt Warlock of Imix (cr 1, vgm 143)',
                                        'Firenewt Warrior (cr 1/2, vgm 142)'
                                        ]
                                    )
        # combat type
        self.assertEqual(combat_list, ['medium'])
        # xp amount
        self.assertEqual(xp_list, ['300'])


    def test_compile_monster_return_none_reposnse_for_fantasy(self):
        # should never happen
        monster_list = locations.compile_monster_and_combat_details(MULTI_MONSTER_LIST, "fantasy")

        self.assertEqual(monster_list, None)


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
