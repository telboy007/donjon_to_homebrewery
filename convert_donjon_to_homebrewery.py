#!/usr/bin/env python

"""
    Donjon to homebrewery convertor
    line arguments:
        json file [mandatory]
        gm map (url) [optional]
        player map (url) [optional]
"""

import argparse
import json
from collections import OrderedDict


def set_check():
    """Set the initial number of characters in the file"""
    with open(args.output_filename, "r", encoding="utf-8") as readonly_file:
        return len(readonly_file.read())


def file_size(current_check):
    """Count the currenct number of characters in a file"""
    with open(args.output_filename, "r", encoding="utf-8") as readonly_file:
        new_size = len(readonly_file.read())
    if (new_size - current_check) > 2450:
        with open(args.output_filename, "a", encoding="utf-8") as append_file:
            append_file.write("{{footnote LOCATIONS}}\n")
            append_file.write("\\page\n")
            append_file.write("{{pageNumber,auto}}\n")
        # set new current check
        current_check = new_size
    return current_check


def sum_up_treasure(string):
    """5e random dungeons can end up having lots of little currency amounts"""
    if data['settings']['infest'] == "dnd_5e":
        currency = {}
        currency_list = string.split(";")
        for amount in currency_list:
            amount = amount.split(" ")
            # build list of amounts of specific types of coin
            currency.setdefault(amount[2].strip(), []).append(int(amount[1].strip()))
        result = ""
        for coin_type, values in currency.items():
            # build list of totals and coin type (string)
            result += (f"{sum(values)} {str(coin_type)}, ")
        return f"{str(result[:-2]).replace(',;', ',')}\n"
    return None


# add magical items to list
def add_magical_items_to_list(string):
    """ compiles ref table for magic items - 5e only """
    if data['settings']['infest'] == "dnd_5e":
        raw_magic_items = string.split(',')
        for index, raw_magic_item in enumerate(raw_magic_items):
            if 'dmg' in raw_magic_item:
                if ' x ' in raw_magic_items[index - 1]:
                    singular_item = raw_magic_items[index - 1].split(' x ')
                    magic_items[singular_item[1].strip()] = raw_magic_item.strip().replace(')', '').replace(' ', ' p.')
                else:
                    magic_items[raw_magic_items[index - 1].strip()] = raw_magic_item.strip().replace(')', '').replace(' ', ' p.')


def add_monsters_to_monster_list(string):
    """ compiles ref table for monsters - 4e and 5e only """
    if data['settings']['infest'] == "dnd_5e":
        #get monster name and book details and add to list
        monsters_and_combat = string.split(';')
        monsters = monsters_and_combat[0].split(' and ')
        for monster in monsters:
            if ' x ' in monster:
                monster = monster.split(' x ')[1]
                monster_list.append(monster.strip())
            else:
                monster_list.append(monster.strip())
        # get combat type and add to list
        combat = monsters_and_combat[1].split(',')
        combat_list.append(combat[0].strip())
        # get xp amount and add to list
        xp_amount = combat[1].strip().split(' ')
        xp_list.append(xp_amount[0].strip())
    if data['settings']['infest'] == "dnd_4e":
        #get monster name and book details and add to list
        monsters = string.split(') and ')
        for monster in monsters:
            if ' x ' in monster:
                monster = monster.split(' x ')[1]
                monster = monster.strip().split(',')
                monster_list.append(monster[0])
            else:
                monster = monster.strip().split(',')
                monster_list.append(monster[0])


def extract_book_details(details):
    """ split out name and source book(s) (used on monster list) - 5e and 4e only"""
    if data['settings']['infest'] == "dnd_5e":
        split = details.split('(')
        name = split[0].strip()
        details = split[1].split(',')
        book = details[1].strip().replace(')','').replace(' ', ' p.')
        if len(details) > 2:
            book = f"{book} / {details[2].strip().replace(')','').replace(' ', ' p.')}"
        return name, book
    if data['settings']['infest'] == "dnd_4e":
        split = details.split('(')
        name = split[0].strip()
        book = split[1].strip().replace(' ', ' p.')
        return name, book
    return None


# globals
xp_list = []
monster_list = []
combat_list = []
magic_items = {}
newline = '\n'


# set up command line parser
parser = argparse.ArgumentParser(
                    prog = 'Donjon to Homebrewery',
                    description = 'Converts donjon random dungeons into v3 homebrewery text to copy and paste.',
                    epilog = 'See README for more details.')

parser.add_argument('filename') # required
parser.add_argument('-gm', '--gm_map', help='URL for the GM Map image') # optional
parser.add_argument('-p', '--player_map', help='URL for the Player map image') # optional
parser.add_argument('-o', '--output_filename', help='Override for text filename', default="homebrewery.txt") # optional

args = parser.parse_args()

# opening JSON file
filename = args.filename
f = open(filename, encoding="utf-8")

# returns JSON object as a dictionary
data = json.load(f)

# Open file to write content to
with open(args.output_filename, "w", encoding="utf-8") as outfile:

    # title page
    if args.gm_map:
        outfile.write(f"![map]({args.gm_map}){{position:absolute;mix-blend-mode:color-burn;transform:rotate(-30deg);width:500%;top:-1000px;}}\n")

    outfile.write("{{margin-top:225px}}\n")
    outfile.write("{{wide,background-color:white,border-width:10px,border-radius:20px,padding:10px,margin-left:-10px\n")
    outfile.write(f"# {data['settings']['name']}\n")

    # certain dungeon generators don't create a blurb
    if "history" in data['details']:
        outfile.write(":\n")
        outfile.write(f"##### {data['details']['history']}\n")
        outfile.write(":::\n")
    else:
        outfile.write(":::\n")

    # work out ruleset for title page and if we can generate summary page
    if data['settings']['infest'] == "dnd_5e":
        infest = "D&D 5e"
        summary_page = True
    elif data['settings']['infest'] == "dnd_4e":
        infest = "D&D 4e"
        summary_page = True
    elif data['settings']['infest'] == "adnd":
        infest = "AD&D"
        summary_page = False
    else:
        infest = "fantasy"
        summary_page = False

    outfile.write(f"##### A randomly generated {infest} donjon dungeon for a party size of {data['settings']['n_pc']} and APL{data['settings']['level']}\n")
    outfile.write(":::\n")
    outfile.write("##### Created using [Homebrewery](https://homebrewery.naturalcrit.com), [Donjon](https://donjon.bin.sh) and [donjon_to_homebrewery](https://github.com/telboy007/donjon_to_homebrewery)\n")
    outfile.write("}}\n")
    outfile.write("\\page\n")
    outfile.write("{{pageNumber,auto}}\n")

    # map pages
    if args.gm_map:
        outfile.write("## GM Map\n")
        outfile.write(f"![map]({args.gm_map}){{width:680px;}}\n")
        outfile.write("Courtesy of <a href=\"https://donjon.bin.sh\">donjon.bin.sh</a>\n")
        outfile.write("{{footnote MAPS}}\n")
        outfile.write("\\page\n")
        outfile.write("{{pageNumber,auto}}\n")

    if args.player_map:
        outfile.write("## Player Map\n")
        outfile.write(f"![map]({args.player_map}){{width:680px;}}\n")
        outfile.write("Courtesy of <a href=\"https://donjon.bin.sh\">donjon.bin.sh</a>\n")
        outfile.write("{{footnote MAPS}}\n")
        outfile.write("\\page\n")
        outfile.write("{{pageNumber,auto}}\n")

    # general features
    outfile.write("## Description\n")
    outfile.write("The dungeon has the following features, these may include skill checks to perform certain actions.\n")
    outfile.write("{{descriptive\n")
    outfile.write("#### General Features\n")
    outfile.write("| Type | Detail |\n")
    outfile.write("|:--|:--|\n")
    outfile.write(f"| Floors | {data['details']['floor']} |\n")
    outfile.write(f"| Walls | {data['details']['walls']} |\n")
    outfile.write(f"| Temperature | {data['details']['temperature'].replace(newline, ' ')} |\n")
    outfile.write(f"| Lighting | {data['details']['illumination']} |\n")
    if "special" in data['details']:
        if data['details']['special'] is not None:
            outfile.write(f"| Special | {data['details']['special'].replace(newline, ' ')} |\n")
        else:
            outfile.write(f"| Special | {data['details']['special']} |\n")
    outfile.write("}}\n")

    # corridor features - caves don't have corridor features
    if "corridor_features" in data:
        outfile.write("Some of the corridors marked on the map have special features detailed below.\n")
        outfile.write("{{descriptive\n")
        outfile.write("#### Corridor Features\n")
        outfile.write("| Type | Detail |\n")
        outfile.write("|:--|:--|\n")

        for key, val in data["corridor_features"].items():
            outfile.write(f"| {val['key']} | {val['detail'].replace(newline, ' ')} |\n")

        outfile.write("}}\n")

    # wandering monsters - certain dungeon outfit types don't have one
    if "wandering_monsters" in data:
        outfile.write("## Random Encounters\n")

        outfile.write("There are also roaming groups with specific goals, this will help you place them in the dungeon or when the party encounter them.\n")
        outfile.write("{{classTable,frame\n")
        outfile.write("#### Wandering Monsters\n")
        outfile.write("| Roll | Detail |\n")
        outfile.write("|:--|:--|\n")

        for key, val in data["wandering_monsters"].items():
            outfile.write(f"| {key} | {val.replace(newline, ' ')} |\n")
            # add to the monster list for the summary page
            add_monsters_to_monster_list(val.replace(newline, ' '))

        outfile.write("}}\n")

    # end description page
    outfile.write("{{footnote OVERVIEW}}\n")
    outfile.write("\\page\n")
    outfile.write("{{pageNumber,auto}}\n")

# set page marker check
check = set_check()

with open(args.output_filename, "a", encoding="utf-8") as outfile:

    # locations
    outfile.write("## Locations\n")

    # certain dungeon generators don't provide entrance information
    # or there are multiple entrances
    if "egress" in data:
        outfile.write("### Getting In\n")
        if len(data["egress"]) == 1:
            outfile.write("There is only one entrance into the dungeon:\n")
        else:
            outfile.write("There are multiple entrances into the dungeon:\n")
        for egress in data["egress"]:
            # caves don't have a type the entrance leads into
            if "type" in egress:
                outfile.write(f"* On the GM map at ***row: {egress['row']}*** and ***column: {egress['col']}***, which enters the {egress['type']} from the {egress['dir']}.\n")
            else:
                outfile.write(f"* On the GM map at ***row: {egress['row']}*** and ***column: {egress['col']}***, which enters from the {egress['dir']}.\n")
        outfile.write("\n")

    # rooms
    if "rooms" in data:
        for rooms in data["rooms"]:
            if rooms is None:
                continue
            outfile.write(f"### Room {rooms['id']}\n")
            outfile.write(":\n")

            # check for page marker
            outfile.close()
            check = file_size(check)
            outfile = open(args.output_filename, "a", encoding="utf-8")

            if "contents" in rooms:
                if "detail" in rooms["contents"]:

                    # traps
                    if "trap" in rooms["contents"]["detail"]:
                        outfile.write("{{classTable,frame\n")
                        outfile.write("#### Trap!\n")
                        for item in rooms["contents"]["detail"]["trap"]:
                            desc = item.replace("\n","")
                            outfile.write(f"* {desc}\n")

                        outfile.write("}}\n")

                    # check for page marker
                    outfile.close()
                    check = file_size(check)
                    outfile = open(args.output_filename, "a", encoding="utf-8")

                    # hidden treasure
                    if "hidden_treasure" in rooms["contents"]["detail"]:
                        outfile.write("{{classTable,frame\n")
                        outfile.write("#### Hidden Treasure!\n")
                        for item in rooms["contents"]["detail"]["hidden_treasure"]:
                            if item == "--":
                                continue
                            outfile.write(f"* {item.replace(newline,' ')}\n")
                            # add to magic items list for the summary page
                            add_magical_items_to_list(item.replace(newline,' '))

                        outfile.write("}}\n")

                    # check for page marker
                    outfile.close()
                    check = file_size(check)
                    outfile = open(args.output_filename, "a", encoding="utf-8")

                    # room description
                    if "room_features" in rooms["contents"]["detail"]:
                        outfile.write("{{note\n")
                        outfile.write(f"{rooms['contents']['detail']['room_features']}.\n")
                        outfile.write("}}\n")
                    else:
                        outfile.write("{{note\n")
                        outfile.write("Empty.\n")
                        outfile.write("}}\n")

                    # check for page marker
                    outfile.close()
                    check = file_size(check)
                    outfile = open(args.output_filename, "a", encoding="utf-8")

                    # monsters and treasure
                    if "monster" in rooms["contents"]["detail"]:
                        for thing in rooms["contents"]["detail"]["monster"]:
                            if thing == "--":
                                continue
                            if thing.startswith("Treasure"):
                                outfile.write(":\n")
                                outfile.write("{{descriptive\n")
                                outfile.write("#### Treasure\n")
                                if thing.count("(") == 0:
                                    thing = sum_up_treasure(thing.replace(",",";"))
                                    outfile.write(f"{thing}\n")
                                else:
                                    outfile.write(f"{thing.replace(newline, ' ').replace('Treasure: ','')}\n")
                                    # add to magic items list for the summary page
                                    add_magical_items_to_list(thing.replace(newline, ' ').replace('Treasure: ',''))
                                outfile.write("}}\n")
                            else:
                                outfile.write("\n")
                                outfile.write(f"This room is occupied by **{thing}**\n")
                                # add to the monster list for the summary page
                                add_monsters_to_monster_list(thing)

                    # check for page marker
                    outfile.close()
                    check = file_size(check)
                    outfile = open(args.output_filename, "a", encoding="utf-8")

                else:
                    # no details
                    outfile.write("{{note\n")
                    outfile.write("Empty.\n")
                    outfile.write("}}\n")

                # check for page marker
                outfile.close()
                check = file_size(check)
                outfile = open(args.output_filename, "a", encoding="utf-8")

            # exits
            if "doors" in rooms:
                outfile.write("#### Exits\n")
                outfile.write("| Direction | Description | Leads to |\n")
                outfile.write("|:--|:--|:--|\n")

                for direction, door in rooms["doors"].items():
                    for d in door:
                        DESC = ""
                        if d["type"] == "secret":
                            if "trap" in d:
                                DESC += f" ***Secret:*** {d['secret'].replace(newline, ' ')} ***Trap:*** {d['trap'].replace(newline, ' ')}"
                            else:
                                DESC += f"***Secret:*** {d['secret'].replace(newline, ' ')}"
                        if d["type"] == "trapped":
                            if "trap" in d:
                                DESC += f" ***Trap:*** {d['trap'].replace(newline, ' ')}"
                            else:
                                DESC += " ***Trap***: Already disarmed."
                        if "out_id" in d:
                            outfile.write(f"| {direction} | {d['desc']} {DESC} | {d['out_id']} |")
                        else:
                            outfile.write(f"| {direction} | {d['desc']} {DESC} | n/a |")
                        outfile.write("\n")

                outfile.write(":\n")

            # check for page marker
            outfile.close()
            check = file_size(check)
            outfile = open(args.output_filename, "a", encoding="utf-8")

    # end locations section and prepare for summary
    # end description page
    outfile.write("{{footnote LOCATIONS}}\n")

    # if 4th or 5th edition then create a summary page
    if summary_page:
        outfile.write("\\page\n")
        outfile.write("{{pageNumber,auto}}\n")

        # summary
        outfile.write("## Summary\n")
        outfile.write("Here you will find useful reference tables for things encountered in the dungeon.\n")

        # list out xp and combat type details if 5e dungeon
        if data['settings']['infest'] == "dnd_5e":
            outfile.write("{{descriptive\n")
            outfile.write("#### Combat details\n")

            # work out some xp totals
            total_xp = sum(int(i) for i in xp_list)
            shared_xp = round(sum(int(i) for i in xp_list)/int(data['settings']['n_pc']))

            outfile.write(f"**Total XP: {total_xp}** which is {shared_xp} xp per party member.\n")
            outfile.write("| Type | Amount |\n")
            outfile.write("|:--|:--|\n")
            outfile.write(f"| Easy | {combat_list.count('easy')} |\n")
            outfile.write(f"| Medium | {combat_list.count('medium')} |\n")
            outfile.write(f"| Hard | {combat_list.count('hard')} |\n")
            outfile.write(f"| Deadly | {combat_list.count('deadly')} |\n")
            outfile.write("}}\n")
            outfile.write(":\n")

        # list out monsters in a handy reference table
        outfile.write("{{descriptive\n")
        outfile.write("#### Monster List (alphabetical)\n")
        outfile.write("| Monster | Book |\n")
        outfile.write("|:--|:--|\n")

        # but first dedupe and order monster list
        monster_list = list(dict.fromkeys(monster_list))
        monster_list.sort()

        for monster in monster_list:
            # split out monster and source book details
            monster, sourcebook = extract_book_details(monster)
            outfile.write(f"| {monster} | {sourcebook} |\n")

        outfile.write("}}\n")
        outfile.write(":\n")

        # list out magic items for 5th edition
        if data['settings']['infest'] == "dnd_5e":
            outfile.write("{{descriptive\n")
            outfile.write("#### Magic Items (alphabetical)\n")
            outfile.write("| Item | Book |\n")
            outfile.write("|:--|:--|\n")
            ordered_magic_items = OrderedDict(sorted(magic_items.items()))

            for magic_item, sourcebook in ordered_magic_items.items():
                # split out item and source book details
                outfile.write(f"| {magic_item}) | {sourcebook} |\n")

            outfile.write("}}\n")

        # final footnote
        outfile.write("{{footnote SUMMARY}}\n")

    # donjon settings
    outfile.write("\\page\n")
    outfile.write("{{pageNumber,auto}}\n")

    outfile.write("{{wide\n")
    outfile.write("## Settings\n")
    outfile.write("Settings used to create this dungeon:\n")
    outfile.write(":\n")
    outfile.write(f"{infest} Random Dungeon Generator\n")
    outfile.write("|||\n")
    outfile.write("|:--|:--|\n")
    outfile.write(f"|Dungeon Name|{data['settings']['name']}|\n")
    outfile.write(f"|Dungeon Level|{data['settings']['level']}|\n")
    outfile.write(f"|Party Size|{data['settings']['n_pc']}|\n")
    outfile.write(f"|Motif|{data['settings']['motif']}|\n")
    outfile.write("}}\n")
    outfile.write(":\n")
    outfile.write("|||\n")
    outfile.write("|:--|:--|\n")
    outfile.write(f"|Random Seed:|{data['settings']['seed']}|\n")
    outfile.write(f"|Dungeon Size:|{data['settings']['dungeon_size']}|\n")
    outfile.write(f"|Dungeon Layout:|{data['settings']['dungeon_layout']}|\n")
    outfile.write(f"|Peripheral Egress?|{data['settings']['peripheral_egress']}|\n")
    outfile.write(f"|Room Layout:|{data['settings']['room_layout']}|\n")
    outfile.write(f"|Room Size:|{data['settings']['room_size']}|\n")
    outfile.write(f"|Polymorph Rooms?|{data['settings']['room_polymorph']}|\n")
    outfile.write(f"|Doors:|{data['settings']['door_set']}|\n")
    outfile.write(f"|Corridors:|{data['settings']['corridor_layout']}|\n")
    outfile.write(f"|Remove Deadends?|{data['settings']['remove_deadends']}|\n")
    outfile.write(f"|Stairs?|{data['settings']['add_stairs']}|\n")
    outfile.write(f"|Map Style:|{data['settings']['map_style']}|\n")
    outfile.write(f"|Grid|{data['settings']['grid']}|\n")

    outfile.write("\\column\n")

    if args.gm_map:
        outfile.write(":\n")
        outfile.write(f"![map]({args.gm_map}){{width:50%;}}\n")
        outfile.write(":\n")
        outfile.write("Courtesy of <a href=\"https://donjon.bin.sh\">donjon.bin.sh</a>\n")

    outfile.write("{{footnote SETTINGS}}\n")

    outfile.close()
