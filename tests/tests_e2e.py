#!/usr/bin/env python

import os
from unittest import TestCase


class E2E(TestCase):
    """ Checks word count of final document for all ruleset variants """
    def test_fantasy(self):
        os.system("python convert_donjon_to_homebrewery.py ./tests/fantasy_test_file.json -o ./tests/fantasy.txt --testmode")
        with open("./tests/fantasy.txt", "r", encoding="utf-8") as fantasy:
            check_value = len(fantasy.read())
            assert check_value == 26330, f"Should be 26330 but is {check_value}"


    def test_adnd(self):
        os.system("python convert_donjon_to_homebrewery.py ./tests/adnd_test_file.json -o ./tests/adnd.txt --testmode")
        with open("./tests/adnd.txt", "r", encoding="utf-8") as adnd:
            check_value = len(adnd.read())
            assert check_value == 82540, f"Should be 82540 but is {check_value}"


    def test_4e(self):
        os.system("python convert_donjon_to_homebrewery.py ./tests/4e_test_file.json -o ./tests/4e.txt --testmode")
        with open("./tests/4e.txt", "r", encoding="utf-8") as fourth:
            check_value = len(fourth.read())
            assert check_value == 89067, f"Should be 89067 but is {check_value}"


    def test_5e(self):
        with open("./tests/5e.txt", "r", encoding="utf-8") as fifth:
            os.system("python convert_donjon_to_homebrewery.py ./tests/5e_test_file.json -o ./tests/5e.txt --testmode")
            check_value = len(fifth.read())
            assert check_value == 41867, f"Should be 41867 but is {check_value}"
