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
import openai
import os
import requests
from collections import OrderedDict
from dotenv import load_dotenv

load_dotenv()


def set_check():
    """Set the initial number of characters in the file"""
    with open(args.output_filename, "r", encoding="utf-8") as readonly_file:
        return len(readonly_file.read())


def file_size(current_check, footnote):
    """Count the current number of characters in a file"""
    with open(args.output_filename, "r", encoding="utf-8") as readonly_file:
        new_size = len(readonly_file.read())
    if (new_size - current_check) > 2450:
        with open(args.output_filename, "a", encoding="utf-8") as append_file:
            append_file.write("{{footnote {footnote}}}\n")
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


def add_magical_items_to_list(string, room_loc):
    """ 
        compiles ref table for magic items - 5e only 
        format: magic_item[name (quantity if applicable)] = dmg page number/room location id    
    """
    if data['settings']['infest'] == "dnd_5e":
        raw_magic_items = string.split(',')
        for index, raw_magic_item in enumerate(raw_magic_items):
            if 'dmg' in raw_magic_item:
                item_name = format_magic_item_name(raw_magic_items[index - 1])
                magic_items[item_name] = f"{raw_magic_item.strip().replace(')', '').replace(' ', ' p.')}/{room_loc}"


def format_magic_item_name(item_name):
    """ nicely format magic item names """
    if ' x ' in item_name:
        singular_item = item_name.split(' x ')
        item_name = f"{singular_item[1].strip()} ({singular_item[0].strip()})"

    return item_name.replace('(uncommon','**U**').replace('(common','**C**').replace('(rare', '**R**').replace('(very rare', '**VR**').replace('(legendary', '**L**').replace('(artifact', '**A**').strip()


def add_monsters_to_monster_list(string):
    """ compiles ref table for monsters - 4e and 5e only """
    if data['settings']['infest'] == "dnd_5e":
        # get monster name and book details and add to list
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
        # get monster name and book details and add to list
        monsters = string.split(') and ')
        for monster in monsters:
            if ' x ' in monster:
                monster = monster.split(' x ')[1]
                monster = monster.strip().split(',')
                monster_list.append(monster[0])
            else:
                monster = monster.strip().split(',')
                monster_list.append(monster[0])


def extract_book_details(book_details):
    """ split out name and source book(s) (used on monster list) - 5e and 4e only"""
    if data['settings']['infest'] == "dnd_5e":
        split = book_details.split('(')
        name = split[0].strip()
        book_details = split[1].split(',')
        book = book_details[1].strip().replace(')','').replace(' ', ' p.')
        if len(book_details) > 2:
            book = f"{book} / {book_details[2].strip().replace(')','').replace(' ', ' p.')}"
        return name, book
    if data['settings']['infest'] == "dnd_4e":
        split = book_details.split('(')
        name = split[0].strip()
        book = split[1].strip().replace(' ', ' p.')
        return name, book
    return None


def request_monster_statblock(monster_name):
    """ make request to dnd5e api to get json formatted monster statblock """
    url = f"https://www.dnd5eapi.co/api/monsters/{monster_name}"
    x = requests.get(url)

    if x.status_code == 200:
        return x.json()
    return "not found"


def get_ability_modifier(int):
    """ calculate ability modifier """
    if round((int - 10.1) / 2) < 0:
        return round((int - 10.1) / 2)
    return f"+{round((int - 10.1) / 2)}"


def extract_proficiencies_from_api_response(json):
    """ extract the saving throw and skill check information """
    saving_throws = []
    skill_checks = []
    
    if "proficiencies" in json:
        for proficiency in json['proficiencies']:
            proficiency_name = proficiency['proficiency']['name']
            value = proficiency['value']

            if proficiency_name.startswith("Saving Throw"):
                saving_throw_name = proficiency_name.split(':')[1].strip()
                saving_throws.append((saving_throw_name, value))
            elif proficiency_name.startswith("Skill"):
                skill_check_name = proficiency_name.split(':')[1].strip()
                skill_checks.append((skill_check_name, value))

    return saving_throws, skill_checks


def expand_dungeon_overview_via_ai(blurb, dungeon_details):
    openai.api_key = os.getenv("CHATGPT_TOKEN")
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": f"Expand on the description of a D&D 5e dungeon adding excitement, drama and suspense.  Only talk about details, sights and sounds of the dungeon's entrance and not inside.  Make no reference to skill checks or ft. (for reference the dungeon details are {dungeon_details}): {blurb}"}
        ]
    )
    print(completion.usage)
    return completion.choices[0].message["content"]


def suggest_a_bbeg_via_ai(expanded_description, dungeon_detail):
    openai.api_key = os.getenv("CHATGPT_TOKEN")
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": f"Based on the following text what D&D 5e monster should be the boss of the dungeons and what would their lair look like based on {dungeon_detail}: {expanded_description}"}
        ]
    )
    print(completion.usage)
    return completion.choices[0].message["content"]


# globals
xp_list = []
monster_list = []
monster_names = []
skipped_monsters = []
combat_list = []
magic_items = {}
NEWLINE = '\n'


# set up command line parser
parser = argparse.ArgumentParser(
                    prog = 'Donjon to Homebrewery',
                    description = 'Converts donjon random dungeons into v3 homebrewery text to copy and paste.',
                    epilog = 'See README for more details.')

parser.add_argument('filename') # required
parser.add_argument('-gm', '--gm_map', help='URL for the GM Map image') # optional
parser.add_argument('-p', '--player_map', help='URL for the Player map image') # optional
parser.add_argument('-o', '--output_filename', help='Override for text filename', default="homebrewery.txt") # optional
parser.add_argument('-t', '--testmode', help='Stops AI enhancing dungeon details')

args = parser.parse_args()

# grab json filename and convert json to dictionary
filename = args.filename
with open(filename, encoding="utf-8") as inputfile:
    data = json.load(inputfile)

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
        INFEST = "D&D 5e"
        SUMMARY_PAGE = True
    elif data['settings']['infest'] == "dnd_4e":
        INFEST = "D&D 4e"
        SUMMARY_PAGE = True
    elif data['settings']['infest'] == "adnd":
        INFEST = "AD&D"
        SUMMARY_PAGE = False
    else:
        INFEST = "fantasy"
        SUMMARY_PAGE = False

    outfile.write(f"##### A randomly generated {INFEST.upper()} donjon dungeon for a party size of {data['settings']['n_pc']} and APL{data['settings']['level']}\n")
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

    # use AI to expand on the dungeon description and provide other details if not running under testmode
    if not args.testmode or not INFEST == "fantasy":
        dungeon_detail = f"The floors are {data['details']['floor']}, the walls are {data['details']['walls']}, the temperature is {data['details']['temperature'].replace(NEWLINE, ' ')}, and the temperature is {data['details']['illumination']}."
        blurb = expand_dungeon_overview_via_ai(data['details']['history'], dungeon_detail)
        outfile.write("## Description\n")
        outfile.write(f"{blurb}\n")

    # general features
    outfile.write("## Features\n")
    outfile.write("The dungeon has the following features, these may include skill checks to perform certain actions.\n")
    outfile.write("{{descriptive\n")
    outfile.write("#### General Features\n")
    outfile.write("| Type | Detail |\n")
    outfile.write("|:--|:--|\n")
    outfile.write(f"| Floors | {data['details']['floor']} |\n")
    outfile.write(f"| Walls | {data['details']['walls']} |\n")
    outfile.write(f"| Temperature | {data['details']['temperature'].replace(NEWLINE, ' ')} |\n")
    outfile.write(f"| Lighting | {data['details']['illumination']} |\n")
    if "special" in data['details']:
        if data['details']['special'] is not None:
            outfile.write(f"| Special | {data['details']['special'].replace(NEWLINE, ' ')} |\n")
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
            outfile.write(f"| {val['key']} | {val['detail'].replace(NEWLINE, ' ')} |\n")

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
            outfile.write(f"| {key} | {val.replace(NEWLINE, ' ')} |\n")
            # add to the monster list for the summary page
            add_monsters_to_monster_list(val.replace(NEWLINE, ' '))

        outfile.write("}}\n")

    # use AI to suggest a BBEG and lair detail if not running under testmode
    if not args.testmode or not INFEST == "fantasy":
        bbeg_and_lair = suggest_a_bbeg_via_ai(blurb, dungeon_detail)
        outfile.write("## Dungeon Boss\n")
        outfile.write(f"{bbeg_and_lair}  Pick a suitable location on the map to place the boss and it's lair.\n")

    # end description page
    outfile.write("{{footnote OVERVIEW}}\n")
    outfile.write("\\page\n")
    outfile.write("{{pageNumber,auto}}\n")

# set page marker check
check = set_check()

with open(args.output_filename, "a", encoding="utf-8") as outfile:

    """ DUNGEON DETAILS """

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

    """ LOCATION DETAILS """

    # rooms
    if "rooms" in data:
        for rooms in data["rooms"]:
            if rooms is None:
                continue
            outfile.write(f"### Room {rooms['id']}\n")
            outfile.write(":\n")

            # check for page marker
            outfile.close()
            check = file_size(check, "LOCATIONS")
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
                    check = file_size(check, "LOCATIONS")
                    outfile = open(args.output_filename, "a", encoding="utf-8")

                    # hidden treasure
                    if "hidden_treasure" in rooms["contents"]["detail"]:
                        outfile.write("{{classTable,frame\n")
                        outfile.write("#### Hidden Treasure!\n")
                        for item in rooms["contents"]["detail"]["hidden_treasure"]:
                            if item == "--":
                                continue
                            outfile.write(f"* {item.replace(NEWLINE,' ')}\n")
                            # add to magic items list for the summary page
                            add_magical_items_to_list(item.replace(NEWLINE,' '), rooms['id'])

                        outfile.write("}}\n")

                    # check for page marker
                    outfile.close()
                    check = file_size(check, "LOCATIONS")
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
                    check = file_size(check, "LOCATIONS")
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
                                    outfile.write(f"{thing.replace(NEWLINE, ' ').replace('Treasure: ','')}\n")
                                    # add to magic items list for the summary page
                                    add_magical_items_to_list(thing.replace(NEWLINE, ' ').replace('Treasure: ',''), rooms['id'])
                                outfile.write("}}\n")
                            else:
                                outfile.write("\n")
                                outfile.write(f"This room is occupied by **{thing}**\n")
                                # add to the monster list for the summary page
                                add_monsters_to_monster_list(thing)

                    # check for page marker
                    outfile.close()
                    check = file_size(check, "LOCATIONS")
                    outfile = open(args.output_filename, "a", encoding="utf-8")

                else:
                    # no details
                    outfile.write("{{note\n")
                    outfile.write("Empty.\n")
                    outfile.write("}}\n")

                # check for page marker
                outfile.close()
                check = file_size(check, "LOCATIONS")
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
                                DESC += f" ***Secret:*** {d['secret'].replace(NEWLINE, ' ')} ***Trap:*** {d['trap'].replace(NEWLINE, ' ')}"
                            else:
                                DESC += f"***Secret:*** {d['secret'].replace(NEWLINE, ' ')}"
                        if d["type"] == "trapped":
                            if "trap" in d:
                                DESC += f" ***Trap:*** {d['trap'].replace(NEWLINE, ' ')}"
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
            check = file_size(check, "LOCATIONS")
            outfile = open(args.output_filename, "a", encoding="utf-8")

    # end locations section and prepare for summary
    outfile.write("{{footnote LOCATIONS}}\n")

    """ SUMMARY PAGE """

    # if 4th or 5th edition then create a summary page
    if SUMMARY_PAGE:
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

        for item in monster_list:
            # split out monster and source book details
            monster_name, sourcebook = extract_book_details(item)
            outfile.write(f"| {monster_name} | {sourcebook} |\n")

            # compile list of monsters for stat blocks
            if "mm" in sourcebook:
                monster_names.append(monster_name.lower().replace(" ", "-"))
            else:
                skipped_monsters.append(monster_name.replace("{{", "").replace("}}.", ""))

        outfile.write("}}\n")
        outfile.write(":\n")

        # list out magic items for 5th edition
        if data['settings']['infest'] == "dnd_5e":
            outfile.write("{{descriptive\n")
            outfile.write("#### Magic Items (alphabetical)\n")
            outfile.write("| Item | Book | Room |\n")
            outfile.write("|:--|:--|--:|\n")
            ordered_magic_items = OrderedDict(sorted(magic_items.items()))

            for magic_item, details in ordered_magic_items.items():
                # split out location and source book details
                sourcebook, location = details.split('/')
                outfile.write(f"| {magic_item} | {sourcebook} | {location} |\n")

            outfile.write("}}\n")

        # final footnote
        outfile.write("{{footnote SUMMARY}}\n")

    """ STAT BLOCKS """

    # if 5th edition try to get as many monster stat blocks as possible
    if data['settings']['infest'] == "dnd_5e":
        outfile.write("\\page\n")
        outfile.write("{{pageNumber,auto}}\n")
        outfile.write("# Stat Blocks (SRD only)\n")

        for monster in monster_names:
            monster_statblock = request_monster_statblock(monster)

            # check for any monsters listed as in monster manual but not found in api
            if monster_statblock == "not found": 
                skipped_monsters.append(monster.replace("-", " ").title())
                continue

            # write out statblock if monster found
            outfile.write("{{monster,frame\n")
            outfile.write(f"## {monster_statblock['name'].capitalize()}\n")
            outfile.write(f"*{monster_statblock['size'].capitalize()} {monster_statblock['type'].capitalize()}, {monster_statblock['alignment'].title()}*\n")
            outfile.write("___\n")
            outfile.write(f"**Armor Class** :: {monster_statblock['armor_class'][0]['value']} ")

            # handle monsters with more than one armor type (i.e. they have a shield as well)
            if "type" in monster_statblock['armor_class'][0]:
                outfile.write(f"{monster_statblock['armor_class'][0]['type']}\n")
            else:
                outfile.write(f"{monster_statblock['armor_class'][0]['armor'][0]['name']})\n")
            outfile.write(f"**Hit Points** :: {monster_statblock['hit_points']} ({monster_statblock['hit_points_roll']})\n")

            # handle additional movement types
            if len(monster_statblock['speed']) > 1:
                movement_types = []
                for key, value in monster_statblock['speed'].items():
                    movement_types.append(f"{key.capitalize()} {value}")
                strMovement = ', '.join(movement_types)
                outfile.write(f"**Speed** :: {strMovement.replace('Walk ', '')}\n")
            else:
                outfile.write(f"**Speed** :: {monster_statblock['speed']['walk']}\n")

            outfile.write("___\n")
            outfile.write("|STR|DEX|CON|INT|WIS|CHA|\n")
            outfile.write("|:---:|:---:|:---:|:---:|:---:|:---:|\n")
            outfile.write(f"|{monster_statblock['strength']} ({get_ability_modifier(monster_statblock['strength'])})")
            outfile.write(f"|{monster_statblock['dexterity']} ({get_ability_modifier(monster_statblock['dexterity'])})")
            outfile.write(f"|{monster_statblock['constitution']} ({get_ability_modifier(monster_statblock['constitution'])})")
            outfile.write(f"|{monster_statblock['intelligence']} ({get_ability_modifier(monster_statblock['intelligence'])})")
            outfile.write(f"|{monster_statblock['wisdom']} ({get_ability_modifier(monster_statblock['wisdom'])})")
            outfile.write(f"|{monster_statblock['charisma']} ({get_ability_modifier(monster_statblock['charisma'])})|\n")
            outfile.write("___\n")

            # extract saving throws and skill check modifiers
            saving_throws, skill_checks = extract_proficiencies_from_api_response(monster_statblock)
            if saving_throws:
                throws = []
                for key, value in saving_throws:
                    throws.append(f"{key.capitalize()} +{value}")
                strThrows = ', '.join(throws)
                outfile.write(f"**Saving Throws** :: {strThrows}\n")

            if skill_checks:
                skills = []
                for key, value in skill_checks:
                    skills.append(f"{key.capitalize()} +{value}")
                strSkills = ', '.join(skills)
                outfile.write(f"**Skills** :: {strSkills}\n")

            #resistances and immunities
            if monster_statblock["damage_vulnerabilities"]:
                dmg_vul = ', '.join(monster_statblock["damage_vulnerabilities"])
                outfile.write(f"**Damage Vulnerabilities** :: {dmg_vul}\n")

            if monster_statblock["damage_resistances"]:
                dmg_res = ', '.join(monster_statblock["damage_resistances"])
                outfile.write(f"**Damage Resistances** :: {dmg_res}\n")

            if monster_statblock["damage_immunities"]:
                dmg_imm = ', '.join(monster_statblock["damage_immunities"])
                outfile.write(f"**Damage Immunities** :: {dmg_imm}\n")

            if monster_statblock["condition_immunities"]:
                con_imm_list = []
                for condition_immunity in monster_statblock["condition_immunities"]:
                    con_imm_list.append(condition_immunity["index"])
                con_imm = ', '.join(con_imm_list)
                outfile.write(f"**Condition Immunities** :: {con_imm}\n")

            # extract senses
            statblock_senses = str(monster_statblock['senses']).replace("{", "").replace("}", "").replace("'", "").replace(":", "").replace("_", " ")
            outfile.write(f"**Senses** :: {statblock_senses}\n")

            # handle emtpy language list
            if {monster_statblock["languages"]}:
                outfile.write(f"**Languages** :: {monster_statblock['languages']}\n")

            outfile.write(f"**Challenge Rating** :: {monster_statblock['challenge_rating']} ({monster_statblock['xp']} XP)\n")
            outfile.write("___\n")

            # traits and special abilities
            if monster_statblock["special_abilities"]:
                outfile.write(f"***{monster_statblock['special_abilities'][0]['name']}.*** {monster_statblock['special_abilities'][0]['desc']}\n")
                if len(monster_statblock['special_abilities']) > 1:
                    for index, ability in enumerate(monster_statblock['special_abilities'][1:]):
                        outfile.write(":\n")
                        outfile.write(f"***{ability['name']}.*** {ability['desc']}\n")

            # monster actions                    
            if "actions" in monster_statblock:
                outfile.write("### Actions\n")
                outfile.write(f"***{monster_statblock['actions'][0]['name']}.*** {monster_statblock['actions'][0]['desc']}\n")
                if len(monster_statblock['actions']) > 1:
                    for index, action in enumerate(monster_statblock['actions'][1:]):
                        outfile.write(":\n")
                        outfile.write(f"***{action['name']}.*** {action['desc']}\n")

            # monster legendary actions
            if monster_statblock["legendary_actions"]:
                outfile.write("### Legendary Actions\n")
                outfile.write(f"***{monster_statblock['legendary_actions'][0]['name']}.*** {monster_statblock['legendary_actions'][0]['desc']}\n")
                if len(monster_statblock['actions']) > 1:
                    for index, leg_action in enumerate(monster_statblock['legendary_actions'][1:]):
                        outfile.write(":\n")
                        outfile.write(f"***{leg_action['name']}.*** {leg_action['desc']}\n")
            outfile.write("}}\n")

            # check for page marker
            outfile.close()
            check = file_size(check, "STAT BLOCKS")
            outfile = open(args.output_filename, "a", encoding="utf-8")

        # write out list of skipped monsters deduped and ordered
        skipped_monsters = list(dict.fromkeys(skipped_monsters))
        skipped_monsters.sort()
        outfile.write(f"**Monsters without stat blocks**: {', '.join(skipped_monsters)}")       
        outfile.write("\n")
        outfile.write("{{footnote STAT BLOCKS}}\n")

    """ DONJON.BIN.SH SETTINGS PAGE """

    # donjon settings
    outfile.write("\\page\n")
    outfile.write("{{pageNumber,auto}}\n")

    outfile.write("{{wide\n")
    outfile.write("## Settings\n")
    outfile.write("Settings used to create this dungeon:\n")
    outfile.write(":\n")
    outfile.write(f"{INFEST.upper()} Random Dungeon Generator\n")
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
