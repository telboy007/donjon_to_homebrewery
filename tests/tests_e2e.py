#!/bin/python

"""E2E tests for content modules"""

import subprocess
from unittest import TestCase

TEST_DATA_DIR = "./tests/data"
TEST_OUTPUT_DIR = "./tests/outputs/"
CMD_LINE = "python convert_donjon_to_homebrewery.py {0}/{2}_test_file.json -o {1}/{2}.txt --testmode"


class E2E(TestCase):
    """Checks word count of final document for all ruleset variants"""

    def test_fantasy(self):
        """fantasy markdown length check"""
        subprocess.check_output(
            f"{CMD_LINE.format(TEST_DATA_DIR, TEST_OUTPUT_DIR, 'fantasy')}",
            shell=True,
        )
        with open(f"{TEST_OUTPUT_DIR}fantasy.txt", "r", encoding="utf-8") as fantasy:
            check_value = len(fantasy.read())
            assert check_value == 26236, f"Should be 26236 but is {check_value}"

    def test_adnd(self):
        """adnd markdown length check"""
        subprocess.check_output(
            f"{CMD_LINE.format(TEST_DATA_DIR, TEST_OUTPUT_DIR, 'adnd')}", shell=True
        )
        with open(f"{TEST_OUTPUT_DIR}adnd.txt", "r", encoding="utf-8") as adnd:
            check_value = len(adnd.read())
            assert check_value == 82453, f"Should be 82453 but is {check_value}"

    def test_4e(self):
        """4e markdown length check"""
        subprocess.check_output(
            f"{CMD_LINE.format(TEST_DATA_DIR, TEST_OUTPUT_DIR, '4e')}", shell=True
        )
        with open(f"{TEST_OUTPUT_DIR}4e.txt", "r", encoding="utf-8") as fourth:
            check_value = len(fourth.read())
            assert check_value == 89024, f"Should be 89024 but is {check_value}"

    def test_5e_multi_egress(self):
        """5e multi entrance markdown length check"""
        subprocess.check_output(
            f"{CMD_LINE.format(TEST_DATA_DIR, TEST_OUTPUT_DIR, '5e_multi_egress')}",
            shell=True,
        )
        with open(
            f"{TEST_OUTPUT_DIR}5e_multi_egress.txt", "r", encoding="utf-8"
        ) as fifth:
            check_value = len(fifth.read())
            assert check_value == 32677, f"Should be 32677 but is {check_value}"

    def test_5e_cave_and_abandoned(self):
        """5e cave and abandoned markdown length check"""
        subprocess.check_output(
            f"{CMD_LINE.format(TEST_DATA_DIR, TEST_OUTPUT_DIR, '5e_cave')}",
            shell=True,
        )
        with open(f"{TEST_OUTPUT_DIR}5e_cave.txt", "r", encoding="utf-8") as fifth:
            check_value = len(fifth.read())
            assert check_value == 3782, f"Should be 3782 but is {check_value}"
