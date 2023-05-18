"""Module providing statblock & dnd api helper functions"""
import requests


def request_monster_statblock(monster_name):
    """ make request to dnd5e api to get json formatted monster statblock """
    url = f"https://www.dnd5eapi.co/api/monsters/{monster_name}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    return "not found"


def get_ability_modifier(value):
    """ calculate ability modifier """
    if round((value - 10.1) / 2) < 0:
        return round((value - 10.1) / 2)
    return f"+{round((value - 10.1) / 2)}"


def extract_proficiencies_from_api_response(data):
    """ extract the saving throw and skill check information """
    saving_throws = []
    skill_checks = []

    if "proficiencies" in data:
        for proficiency in data['proficiencies']:
            proficiency_name = proficiency['proficiency']['name']
            value = proficiency['value']

            if proficiency_name.startswith("Saving Throw"):
                saving_throw_name = proficiency_name.split(':')[1].strip()
                saving_throws.append((saving_throw_name, value))
            elif proficiency_name.startswith("Skill"):
                skill_check_name = proficiency_name.split(':')[1].strip()
                skill_checks.append((skill_check_name, value))

    return saving_throws, skill_checks


def convert_low_cr_to_fraction(number):
    if number < 1:
        if number == 0.5:
            return "1/2"
        if number == 0.25:
            return "1/4"
        if number == 0.125:
            return "1/8"
    return number
