""" Dict to hold details of donjon locations """

from dth.utilities.locations import sum_up_treasure, add_magical_items_to_list, compile_monster_and_combat_details

NEWLINE = '\n'


def create_single_location(room, settings, magic_items, monster_list, combat_list, xp_list):
    """ 
        Create dict of single location

        location["id"] string
        location["trap_detail"] list
        location["hidden_treasure"] list
        location["treasure"] string
        location["features"] string
        location["monster"] string / list (adnd)
        location["exits"] list of dicts
            {"direction", "exit_desc", "extra_detail", "leads_to"}
    """
    location = {}
    trap_detail = []
    hidden_treasure = []
    exits = []
    occupants = []

    location["id"] = room["id"]
    # check for contents, traps and hidden treasure
    if "contents" in room:
        if "detail" in room["contents"]:
            # deal with traps
            if "trap" in room["contents"]["detail"]:
                location["is_trap"] = True
                for detail in room["contents"]["detail"]["trap"]:
                    trap_detail.append(detail.replace(NEWLINE, ""))
                location["trap"] = trap_detail

            # hidden treasure
            if "hidden_treasure" in room["contents"]["detail"]:
                for detail in room["contents"]["detail"]["hidden_treasure"]:
                    if detail == "--":
                        continue
                    hidden_treasure.append(detail.replace(NEWLINE, " "))
                location["hidden_treasure"] = hidden_treasure
                
                # add to magic items list for the summary page
                if settings["ruleset"] == "dnd_5e":
                    magics = add_magical_items_to_list(detail.replace(NEWLINE, " "), location["id"])
                    magic_items.update(magics)

            # room description
            if "room_features" in room["contents"]["detail"]:
                location["features"] = room["contents"]["detail"]["room_features"]

            # monsters and treasure
            if "monster" in room["contents"]["detail"]:
                for thing in room["contents"]["detail"]["monster"]:
                    if thing == "--":
                        continue
                    # deal with loot
                    if thing.startswith("Treasure"):
                        if thing.count("(") == 0:
                            # treasure is just coins
                            location["treasure"] = sum_up_treasure(thing.replace(",", ";"), settings["ruleset"])
                        else:
                            # treasure has art objects & possibly magic items
                            location["treasure"] = thing.replace(NEWLINE, " ").replace("Treasure: ", "")

                            # add to magic items list for the summary page
                            if settings['ruleset'] == "dnd_5e":
                                magics = add_magical_items_to_list(thing.replace(NEWLINE, " ").replace("Treasure: ", ""), location["id"])
                                magic_items.update(magics)
                    else:
                        # adnd can have a lot of NPCs in the same location
                        occupants.append(thing)
                        # add monster, combat types and xp to global lists
                        monster_list, combat_list, xp_list = compile_monster_and_combat_details(thing, settings["ruleset"], monster_list, combat_list, xp_list)
                    # add list of one or many
                    location["monster"] = occupants
                    
    # parse exit details
    if "doors" in room:
        for direction, door_detail in room["doors"].items():
            for detail in door_detail:
                # extra description of exit
                DESC = ""
                if detail["type"] == "secret":
                    if "trap" in detail:
                        DESC += f" ***Secret:*** {detail['secret'].replace(NEWLINE, ' ')} ***Trap:*** {detail['trap'].replace(NEWLINE, ' ')}"
                    else:
                        DESC += f"***Secret:*** {detail['secret'].replace(NEWLINE, ' ')}"
                if detail["type"] == "trapped":
                    if "trap" in detail:
                        DESC += f" ***Trap:*** {detail['trap'].replace(NEWLINE, ' ')}"
                    else:
                        DESC += " ***Trap***: Already disarmed."
                if "out_id" in detail:
                    exits.append({"direction": direction.capitalize(), "exit_desc": detail["desc"], "extra_detail": DESC, "leads_to": detail["out_id"]})
                else:
                    exits.append({"direction": direction.capitalize(), "exit_desc": detail["desc"], "extra_detail": DESC, "leads_to": "n/a"})
        location["exits"] = exits

    return location, magic_items, monster_list, combat_list, xp_list