""" Dict to hold details of donjon wandering monsters """

NEWLINE = '\n'


def create_donjon_wandering_monsters(data):
    """ Wandering monsters """
    wandering_monsters = {}
    monster_details = []

    wandering_monsters["monsters"] = False
    # populate details if available
    if "wandering_monsters" in data:
        wandering_monsters["monsters"] = True
        for key, val in data["wandering_monsters"].items():
            monster_details.append({key:val.replace(NEWLINE, ' ')})
        wandering_monsters["monster_details"] = monster_details

    return wandering_monsters
