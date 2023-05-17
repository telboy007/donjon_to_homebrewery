""" Dict to hold details of donjon settings and AI enhancements """

from utilities.ai import expand_dungeon_overview_via_ai, suggest_a_bbeg_via_ai, suggest_adventure_hooks_via_ai


NEWLINE = '\n'


def create_donjon_overview(data, testmode):
    """ Overview and AI enhancements """
    overview = {}

    overview["floor"] = data["floor"]
    overview["walls"] = data["walls"]
    overview["temperature"] = data["temperature"].replace(NEWLINE, ' ')
    overview["illumination"] = data["illumination"]
    overview["special"] = data["special"] if "special" in data else False
    overview["blurb"] = data["history"] if "history" in data else False
    overview["dungeon_detail"] = f"{overview['floor']} floors, {overview['walls']} walls, temperature is {overview['temperature']}, and lighting is {overview['illumination']}."
    overview["ai_enhancements"] = False
    if not testmode:
        overview["ai_enhancements"] = True
        overview["flavour_text"] = expand_dungeon_overview_via_ai(overview["blurb"], overview["dungeon_detail"])
        overview["bbeg_and_lair"] = suggest_a_bbeg_via_ai(overview["blurb"], overview["dungeon_detail"])
        overview["adventure_hooks"] = suggest_adventure_hooks_via_ai(overview["blurb"], overview["bbeg_and_lair"])

    return overview
