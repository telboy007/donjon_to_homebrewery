#!/usr/bin/env python

"""
    Donjon to homebrewery convertor
    line arguments:
        json file [mandatory]
        gm map url [optional]
        player map url [optional]
        output file [optional]
        testmode [optional]
"""

import argparse
import json
from collections import OrderedDict
from dotenv import load_dotenv
from dth.content.corridor_features import create_donjon_corridor_features
from dth.content.location import create_donjon_single_location
from dth.content.overview import create_donjon_overview
from dth.content.settings import create_donjon_settings
from dth.content.statblock import create_5e_statblock
from dth.content.wandering_monsters import create_donjon_wandering_monsters
from dth.utilities.locations import extract_book_details, compile_monster_and_combat_details
from dth.utilities.summary import calculate_total_and_shared_xp, dedupe_and_sort_list_via_dict

load_dotenv()


# *** page break utilities ***
def set_check():
    """Set the initial number of characters in the file"""
    with open(args.output_filename, "r", encoding="utf-8") as readonly_file:
        return len(readonly_file.read())


def file_size(current_check, footnote, first_page_flag=False):
    """Count the current number of characters in a file"""
    # first page of locations needs a larger check value
    extra = 500 if footnote == "OVERVIEW" else 200
    check_value = 3000 + extra if first_page_flag else 3000
    with open(args.output_filename, "r", encoding="utf-8") as readonly_file:
        new_size = len(readonly_file.read())
    if (new_size - current_check) > check_value:
        first_page_flag = False
        with open(args.output_filename, "a", encoding="utf-8") as append_file:
            append_file.write("{{")
            append_file.write(f"footnote {footnote}")
            append_file.write("}}\n")
            append_file.write("\\page\n")
            append_file.write("{{pageNumber,auto}}\n")
        # set new current check
        current_check = new_size
    return current_check, first_page_flag


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
parser.add_argument('-gm', '--gm_map_url', help='URL for the GM Map image') # optional
parser.add_argument('-p', '--player_map_url', help='URL for the Player map image') # optional
parser.add_argument('-o', '--output_filename', help='Override for text filename', default="homebrewery.txt") # optional
parser.add_argument('-t', '--testmode', help='Stops AI enhancing dungeon details', default=False, action='store_true') # optional

args = parser.parse_args()

# convert input file from json to dictionary
filename = args.filename
with open(filename, encoding="utf-8") as inputfile:
    data = json.load(inputfile)

# setup content used during creation of title and overview
settings = create_donjon_settings(data["settings"])
overview = create_donjon_overview(data["details"], settings, args.testmode)
corridor_features = create_donjon_corridor_features(data)
wandering_monsters = create_donjon_wandering_monsters(data)

# *** TITLE PAGE ***
with open(args.output_filename, "w", encoding="utf-8") as outfile:
    # title page start
    if args.gm_map_url:
        outfile.write(f"![map]({args.gm_map_url}){{position:absolute;mix-blend-mode:color-burn;transform:rotate(-30deg);width:500%;top:-1000px;}}\n")

    outfile.write("{{margin-top:225px}}\n")
    # start title css formatting
    outfile.write("{{wide,background-color:white,border-width:10px,border-radius:20px,padding:10px,margin-left:-10px\n")
    outfile.write(f"# {settings['dungeon_name']}\n")

    # certain dungeon generators don't create a blurb
    if overview["blurb"]:
        outfile.write(":\n")
        outfile.write(f"##### {overview['blurb']}\n")
        outfile.write(":::\n")
    else:
        outfile.write(":::\n")

    outfile.write(f"##### A randomly generated {settings['ruleset_nice'].upper()} donjon dungeon for a party size of {settings['party_size']} and APL{settings['dungeon_level']}\n")
    outfile.write(":::\n")
    outfile.write(f"##### Created using [Homebrewery]({settings['homebrewery_url']}), [Donjon]({settings['donjon_url']}) and [donjon_to_homebrewery]({settings['dth_url']})\n")
    # close title css formatting

    outfile.write("}}\n")
    outfile.write("\\page\n")
    outfile.write("{{pageNumber,auto}}\n")
    # title page end

    # *** MAP PAGES ***

    # map page(s) start
    if args.gm_map_url:
        outfile.write("## GM Map\n")
        outfile.write(f"![map]({args.gm_map_url}){{width:680px;}}\n")
        outfile.write(f"Courtesy of [donjon.bin.sh]({settings['donjon_url']})\n")
        outfile.write("{{footnote MAPS}}\n")
        outfile.write("\\page\n")
        outfile.write("{{pageNumber,auto}}\n")

    if args.player_map_url:
        outfile.write("## Player Map\n")
        outfile.write(f"![map]({args.player_map_url}){{width:680px;}}\n")
        outfile.write(f"Courtesy of [donjon.bin.sh]({settings['donjon_url']})\n")
        outfile.write("{{footnote MAPS}}\n")
        outfile.write("\\page\n")
        outfile.write("{{pageNumber,auto}}\n")
    # map page(s) end

# set page marker check value
check = set_check()

# *** OVERVIEW ***
with open(args.output_filename, "a", encoding="utf-8") as outfile:
    # overview page start
    FIRST_PAGE = True
    outfile.write("## Overview\n")

    # add AI flavour text for dungeon if description available
    if overview["ai_enhancements"]:
        outfile.write("### Description\n")
        outfile.write(f"{overview['flavour_text']}\n")

    # general features
    outfile.write("### Features\n")
    outfile.write("The dungeon has the following features, these may include skill checks to perform certain actions.\n")
    outfile.write("{{descriptive\n")
    outfile.write("#### General Features\n")
    outfile.write("| Type | Detail |\n")
    outfile.write("|:--|:--|\n")
    outfile.write(f"| Floors | {overview['floor']} |\n")
    outfile.write(f"| Walls | {overview['walls']} |\n")
    outfile.write(f"| Temperature | {overview['temperature']} |\n")
    outfile.write(f"| Lighting | {overview['illumination']} |\n")
    if overview["special"]:
        outfile.write(f"| Special | {overview['special']} |\n")
    outfile.write("}}\n")

    # corridor features - caves don't have corridor features
    if corridor_features:
        outfile.write("Some of the corridors marked on the map have special features detailed below.\n")
        outfile.write("{{descriptive\n")
        outfile.write("#### Corridor Features\n")
        outfile.write("| Type | Detail |\n")
        outfile.write("|:--|:--|\n")
        # write out corridor features by row
        for feature in corridor_features["feature_list"]:
            for key, value in feature.items():
                outfile.write(f"| {key} | {value} |\n")

        outfile.write("}}\n")

    # wandering monsters - certain dungeon types don't have any
    if wandering_monsters["monsters"]:
        outfile.write("### Random Encounters\n")

        outfile.write("There are also roaming groups with specific goals, this will help you place them in the dungeon or when the party encounter them.\n")
        outfile.write("{{classTable,frame\n")
        outfile.write("#### Wandering Monsters\n")
        outfile.write("| Roll | Detail |\n")
        outfile.write("|:--|:--|\n")

        # write out monster detail by row
        for monster in wandering_monsters["monster_details"]:
            for key, value in monster.items():
                outfile.write(f"| {key} | {value} |\n")

        outfile.write("}}\n")

    # check for page marker
    outfile.close()
    check, FIRST_PAGE = file_size(check, "OVERVIEW", FIRST_PAGE)
    outfile = open(args.output_filename, "a", encoding="utf-8")

    # add AI suggestions for boss, lair and adventure hooks if present
    if overview["ai_enhancements"]:
        # dungeon boss and lair details
        outfile.write("### Dungeon Boss\n")
        outfile.write(f"{overview['bbeg_and_lair']}\n")

        # check for page marker
        outfile.close()
        check, FIRST_PAGE = file_size(check, "OVERVIEW", FIRST_PAGE)
        outfile = open(args.output_filename, "a", encoding="utf-8")

        # two adventure hooks to help immerse the party in the dungeon
        outfile.write("### Adventure Hooks\n")
        outfile.write(f"{overview['adventure_hooks']}\n")

        # check for page marker
        outfile.close()
        check, FIRST_PAGE = file_size(check, "OVERVIEW", FIRST_PAGE)
        outfile = open(args.output_filename, "a", encoding="utf-8")
        
        # add some hints about tweaking the dungeon based on boss, lair and adventure hooks
        outfile.write("### Tweaking the dungeon\n")
        outfile.write("Pick a suitable location on the map to place the boss and it's lair, maybe foreshadow the lair by adding small details from it in nearby locations.\n\n")
        outfile.write("Depending on which adventure hook you choose, don't forget to tweak other elements of the dungeon accordingly, changing some of the monsters or random encounters to better reflect the general theme.\n")

    outfile.write("{{footnote OVERVIEW}}\n")
    outfile.write("\\page\n")
    outfile.write("{{pageNumber,auto}}\n")
    # overview page end

# add wandering monster details to global lists
monster_list, combat_list, xp_list = compile_monster_and_combat_details(wandering_monsters["monster_details"], settings['ruleset'], monster_list, combat_list, xp_list)

# set page marker check value
check = set_check()

# *** DUNGEON DETAILS ***
with open(args.output_filename, "a", encoding="utf-8") as outfile:
    # locations start
    FIRST_PAGE = True
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

    # *** LOCATION DETAILS ***

    # rooms
    if "rooms" in data:
        for rooms in data["rooms"]:
            if rooms is None:
                continue
            # parse room details into location dict and update lists
            location, magic_items, monster_list, combat_list, xp_list = create_donjon_single_location(
                                                                                                    rooms,
                                                                                                    settings,
                                                                                                    magic_items,
                                                                                                    monster_list,
                                                                                                    combat_list,
                                                                                                    xp_list
                                                                                                )
            # check for page marker
            outfile.close()
            check, FIRST_PAGE = file_size(check, "LOCATIONS", FIRST_PAGE)
            outfile = open(args.output_filename, "a", encoding="utf-8")

            # write out location details
            outfile.write(f"### Room {location['id']}\n")

            # write out traps
            if "trap" in location:
                outfile.write("{{trap\n")
                outfile.write("#### Trap!\n")
                for item in location["trap"]:
                    outfile.write(f"* {item}\n")
                outfile.write("}}\n")

            # check for page marker
            outfile.close()
            check, FIRST_PAGE = file_size(check, "LOCATIONS", FIRST_PAGE)
            outfile = open(args.output_filename, "a", encoding="utf-8")

            # write out hidden treasure
            if "hidden_treasure" in location:
                outfile.write("{{hidden-treasure\n")
                outfile.write("#### Hidden Treasure!\n")
                for item in location["hidden_treasure"]:
                    outfile.write(f"* {item}\n")
                outfile.write("}}\n")

            # check for page marker
            outfile.close()
            check, FIRST_PAGE = file_size(check, "LOCATIONS", FIRST_PAGE)
            outfile = open(args.output_filename, "a", encoding="utf-8")

            # write out room description
            if "features" in location:
                outfile.write("{{descriptive\n")
                outfile.write(f"{location['features']}.\n")
                outfile.write("}}\n")

            # check for page marker
            outfile.close()
            check, FIRST_PAGE = file_size(check, "LOCATIONS", FIRST_PAGE)
            outfile = open(args.output_filename, "a", encoding="utf-8")

            # write out monster (adnd produces a list of occupants)
            if "monster" in location:
                for occupant in location["monster"]:
                    outfile.write(f"This room is occupied by **{occupant}**\n")

            # check for page marker
            outfile.close()
            check, FIRST_PAGE = file_size(check, "LOCATIONS", FIRST_PAGE)
            outfile = open(args.output_filename, "a", encoding="utf-8")

            # write out treasure
            if "treasure" in location:
                outfile.write("{{treasure\n")
                outfile.write("#### Treasure\n")
                outfile.write(f"{location['treasure']}\n")
                outfile.write("}}\n")

            # check for page marker
            outfile.close()
            check, FIRST_PAGE = file_size(check, "LOCATIONS", FIRST_PAGE)
            outfile = open(args.output_filename, "a", encoding="utf-8")

            # write out exits
            if "exits" in location:
                outfile.write("#### Exits\n")
                outfile.write("| Direction | Description | To |\n")
                outfile.write("|:--|:--|:--|\n")

                for way_out in location["exits"]:
                    # {"direction", "exit_desc", "extra_detail", "leads_to"}
                    outfile.write(f"| {way_out['direction']} | {way_out['exit_desc']} {way_out['extra_detail']} | {way_out['leads_to']} |\n")

                outfile.write(":\n")

            # check for page marker
            outfile.close()
            check, FIRST_PAGE = file_size(check, "LOCATIONS", FIRST_PAGE)
            outfile = open(args.output_filename, "a", encoding="utf-8")

    outfile.write("{{footnote LOCATIONS}}\n")
    # locations end

    # *** SUMMARY PAGE ***

    # if 4th or 5th edition then create a summary page
    if settings["summary_page"]:
        outfile.write("\\page\n")
        outfile.write("{{pageNumber,auto}}\n")

        # summary
        outfile.write("## Summary\n")
        outfile.write("Here you will find useful reference tables for things encountered in the dungeon.\n")

        # 4e and 5e both have XP summaries
        outfile.write("{{descriptive\n")
        outfile.write("#### Combat details (guide only)\n")

        # work out xp totals
        total_xp, shared_xp = calculate_total_and_shared_xp(xp_list, settings['party_size'])
        outfile.write(f"**Total XP: {total_xp}** which is {shared_xp} xp per party member.\n")

        # list out combat type details for 5e
        if settings['ruleset'] == "dnd_5e":
            outfile.write("| Type | Amount |\n")
            outfile.write("|:--|:--|\n")
            outfile.write(f"| Easy | {combat_list.count('easy')} |\n")
            outfile.write(f"| Medium | {combat_list.count('medium')} |\n")
            outfile.write(f"| Hard | {combat_list.count('hard')} |\n")
            outfile.write(f"| Deadly | {combat_list.count('deadly')} |\n")

        # close the xp and combat descriptive panel
        outfile.write("}}\n")
        outfile.write(":\n")

        # list out monsters in a handy reference table
        outfile.write("{{descriptive\n")
        outfile.write("#### Monster List (alphabetical)\n")
        outfile.write("| Monster | Book |\n")
        outfile.write("|:--|:--|\n")

        # dedupe and order monster list and work out number of monsters
        monster_list = dedupe_and_sort_list_via_dict(monster_list)

        for index, item in enumerate(monster_list):
            # split out monster and source book details
            monster_name, sourcebook = extract_book_details(item, settings['ruleset'])
            outfile.write(f"| {monster_name} | {sourcebook} |\n")

            # add break in table if monster list is super long
            if index == 38 and len(monster_list) > 38:
                outfile.write("}}\n")
                outfile.write(":\n")
                outfile.write("{{descriptive\n")
                outfile.write("#### Monster List (alphabetical) cont.\n")
                outfile.write("| Monster | Book |\n")
                outfile.write("|:--|:--|\n")          

            # compile list of monsters for stat block api calls
            if "mm" in sourcebook:
                monster_names.append(monster_name.lower().replace(" ", "-"))
            else:
                # skipped monsters will be listed out after stat blocks  
                skipped_monsters.append(monster_name)

        outfile.write("}}\n")
        outfile.write(":\n")

        # before adding magic items see if we need to split table
        if len(monster_list) >= 38:
            split_value = 53
        else:
            split_value = 38 - (len(monster_list) + 6)

        # list out magic items for 5th edition
        if settings['ruleset'] == "dnd_5e":
            outfile.write("{{descriptive\n")
            outfile.write("#### Magic Items (alphabetical)\n")
            outfile.write("| Item | Book | Room |\n")
            outfile.write("|:--|:--|--:|\n")
            ordered_magic_items = OrderedDict(sorted(magic_items.items()))

            SPLIT_CHECK = True
            for index, (magic_item, details) in enumerate(ordered_magic_items.items()):
                # we need to check whether there are any long names
                if len(magic_item) >= 40 and index <= split_value and SPLIT_CHECK:
                    split_value = round(split_value / 2)
                    SPLIT_CHECK = False
                # split out location and source book details
                sourcebook, location = details.split('/')
                outfile.write(f"| {magic_item} | {sourcebook} | {location} |\n")

                # split table and continue on next column
                if index == split_value and len(ordered_magic_items) > split_value:
                    outfile.write("}}\n")
                    outfile.write(":\n")
                    outfile.write("{{descriptive\n")
                    outfile.write("#### Magic Items (alphabetical) cont.\n")
                    outfile.write("| Item | Book | Room |\n")
                    outfile.write("|:--|:--|--:|\n")
                    
            outfile.write("}}\n")

        # final footnote
        outfile.write("{{footnote SUMMARY}}\n")

# set page marker check value
check = set_check()
current_statblocks = 0

# *** STAT BLOCKS ***
with open(args.output_filename, "a", encoding="utf-8") as outfile:

    # if 5th edition try to get as many monster stat blocks as possible
    if settings['ruleset'] == "dnd_5e":
        outfile.write("\\page\n")

        outfile.write("{{pageNumber,auto}}\n")
        outfile.write("# Stat Blocks (SRD only)\n")

        for monster in monster_names:
            monster_statblock, skipped_monsters = create_5e_statblock(monster, skipped_monsters)

            # check for monster listed as in monster manual but not found in api
            if monster_statblock == {}:
                continue

            """
                need to split up statblocks when:
                current_statblocks = 3 and next is size = 2
                current_statblocks = 3 and last one was size = 2
                current_statblocks = 4
            """
            if current_statblocks == 3 and int(monster_statblock["markdown_size"]) == 2:
                outfile.write("{{footnote STAT BLOCKS}}\n")
                outfile.write("\\page\n")
                outfile.write("{{pageNumber,auto}}\n")
                current_statblocks = int(monster_statblock["markdown_size"])
            elif current_statblocks == 3 and previous_statblock == 2:
                outfile.write("{{footnote STAT BLOCKS}}\n")
                outfile.write("\\page\n")
                outfile.write("{{pageNumber,auto}}\n")
                current_statblocks = int(monster_statblock["markdown_size"])
            elif current_statblocks == 4:
                outfile.write("{{footnote STAT BLOCKS}}\n")
                outfile.write("\\page\n")
                outfile.write("{{pageNumber,auto}}\n")
                current_statblocks = int(monster_statblock["markdown_size"])
            else:
                current_statblocks += int(monster_statblock["markdown_size"])

            # write out statblock if monster found
            outfile.write("{{monster,frame\n")
            outfile.write(f"## {monster_statblock['name']}\n")
            outfile.write(f"*{monster_statblock['size']} {monster_statblock['type']}, {monster_statblock['alignment']}*\n")
            outfile.write("___\n")
            outfile.write(f"**Armor Class** :: {monster_statblock['ac']} ")
            outfile.write(f"{monster_statblock['armour_type']}\n")
            outfile.write(f"**Hit Points** :: {monster_statblock['hp']} ({monster_statblock['hp_formula']})\n")
            outfile.write(f"**Speed** :: {monster_statblock['speed']}\n")
            outfile.write("___\n")
            outfile.write("|STR|DEX|CON|INT|WIS|CHA|\n")
            outfile.write("|:---:|:---:|:---:|:---:|:---:|:---:|\n")
            outfile.write(f"|{monster_statblock['str']} ({monster_statblock['str_mod']})")
            outfile.write(f"|{monster_statblock['dex']} ({monster_statblock['dex_mod']})")
            outfile.write(f"|{monster_statblock['con']} ({monster_statblock['con_mod']})")
            outfile.write(f"|{monster_statblock['int']} ({monster_statblock['int_mod']})")
            outfile.write(f"|{monster_statblock['wis']} ({monster_statblock['wis_mod']})")
            outfile.write(f"|{monster_statblock['cha']} ({monster_statblock['cha_mod']})|\n")
            outfile.write("___\n")
            if "saving_throws" in monster_statblock:
                outfile.write(f"**Saving Throws** :: {monster_statblock['saving_throws']}\n")
            if "skill_checks" in monster_statblock:
                outfile.write(f"**Skills** :: {monster_statblock['skill_checks']}\n")
            if "damage_vulnerabilities" in monster_statblock:
                outfile.write(f"**Damage Vulnerabilities** :: {monster_statblock['damage_vulnerabilities']}\n")
            if "damage_resistances" in monster_statblock:
                outfile.write(f"**Damage Resistances** :: {monster_statblock['damage_resistances']}\n")
            if "damage_immunities" in monster_statblock:
                outfile.write(f"**Damage Immunities** :: {monster_statblock['damage_immunities']}\n")
            if "damage_vulnerabilities" in monster_statblock:
                outfile.write(f"**Damage Vulnerabilities** :: {monster_statblock['damage_vulnerabilities']}\n")
            if "condition_immunities" in monster_statblock:
                outfile.write(f"**Condition Immunities** :: {monster_statblock['condition_immunities']}\n")
            outfile.write(f"**Senses** :: {monster_statblock['senses']}\n")
            if "languages" in monster_statblock:
                outfile.write(f"**Languages** :: {monster_statblock['languages']}\n")
            outfile.write(f"**Challenge Rating** :: {monster_statblock['CR']} ({monster_statblock['XP']} XP)\n")
            outfile.write("___\n")

            # traits and special abilities
            if "special_abilities" in monster_statblock:
                for index, (key, value) in enumerate(monster_statblock["special_abilities"].items()):
                    if index == 0:
                        outfile.write(f"***{key}.*** {value}\n")
                    if index > 0:
                        outfile.write(":\n")
                        outfile.write(f"***{key}.*** {value}\n")

            # monster actions
            if "actions" in monster_statblock:
                outfile.write(f"### Actions\n")
                for index, (key, value) in enumerate(monster_statblock["actions"].items()):
                    if index == 0:
                        outfile.write(f"***{key}.*** {value}\n")
                    if index > 0:
                        outfile.write(":\n")
                        outfile.write(f"***{key}.*** {value}\n")

            # monster legendary actions
            if "legendary_actions" in monster_statblock:
                outfile.write(f"### Legendary Actions\n")
                for index, (key, value) in enumerate(monster_statblock["legendary_actions"].items()):
                    if index == 0:
                        outfile.write(f"***{key}.*** {value}\n")
                    if index > 0:
                        outfile.write(":\n")
                        outfile.write(f"***{key}.*** {value}\n")

            outfile.write("}}\n")

            # keep track of last statblock size
            previous_statblock = int(monster_statblock["markdown_size"])

        # write out list of skipped monsters deduped and ordered
        skipped_monsters = dedupe_and_sort_list_via_dict(skipped_monsters)
        outfile.write(f"**Monsters without stat blocks**: {', '.join(skipped_monsters)}")
        outfile.write("\n")
        outfile.write("{{footnote STAT BLOCKS}}\n")

    # *** DONJON.BIN.SH SETTINGS PAGE ***

    # donjon settings
    outfile.write("\\page\n")
    outfile.write("{{pageNumber,auto}}\n")

    outfile.write("{{wide\n")
    outfile.write("## Settings\n")
    outfile.write("Settings used to create this dungeon:\n")
    outfile.write(":\n")
    outfile.write(f"{settings['ruleset_nice'].upper()} Random Dungeon Generator\n")
    outfile.write("|||\n")
    outfile.write("|:--|:--|\n")
    outfile.write(f"|Dungeon Name|{settings['dungeon_name']}|\n")
    outfile.write(f"|Dungeon Level|{settings['dungeon_level']}|\n")
    outfile.write(f"|Party Size|{settings['party_size']}|\n")
    outfile.write(f"|Motif|{settings['motif']}|\n")
    outfile.write("}}\n")
    outfile.write(":\n")
    outfile.write("|||\n")
    outfile.write("|:--|:--|\n")
    outfile.write(f"|Random Seed|{settings['random_seed']}|\n")
    outfile.write(f"|Dungeon Size|{settings['dungeon_size']}|\n")
    outfile.write(f"|Dungeon Layout|{settings['dungeon_layout']}|\n")
    outfile.write(f"|Peripheral Egress?|{settings['peripheral_egress']}|\n")
    outfile.write(f"|Room Layout|{settings['room_layout']}|\n")
    outfile.write(f"|Room Size|{settings['room_size']}|\n")
    outfile.write(f"|Polymorph Rooms?|{settings['polymorph_rooms']}|\n")
    outfile.write(f"|Doors|{settings['doors']}|\n")
    outfile.write(f"|Corridors|{settings['corridors']}|\n")
    outfile.write(f"|Remove Deadends?|{settings['remove_deadends']}|\n")
    outfile.write(f"|Stairs?|{settings['stairs']}|\n")
    outfile.write(f"|Map Style|{settings['map_style']}|\n")
    outfile.write(f"|Grid|{settings['grid']}|\n")

    outfile.write("\\column\n")

    if args.gm_map_url:
        outfile.write(":\n")
        outfile.write(f"![map]({args.gm_map_url}){{width:50%;}}\n")
        outfile.write(":\n")
        outfile.write(f"Courtesy of [donjon.bin.sh]({settings['donjon_url']})\n")

    # homebrewery logo
    outfile.write("![logo](https://i.imgur.com/cYz20b0.png){position:absolute,bottom:100px,left:43%,width:14%,filter:invert(60%)}\n")
    outfile.write("{{footnote SETTINGS}}\n")
    # fin
