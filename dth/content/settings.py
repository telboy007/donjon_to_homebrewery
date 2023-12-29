""" Dict to hold all settings used to generate the donjon dungeon """


def create_donjon_settings(data):
    """Settings"""
    settings = {}

    settings["donjon_url"] = "https://donjon.bin.sh"
    settings["homebrewery_url"] = "https://homebrewery.naturalcrit.com"
    settings["dth_url"] = "https://github.com/telboy007/donjon_to_homebrewery"
    settings["ruleset"] = data["infest"]
    settings["dungeon_name"] = data["name"]
    settings["dungeon_level"] = data["level"]
    settings["party_size"] = data["n_pc"]
    settings["motif"] = data["motif"]
    settings["random_seed"] = data["seed"]
    settings["dungeon_size"] = data["dungeon_size"]
    settings["dungeon_layout"] = data["dungeon_layout"]
    settings["peripheral_egress"] = data["peripheral_egress"]
    settings["room_layout"] = data["room_layout"]
    settings["room_size"] = data["room_size"]
    settings["polymorph_rooms"] = data["room_polymorph"]
    settings["doors"] = data["door_set"]
    settings["corridors"] = data["corridor_layout"]
    settings["remove_deadends"] = data["remove_deadends"]
    settings["stairs"] = data["add_stairs"]
    settings["map_style"] = data["map_style"]
    settings["grid"] = data["grid"]

    # work out human readable ruleset and if we can generate summary page
    if settings["ruleset"] == "dnd_5e":
        settings["ruleset_nice"] = "D&D 5e"
        settings["summary_page"] = True
    elif settings["ruleset"] == "dnd_4e":
        settings["ruleset_nice"] = "D&D 4e"
        settings["summary_page"] = True
    elif settings["ruleset"] == "adnd":
        settings["ruleset_nice"] = "AD&D"
        settings["summary_page"] = False
    else:
        settings["ruleset_nice"] = "fantasy"
        settings["summary_page"] = False

    return settings
