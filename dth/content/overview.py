""" Dict to hold details of donjon settings and AI enhancements """

from utilities.ai import (
    expand_dungeon_overview_via_ai,
    suggest_a_bbeg_via_ai,
    suggest_adventure_hooks_via_ai,
)
from utilities.overview import generate_boss_treasure_horde
from utilities.locations import add_magical_items_to_list


NEWLINE = "\n"


def create_donjon_overview(data, settings, testmode):
    """Overview and AI enhancements"""
    overview = {}

    overview["floor"] = data["floor"]
    overview["walls"] = data["walls"]
    overview["temperature"] = data["temperature"].replace(NEWLINE, " ")
    overview["illumination"] = data["illumination"]
    overview["special"] = data["special"] if "special" in data else None
    # fix special so it shows in the table
    if overview["special"] is not None:
        overview["special"].replace(NEWLINE, " ")
    else:
        overview["special"] = "None"
    overview["blurb"] = data["history"] if "history" in data else False
    overview[
        "dungeon_detail"
    ] = f"{overview['floor']} floors, {overview['walls']} walls, temperature is {overview['temperature']}, and lighting is {overview['illumination']}."

    # AI ENHANCEMENTS
    magic_items = []
    overview["ai_enhancements"] = False
    overview["flavour_text"] = False
    overview["bbeg_and_lair"] = False
    overview["adventure_hooks"] = False
    overview["boss_treasure"] = False
    if not testmode:
        overview["ai_enhancements"] = True
        # only 5e dungeons have a description, use dungeon name for other rulesets
        if overview["blurb"]:
            overview["flavour_text"] = expand_dungeon_overview_via_ai(
                settings["ruleset_nice"], overview["blurb"], overview["dungeon_detail"]
            )
        else:
            overview["flavour_text"] = expand_dungeon_overview_via_ai(
                settings["ruleset_nice"],
                settings["dungeon_name"],
                overview["dungeon_detail"],
            )
        overview["bbeg_and_lair"] = suggest_a_bbeg_via_ai(
            settings["ruleset_nice"],
            overview["blurb"],
            overview["dungeon_detail"],
            settings["party_size"],
            settings["dungeon_level"],
        )
        overview["adventure_hooks"] = suggest_adventure_hooks_via_ai(
            settings["ruleset_nice"], overview["blurb"], overview["bbeg_and_lair"]
        )
        # generate some boss treasure
        overview["boss_treasure"] = generate_boss_treasure_horde(
            settings["dungeon_level"]
        )
        # add any horde magical items to global list
        magic_items = add_magical_items_to_list(overview["boss_treasure"], "Boss")

    return overview, magic_items
