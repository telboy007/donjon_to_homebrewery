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
from content.settings import create_donjon_settings
from content.overview import create_donjon_overview
from utilities.locations import sum_up_treasure, extract_book_details, add_magical_items_to_list, compile_monster_and_combat_details
from utilities.statblocks import extract_proficiencies_from_api_response, request_monster_statblock, get_ability_modifier, convert_low_cr_to_fraction

load_dotenv()


# *** page break utilities ***

def set_check():
    """Set the initial number of characters in the file"""
    with open(args.output_filename, "r", encoding="utf-8") as readonly_file:
        return len(readonly_file.read())


def file_size(current_check, footnote, flag=False):
    """Count the current number of characters in a file"""
    # first page of locations needs a larger check value
    value = 3200 if flag else 3000
    with open(args.output_filename, "r", encoding="utf-8") as readonly_file:
        new_size = len(readonly_file.read())
    if (new_size - current_check) > value:
        flag = False
        with open(args.output_filename, "a", encoding="utf-8") as append_file:
            append_file.write("{{")
            append_file.write(f"footnote {footnote}")
            append_file.write("}}\n")
            append_file.write("\\page\n")
            append_file.write("{{pageNumber,auto}}\n")
        # set new current check
        current_check = new_size
    return current_check, flag


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

# setup content used during creation of markdown
settings = create_donjon_settings(data["settings"])
overview = create_donjon_overview(data["details"], args.testmode)

# open output file to write content to
with open(args.output_filename, "w", encoding="utf-8") as outfile:

    # *** TITLE PAGE ***

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

    # *** OVERVIEW ***

    # overview page start
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
    if "corridor_features" in data:
        outfile.write("Some of the corridors marked on the map have special features detailed below.\n")
        outfile.write("{{descriptive\n")
        outfile.write("#### Corridor Features\n")
        outfile.write("| Type | Detail |\n")
        outfile.write("|:--|:--|\n")

        for key, val in data["corridor_features"].items():
            outfile.write(f"| {val['key']} | {val['detail'].replace(NEWLINE, ' ')} |\n")

        outfile.write("}}\n")

    # wandering monsters - certain dungeon types don't have any
    if "wandering_monsters" in data:
        outfile.write("### Random Encounters\n")

        outfile.write("There are also roaming groups with specific goals, this will help you place them in the dungeon or when the party encounter them.\n")
        outfile.write("{{classTable,frame\n")
        outfile.write("#### Wandering Monsters\n")
        outfile.write("| Roll | Detail |\n")
        outfile.write("|:--|:--|\n")

        for key, val in data["wandering_monsters"].items():
            outfile.write(f"| {key} | {val.replace(NEWLINE, ' ')} |\n")

            # add monster, combat types and xp to global lists
            if settings['ruleset'] == "dnd_5e":
                monster_list, combat_list, xp_list = compile_monster_and_combat_details(val.replace(NEWLINE, ' '), settings['ruleset'])
            if settings['ruleset'] == "dnd_4e":
                monster_list = compile_monster_and_combat_details(val.replace(NEWLINE, ' '), settings['ruleset'])

        outfile.write("}}\n")

    # add AI suggestions for boss, lair and adventure hooks if present
    if overview["ai_enhancements"]:
        # dungeon boss and lair details
        outfile.write("### Dungeon Boss\n")
        outfile.write(f"{overview['bbeg_and_lair']}\n")
        # two adventure hooks to help immerse the party in the dungeon
        outfile.write("### Adventure Hooks\n")
        outfile.write(f"{overview['adventure_hooks']}\n")
        # add some hints about tweaking the dungeon based on boss, lair and adventure hooks
        outfile.write("### Tweaking the dungeon\n")
        outfile.write("Pick a suitable location on the map to place the boss and it's lair, maybe foreshadow the lair by adding small details from it in nearby locations.\n\n")
        outfile.write("Depending on which adventure hook you choose, don't forget to tweak other elements of the dungeon accordingly, changing some of the monsters or random encounters to better reflect the general theme.\n")

    outfile.write("{{footnote OVERVIEW}}\n")
    outfile.write("\\page\n")
    outfile.write("{{pageNumber,auto}}\n")
    # overview page end

# set initial page marker check value
check = set_check()

with open(args.output_filename, "a", encoding="utf-8") as outfile:

    # *** DUNGEON DETAILS ***

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
            outfile.write(f"### Room {rooms['id']}\n")

            # check for page marker
            outfile.close()
            check, FIRST_PAGE = file_size(check, "LOCATIONS", FIRST_PAGE)
            outfile = open(args.output_filename, "a", encoding="utf-8")

            if "contents" in rooms:
                if "detail" in rooms["contents"]:

                    # traps
                    if "trap" in rooms["contents"]["detail"]:
                        outfile.write("{{trap\n")
                        outfile.write("#### Trap!\n")
                        for item in rooms["contents"]["detail"]["trap"]:
                            desc = item.replace("\n","")
                            outfile.write(f"* {desc}\n")

                        outfile.write("}}\n")

                    # check for page marker
                    outfile.close()
                    check, FIRST_PAGE = file_size(check, "LOCATIONS", FIRST_PAGE)
                    outfile = open(args.output_filename, "a", encoding="utf-8")

                    # hidden treasure
                    if "hidden_treasure" in rooms["contents"]["detail"]:
                        outfile.write("{{hidden-treasure\n")
                        outfile.write("#### Hidden Treasure!\n")
                        for item in rooms["contents"]["detail"]["hidden_treasure"]:
                            if item == "--":
                                continue
                            outfile.write(f"* {item.replace(NEWLINE,' ')}\n")
                            # add to magic items list for the summary page
                            if settings['ruleset'] == "dnd_5e":
                                magics = add_magical_items_to_list(item.replace(NEWLINE,' '), rooms['id'])
                                magic_items.update(magics)

                        outfile.write("}}\n")

                    # check for page marker
                    outfile.close()
                    check, FIRST_PAGE = file_size(check, "LOCATIONS", FIRST_PAGE)
                    outfile = open(args.output_filename, "a", encoding="utf-8")

                    # room description
                    if "room_features" in rooms["contents"]["detail"]:
                        outfile.write("{{descriptive\n")
                        outfile.write(f"{rooms['contents']['detail']['room_features']}.\n")
                        outfile.write("}}\n")

                    # check for page marker
                    outfile.close()
                    check, FIRST_PAGE = file_size(check, "LOCATIONS", FIRST_PAGE)
                    outfile = open(args.output_filename, "a", encoding="utf-8")

                    # monsters and treasure
                    if "monster" in rooms["contents"]["detail"]:
                        for thing in rooms["contents"]["detail"]["monster"]:
                            if thing == "--":
                                continue
                            if thing.startswith("Treasure"):
                                # custom format class
                                outfile.write("{{treasure\n")
                                outfile.write("#### Treasure\n")
                                if thing.count("(") == 0:
                                    thing = sum_up_treasure(thing.replace(",",";"), settings['ruleset'])
                                    outfile.write(f"{thing}\n")
                                else:
                                    outfile.write(f"{thing.replace(NEWLINE, ' ').replace('Treasure: ','')}\n")
                                    # add to magic items list for the summary page
                                    if settings['ruleset'] == "dnd_5e":
                                        magics = add_magical_items_to_list(thing.replace(NEWLINE, ' ').replace('Treasure: ',''), rooms['id'])
                                        magic_items.update(magics)
                                outfile.write("}}\n")
                            else:
                                outfile.write(f"This room is occupied by **{thing}**\n")
                                # add monster, combat types and xp to global lists
                                if settings['ruleset'] == "dnd_5e":
                                    monster_list, combat_list, xp_list = compile_monster_and_combat_details(thing, settings['ruleset'])
                                if settings['ruleset'] == "dnd_4e":
                                    monster_list = compile_monster_and_combat_details(thing, settings['ruleset'])

                    # check for page marker
                    outfile.close()
                    check, FIRST_PAGE = file_size(check, "LOCATIONS", FIRST_PAGE)
                    outfile = open(args.output_filename, "a", encoding="utf-8")

                # check for page marker
                outfile.close()
                check, FIRST_PAGE = file_size(check, "LOCATIONS", FIRST_PAGE)
                outfile = open(args.output_filename, "a", encoding="utf-8")

            # exits
            if "doors" in rooms:
                outfile.write("#### Exits\n")
                outfile.write("| Direction | Description | To |\n")
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
                            outfile.write(f"| {direction.capitalize()} | {d['desc']} {DESC} | {d['out_id']} |")
                        else:
                            outfile.write(f"| {direction.capitalize()} | {d['desc']} {DESC} | n/a |")
                        outfile.write("\n")

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

        # list out xp and combat type details if 5e dungeon
        if settings['ruleset'] == "dnd_5e":
            outfile.write("{{descriptive\n")
            outfile.write("#### Combat details (guide only)\n")

            # work out some xp totals
            total_xp = sum(int(i) for i in xp_list)
            shared_xp = round(sum(int(i) for i in xp_list)/int(settings['party_size']))

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
            monster_name, sourcebook = extract_book_details(item, settings['ruleset'])
            outfile.write(f"| {monster_name} | {sourcebook} |\n")

            # compile list of monsters for stat blocks
            if "mm" in sourcebook:
                monster_names.append(monster_name.lower().replace(" ", "-"))
            else:
                skipped_monsters.append(monster_name)

        outfile.write("}}\n")
        outfile.write(":\n")

        # list out magic items for 5th edition
        if settings['ruleset'] == "dnd_5e":
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

    # *** STAT BLOCKS ***

    # if 5th edition try to get as many monster stat blocks as possible
    if settings['ruleset'] == "dnd_5e":
        outfile.write("\\page\n")

        # update check value
        outfile.close()
        check = set_check()
        outfile = open(args.output_filename, "a", encoding="utf-8")

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
                STR_MOVEMENT = ', '.join(movement_types)
                outfile.write(f"**Speed** :: {STR_MOVEMENT.replace('Walk ', '')}\n")
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
                STR_THROWS = ', '.join(throws)
                outfile.write(f"**Saving Throws** :: {STR_THROWS}\n")

            if skill_checks:
                skills = []
                for key, value in skill_checks:
                    skills.append(f"{key.capitalize()} +{value}")
                STR_SKILLS = ', '.join(skills)
                outfile.write(f"**Skills** :: {STR_SKILLS}\n")

            #resistances and immunities
            if monster_statblock["damage_vulnerabilities"]:
                DMG_VUL = ', '.join(monster_statblock["damage_vulnerabilities"])
                outfile.write(f"**Damage Vulnerabilities** :: {DMG_VUL}\n")

            if monster_statblock["damage_resistances"]:
                DMG_RES = ', '.join(monster_statblock["damage_resistances"])
                outfile.write(f"**Damage Resistances** :: {DMG_RES}\n")

            if monster_statblock["damage_immunities"]:
                DMG_IMM = ', '.join(monster_statblock["damage_immunities"])
                outfile.write(f"**Damage Immunities** :: {DMG_IMM}\n")

            if monster_statblock["condition_immunities"]:
                con_imm_list = []
                for condition_immunity in monster_statblock["condition_immunities"]:
                    con_imm_list.append(condition_immunity["index"])
                CON_IMM = ', '.join(con_imm_list)
                outfile.write(f"**Condition Immunities** :: {CON_IMM}\n")

            # extract senses
            STATBLOCK_SENSES = str(monster_statblock['senses']).replace("{", "").replace("}", "").replace("'", "").replace(":", "").replace("_", " ")
            outfile.write(f"**Senses** :: {STATBLOCK_SENSES}\n")

            # handle emtpy language list
            if monster_statblock["languages"]:
                outfile.write(f"**Languages** :: {monster_statblock['languages']}\n")

            CR = convert_low_cr_to_fraction(monster_statblock['challenge_rating'])
            outfile.write(f"**Challenge Rating** :: {CR} ({monster_statblock['xp']} XP)\n")
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
            check, flag = file_size(check, "STAT BLOCKS")
            outfile = open(args.output_filename, "a", encoding="utf-8")

        # write out list of skipped monsters deduped and ordered
        skipped_monsters = list(dict.fromkeys(skipped_monsters))
        skipped_monsters.sort()
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
