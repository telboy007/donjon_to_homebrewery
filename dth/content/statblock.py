""" Dict to hold all settings used to generate a 5e stat block """

from dth.utilities.statblocks import (
    request_monster_statblock,
    get_ability_modifier,
    extract_proficiencies_from_api_response,
    convert_low_cr_to_fraction,
    format_armour_type,
)


def create_5e_statblock(
    monster: dict, skipped_monsters: list
) -> tuple[dict, list] | tuple[dict, list]:
    """create dict for statblock and add not founds to skipped list"""
    monster_statblock = {}
    stat_block_size = 0

    # api call to dnd5eapi
    response = request_monster_statblock(monster)

    # check for any monsters listed as in monster manual but not found in api
    if response == "not found":
        skipped_monsters.append(monster.replace("-", " ").title())
        return {}, skipped_monsters

    monster_statblock["name"] = response["name"].capitalize()
    monster_statblock["size"] = response["size"].capitalize()
    monster_statblock["type"] = response["type"].capitalize()
    monster_statblock["alignment"] = response["alignment"].title()
    monster_statblock["ac"] = response["armor_class"][0]["value"]

    # work out correct armour type(s) to show
    if "type" in response["armor_class"][0]:
        monster_statblock["armour_type"] = format_armour_type(response["armor_class"])
    else:
        monster_statblock["armor_type"] = ""

    monster_statblock["hp"] = response["hit_points"]
    monster_statblock["hp_formula"] = response["hit_points_roll"]

    # handle additional movement types
    if len(response["speed"]) > 1:
        movement_types = []
        for key, value in response["speed"].items():
            movement_types.append(f"{key.capitalize()} {value}")
        monster_statblock["speed"] = ", ".join(movement_types).replace("Walk ", "")
    else:
        monster_statblock["speed"] = response["speed"]["walk"]

    # attributes and modifiers
    monster_statblock["str"] = response["strength"]
    monster_statblock["str_mod"] = get_ability_modifier(monster_statblock["str"])
    monster_statblock["dex"] = response["dexterity"]
    monster_statblock["dex_mod"] = get_ability_modifier(monster_statblock["dex"])
    monster_statblock["con"] = response["constitution"]
    monster_statblock["con_mod"] = get_ability_modifier(monster_statblock["con"])
    monster_statblock["int"] = response["intelligence"]
    monster_statblock["int_mod"] = get_ability_modifier(monster_statblock["int"])
    monster_statblock["wis"] = response["wisdom"]
    monster_statblock["wis_mod"] = get_ability_modifier(monster_statblock["wis"])
    monster_statblock["cha"] = response["charisma"]
    monster_statblock["cha_mod"] = get_ability_modifier(monster_statblock["cha"])

    # extract saving throws and skill check modifiers
    saving_throws, skill_checks = extract_proficiencies_from_api_response(response)
    if saving_throws:
        throws = []
        for key, value in saving_throws:
            throws.append(f"{key.capitalize()} +{value}")
        monster_statblock["saving_throws"] = ", ".join(throws)

    if skill_checks:
        skills = []
        for key, value in skill_checks:
            skills.append(f"{key.capitalize()} +{value}")
        monster_statblock["skill_checks"] = ", ".join(skills)

    # resistances and immunities
    if response["damage_vulnerabilities"]:
        monster_statblock["damage_vulnerabilities"] = ", ".join(
            response["damage_vulnerabilities"]
        )

    if response["damage_resistances"]:
        monster_statblock["damage_resistances"] = ", ".join(
            response["damage_resistances"]
        )

    if response["damage_immunities"]:
        monster_statblock["damage_immunities"] = ", ".join(
            response["damage_immunities"]
        )

    if response["condition_immunities"]:
        con_imm_list = []
        for condition_immunity in response["condition_immunities"]:
            con_imm_list.append(condition_immunity["index"])
        monster_statblock["condition_immunities"] = ", ".join(con_imm_list)

    # extract senses
    monster_statblock["senses"] = (
        str(response["senses"])
        .replace("{", "")
        .replace("}", "")
        .replace("'", "")
        .replace(":", "")
        .replace("_", " ")
    )

    # languages
    if response["languages"]:
        monster_statblock["languages"] = response["languages"]
        stat_block_size += len(response["languages"])

    # cr and xp
    monster_statblock["CR"] = convert_low_cr_to_fraction(response["challenge_rating"])
    monster_statblock["XP"] = response["xp"]

    # traits and special abilities
    if response["special_abilities"]:
        special_abilities = {}
        for ability in response["special_abilities"]:
            special_abilities[ability["name"]] = ability["desc"]
            stat_block_size += len(ability["name"]) + len(ability["desc"])
        monster_statblock["special_abilities"] = special_abilities

    # monster actions
    if response["actions"]:
        actions = {}
        for action in response["actions"]:
            actions[action["name"]] = action["desc"]
            stat_block_size += len(action["name"]) + len(action["desc"])
        monster_statblock["actions"] = actions

    # set stat block size
    if stat_block_size >= 698:
        monster_statblock["markdown_size"] = "2"
    else:
        monster_statblock["markdown_size"] = "1"

    # monster legendary actions
    if response["legendary_actions"]:
        legendary_actions = {}
        for legendary_action in response["legendary_actions"]:
            legendary_actions[legendary_action["name"]] = legendary_action["desc"]
        monster_statblock["legendary_actions"] = legendary_actions
        # set stat block size as 2 for legendary action monsters by default
        monster_statblock["markdown_size"] = "2"

    return monster_statblock, skipped_monsters
