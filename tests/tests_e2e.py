#!/usr/bin/env python

import os
from unittest import TestCase

test_data_dir = "./tests/data/"
test_output_dir = "./tests/outputs/"
command_line = "python convert_donjon_to_homebrewery.py {0}/{2}_test_file.json -o {1}/{2}.txt --testmode"


class E2E(TestCase):
    """ Checks word count of final document for all ruleset variants """
    def test_fantasy(self):
        os.system(f"{command_line.format(test_data_dir, test_output_dir, 'fantasy')}")
        with open(f"{test_output_dir}fantasy.txt", "r", encoding="utf-8") as fantasy:
            check_value = len(fantasy.read())
            assert check_value == 26330, f"Should be 26330 but is {check_value}"


    def test_adnd(self):
        os.system(f"{command_line.format(test_data_dir, test_output_dir, 'adnd')}")
        with open(f"{test_output_dir}adnd.txt", "r", encoding="utf-8") as adnd:
            check_value = len(adnd.read())
            assert check_value == 82540, f"Should be 82540 but is {check_value}"


    def test_4e(self):
        os.system(f"{command_line.format(test_data_dir, test_output_dir, '4e')}")
        with open(f"{test_output_dir}4e.txt", "r", encoding="utf-8") as fourth:
            check_value = len(fourth.read())
            assert check_value == 89067, f"Should be 89067 but is {check_value}"


    def test_5e(self):
        os.system(f"{command_line.format(test_data_dir, test_output_dir, '5e')}")
        with open(f"{test_output_dir}5e.txt", "r", encoding="utf-8") as fifth:
            check_value = len(fifth.read())
            assert check_value == 41867, f"Should be 41867 but is {check_value}"
