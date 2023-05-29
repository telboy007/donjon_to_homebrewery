#!/usr/bin/env python

import os
from unittest import TestCase

test_data_dir = "./tests/data"
test_output_dir = "./tests/outputs/"
command_line = "python convert_donjon_to_homebrewery.py {0}/{2}_test_file.json -o {1}/{2}.txt --testmode"


class E2E(TestCase):
    """ Checks word count of final document for all ruleset variants """
    def test_fantasy(self):
        os.system(f"{command_line.format(test_data_dir, test_output_dir, 'fantasy')}")
        with open(f"{test_output_dir}fantasy.txt", "r", encoding="utf-8") as fantasy:
            check_value = len(fantasy.read())
            assert check_value == 26232, f"Should be 26232 but is {check_value}"


    def test_adnd(self):
        os.system(f"{command_line.format(test_data_dir, test_output_dir, 'adnd')}")
        with open(f"{test_output_dir}adnd.txt", "r", encoding="utf-8") as adnd:
            check_value = len(adnd.read())
            assert check_value == 82449, f"Should be 82449 but is {check_value}"


    def test_4e(self):
        os.system(f"{command_line.format(test_data_dir, test_output_dir, '4e')}")
        with open(f"{test_output_dir}4e.txt", "r", encoding="utf-8") as fourth:
            check_value = len(fourth.read())
            assert check_value == 89017, f"Should be 89017 but is {check_value}"


    def test_5e_multi_egress(self):
        os.system(f"{command_line.format(test_data_dir, test_output_dir, '5e_multi_egress')}")
        with open(f"{test_output_dir}5e_multi_egress.txt", "r", encoding="utf-8") as fifth:
            check_value = len(fifth.read())
            assert check_value == 32569, f"Should be 32569 but is {check_value}"


    def test_5e_cave_and_abandoned(self):
        os.system(f"{command_line.format(test_data_dir, test_output_dir, '5e_cave')}")
        with open(f"{test_output_dir}5e_cave.txt", "r", encoding="utf-8") as fifth:
            check_value = len(fifth.read())
            assert check_value == 3764, f"Should be 3764 but is {check_value}"