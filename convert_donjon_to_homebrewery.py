#!/usr/bin/env python

"""
    Donjon to homebrewery convertor
    line arguments:
        json file
        image url (imgur, etc)
"""

import json
import sys


# set check value
def set_check(check):
    """Count the number of characters in a file"""
    infile = open("homebrewery.txt", "r")
    data = infile.read()
    infile.close()
    return len(data)


# add a page marker check
def file_size(check):
    """Count the number of characters in a file"""
    infile = open("homebrewery.txt", "r")
    data = infile.read()
    infile.close()
    if (len(data) - check) > 2450:
        outfile = open("homebrewery.txt", "a")
        outfile.write("\\page\n")
        outfile.close()
        return len(data)
    return check


# can we add up all the random little amounts of money? yes we can!
def sum_up_treasure(string):
    currency = {}
    list = string.split(";")
    for amount in list:
        amount = amount.split(" ")
        # build list of amounts of specific types of coin
        currency.setdefault(amount[2].strip(), []).append(int(amount[1].strip()))
    result = ""
    for coinType, values in currency.items():
        # build list of totals and coin type (string)
        result += (f"{sum(values)} {str(coinType)}, ")
    return f"{str(result[:-2]).replace(',;', ',')}\n"


# add monsters to monster list
def add_monsters_to_monster_list(thing):
    monsters = thing.split(';')
    monster = monsters[0].split(' and ')
    for mon in monster:
        try:
            m = mon.split(' x ')[1]
            monster_list.append(m.strip())
        except:
            monster_list.append(mon.strip())


# split our monster name and source book
def split_monster_details(monster_details):
    split = monster_details.split('(')
    monster = split[0].strip()
    details = split[1].split(',')
    book = details[1].strip().replace(')','').replace(' ', ' p.')
    return monster, book 


# globals
check = 0
monster_list = []
newline = '\n'

# opening JSON file
try:
    filename = sys.argv[1]
    f = open(filename)

    # returns JSON object as a dictionary
    data = json.load(f)
except:
    print("Please supply json filename to convert.")
    sys.exit()

# Open file to write content to
outfile = open("homebrewery.txt", "w")

# title page
if len(sys.argv) == 3:
    outfile.write(f"![map]({sys.argv[2]}){{position:absolute;mix-blend-mode:color-burn;transform:rotate(-30deg);width:500%;top:-1000px;}}\n")
    outfile.write(":\n")

outfile.write("{{margin-top:225px}}\n")
outfile.write(f"# {data['settings']['name']}\n")
outfile.write("{{margin-top:25px}}\n")
outfile.write("{{wide\n")

# certain dungeon generators don't create a blurb
try:
    outfile.write(f"##### {data['details']['history']}\n")
    outfile.write("::\n")
except:
    outfile.write("::\n")

# work out ruleset for title page
if data['settings']['infest'] == "dnd_5e":
    infest = "D&D 5e"
elif data['settings']['infest'] == "dnd_4e":
    infest = "D&D 4e"
elif data['settings']['infest'] == "adnd":
    infest = "AD&D"
else:
    infest = "fantasy"

outfile.write(f"##### A randomly generated {infest} donjon dungeon for a party size of {data['settings']['n_pc']} and APL{data['settings']['level']}\n")
outfile.write("::::\n")
outfile.write("##### Created using [Homebrewery](https://homebrewery.naturalcrit.com), [Donjon](https://donjon.bin.sh) and [donjon_to_homebrewery](https://github.com/telboy007/donjon_to_homebrewery)\n")
outfile.write("}}\n")
outfile.write("\\page\n")

# map page
if len(sys.argv) == 3:
    outfile.write("## GM Map\n")
    outfile.write(f"![map]({sys.argv[2]}){{width:680px;}}\n")
    outfile.write("Courtesy of <a href=\"https://donjon.bin.sh\">donjon.bin.sh</a>\n")
    outfile.write("\\page\n")

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
    if data['details']['special'] != None:
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

# set page marker check
outfile.close()
check = set_check(check)
outfile = open("homebrewery.txt", "a")

# end description page
outfile.write("\\page\n")

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
    outfile.write(":\n")

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
        outfile = open("homebrewery.txt", "a")

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
                outfile = open("homebrewery.txt", "a")

                # hidden treasure
                if "hidden_treasure" in rooms["contents"]["detail"]:
                    outfile.write("{{classTable,frame\n")
                    outfile.write("#### Hidden Treasure!\n")
                    for item in rooms["contents"]["detail"]["hidden_treasure"]:
                        if item == "--":
                            continue
                        outfile.write(f"* {item.replace(newline,' ')}\n")

                    outfile.write("}}\n")

                # check for page marker
                outfile.close()
                check = file_size(check)
                outfile = open("homebrewery.txt", "a")

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
                outfile = open("homebrewery.txt", "a")

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
                            outfile.write("}}\n")
                        else:
                            outfile.write("::\n")
                            outfile.write(f"This room is occupied by **{thing}**\n")
                            # add to the monster list for the summary page
                            add_monsters_to_monster_list(thing)

                # check for page marker
                outfile.close()
                check = file_size(check)
                outfile = open("homebrewery.txt", "a")

            else:
                # no details
                outfile.write("{{note\n")
                outfile.write("Empty.\n")
                outfile.write("}}\n")

            # check for page marker
            outfile.close()
            check = file_size(check)
            outfile = open("homebrewery.txt", "a")

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
        outfile = open("homebrewery.txt", "a")

# end locations section and prepare for summary
outfile.write("\\page\n")

# summary
outfile.write("## Summary\n")
outfile.write("You will find here useful reference tables for things encountered in the dungeon.\n")

# list out monsters in a handy reference table
outfile.write("{{descriptive\n")
outfile.write("#### Monster List (alphabetical)\n")
outfile.write("| Detail | Book |\n")
outfile.write("|:--|:--|\n")

# but first dedupe and order monster list
monster_list = list(dict.fromkeys(monster_list))
monster_list.sort()

for monster in monster_list:
    # split out monster and source book details
    monster, book = split_monster_details(monster)
    outfile.write(f"| {monster} | {book} |\n")

outfile.write("}}\n")

# done
outfile.close()
