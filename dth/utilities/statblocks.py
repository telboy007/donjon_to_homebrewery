"""Module providing statblock & dnd api helper functions"""

import requests
from dth.utilities.summary import dedupe_and_sort_list_via_dict


def request_monster_statblock(monster_name: str) -> dict[str, object] | str:
    """make request to dnd5e api to get json formatted monster statblock"""
    url = f"https://www.dnd5eapi.co/api/monsters/{monster_name}"
    response = requests.get(url, timeout=5)

    if response.status_code == 200:
        return response.json()
    return "not found"


def get_ability_modifier(value: int) -> str | str:
    """calculate ability modifier"""
    if round((value - 10.1) / 2) < 0:
        return f"{round((value - 10.1) / 2)}"
    return f"+{round((value - 10.1) / 2)}"


def extract_proficiencies_from_api_response(data: dict) -> tuple[list, list]:
    """extract the saving throw and skill check information"""
    saving_throws = []
    skill_checks = []

    if "proficiencies" in data:
        for proficiency in data["proficiencies"]:
            proficiency_name = proficiency["proficiency"]["name"]
            value = proficiency["value"]

            if proficiency_name.startswith("Saving Throw"):
                saving_throw_name = proficiency_name.split(":")[1].strip()
                saving_throws.append((saving_throw_name, value))
            elif proficiency_name.startswith("Skill"):
                skill_check_name = proficiency_name.split(":")[1].strip()
                skill_checks.append((skill_check_name, value))

    return saving_throws, skill_checks


def convert_low_cr_to_fraction(number: int) -> str:
    """convert low CRs to fractions"""
    if number < 1:
        if number == 0.5:
            return "1/2"
        if number == 0.25:
            return "1/4"
        if number == 0.125:
            return "1/8"
    return f"{number}"


def format_armour_type(armour: dict) -> str | str | str | str:
    """format armour and include all types i.e. shield"""
    armour_list = []
    if armour[0]["type"] == "armor":
        if len(armour[0]["armor"]) > 1:
            for ac_type in armour[0]["armor"]:
                armour_list.append(ac_type["name"].lower())
            return f"({', '.join(dedupe_and_sort_list_via_dict(armour_list))})"
        return f"({armour[0]['armor'][0]['name'].lower()})"
    if armour[0]["type"] == "natural":
        return "(natural)"
    return ""


def check_for_full_pages(
    cumulative: int, statblock_size: int, previous: int
) -> tuple[int, bool] | tuple[int, bool] | tuple[int, bool] | tuple[int, bool]:
    """
    need to split up statblocks when:
    current_statblocks = 3 and next is size = 2
    current_statblocks = 3 and last one was size = 2
    current_statblocks = 4
    """
    if cumulative == 3 and int(statblock_size) == 2:
        cumulative = int(statblock_size)
        return cumulative, True
    if cumulative == 3 and previous == 2:
        cumulative = int(statblock_size)
        return cumulative, True
    if cumulative == 4:
        cumulative = int(statblock_size)
        return cumulative, True
    cumulative += int(statblock_size)
    return cumulative, False
