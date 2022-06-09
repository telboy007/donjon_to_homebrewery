import json
import sys

# Opening JSON file
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

""" title page """
if len(sys.argv) == 3:
    outfile.writelines(f"<img src=\"{sys.argv[2]}\" style=\"position:absolute;mix-blend-mode: color-burn;transform:rotate(-30deg);width:500%;top:-1000px;\" />\n")
    outfile.writelines(":\n")

outfile.writelines("{{margin-top:225px}}\n")
outfile.writelines(f"# {data['settings']['name']}\n")
outfile.writelines("{{margin-top:25px}}\n")
outfile.writelines("{{wide\n")
outfile.writelines(f"##### {data['details']['history']}\n")
outfile.writelines("::\n")
outfile.writelines(f"##### A randomly generated D&D 5e donjon dungeon for APL{data['settings']['level']}\n")
outfile.writelines("}}\n")
outfile.writelines("\page\n")

""" map page """
if len(sys.argv) == 3:
    outfile.writelines("## Map\n")
    outfile.writelines(f"<img src=\"{sys.argv[2]}.png\" style=\"width:680px\" />\n")
    outfile.writelines("Courtesy of <a href=\"https://donjon.bin.sh\">donjon.bin.sh</a>\n")
    outfile.writelines("\page\n")

""" general features """

outfile.writelines("## Description\n")

outfile.writelines("The dungeon has the following features, these may include skill checks to perform certain actions.\n")
outfile.writelines("{{descriptive\n")
outfile.writelines("#### General Features\n")
outfile.writelines("| Type | Detail |\n")
outfile.writelines("|:--|:--|\n")
outfile.writelines(f"| Floors | {data['details']['floor']} |\n")
outfile.writelines(f"| Walls | {data['details']['walls']} |\n")
outfile.writelines(f"| Temperature | {data['details']['temperature']} |\n")
outfile.writelines(f"| Lighting | {data['details']['illumination']} |\n")
outfile.writelines("}}\n")

""" corridor features """

outfile.writelines("Some of the corridors marked on the map have special features detailed below.\n")
outfile.writelines("{{descriptive\n")
outfile.writelines("#### Corridor Features\n")
outfile.writelines("| Type | Detail |\n")
outfile.writelines("|:--|:--|\n")

for key, val in data["corridor_features"].items():
    detail = val["detail"].replace("\n", " ")
    outfile.writelines(f"| {val['key']} | {detail} |\n")

outfile.writelines("}}\n")

""" wandering monsters """

outfile.writelines("## Random Encounters\n")

outfile.writelines("As well as the monsters occupying certain rooms in the dungeon, there are roaming groups with a specific goal.  This will help you place them in the dungeon or when the party encounter them.\n")
outfile.writelines("{{classTable,frame\n")
outfile.writelines("#### Wandering Monsters\n")
outfile.writelines("| Roll | Detail |\n")
outfile.writelines("|:--|:--|\n")

for key, val in data["wandering_monsters"].items():
    group = val.replace("\n", " ")
    outfile.writelines(f"| {key} | {group} |\n")
    
outfile.writelines("}}\n")

""" Locations """

outfile.writelines("## Locations\n")

for egress in data["egress"]:
    outfile.writelines("### Getting In\n")
    outfile.writelines(f"The entrance into this dungeon can be found on the GM version of the map at ***row: {egress['row']}*** and ***column: {egress['col']}***, which enters the {egress['type']} from the {egress['dir']}.\n")

""" rooms / locations """

if "rooms" in data:
    for rooms in data["rooms"]:
        if rooms is None:
            continue
        outfile.writelines(f"### Room {rooms['id']}\n")

        if "contents" in rooms:
            if "detail" in rooms["contents"]:

                """ traps """
                if "trap" in rooms["contents"]["detail"]:
                    outfile.writelines(":\n")
                    outfile.writelines("{{classTable,frame\n")
                    outfile.writelines("#### Trap!\n")
                    for item in rooms["contents"]["detail"]["trap"]:
                        desc = item.replace("\n","")
                        outfile.writelines(f"* {desc}\n")
                    
                    outfile.writelines("}}\n")

                """ hidden treasure """
                if "hidden_treasure" in rooms["contents"]["detail"]:
                    outfile.writelines(":\n")
                    outfile.writelines("{{classTable,frame\n")
                    outfile.writelines("#### Hidden Treasure!\n")
                    for item in rooms["contents"]["detail"]["hidden_treasure"]:
                        if item == "--":
                            continue
                        else:
                            item = item.replace("\n","")
                            outfile.writelines(f"* {item}\n")
                    
                    outfile.writelines("}}\n")

                """ room description """
                if "room_features" in rooms["contents"]["detail"]:
                    outfile.writelines(":\n")
                    outfile.writelines("{{note\n")
                    outfile.writelines(f"{rooms['contents']['detail']['room_features']}.\n")
                    outfile.writelines("}}\n")
                else:
                    outfile.writelines(":\n")
                    outfile.writelines("{{note\n")
                    outfile.writelines("Empty.\n")
                    outfile.writelines("}}\n")

                """ monsters and treasure """
                if "monster" in rooms["contents"]["detail"]:
                    for thing in rooms["contents"]["detail"]["monster"]:
                        if thing == "--":
                            continue
                        elif thing.startswith("Treasure"):
                            thing.replace("\n","")
                            outfile.writelines(":\n")
                            outfile.writelines("{{descriptive\n")
                            outfile.writelines("#### Treasure\n")
                            outfile.writelines(f"{thing}\n")
                            outfile.writelines("}}\n")
                        else:
                            outfile.writelines("::\n")
                            outfile.writelines(f"This room is occupied by **{thing}**\n")
            else:
                # no details
                outfile.writelines(":\n")
                outfile.writelines("{{note\n")
                outfile.writelines("Empty.\n")
                outfile.writelines("}}\n")

        """ exits """
        if "doors" in rooms:
            outfile.writelines("#### Exits\n")
            outfile.writelines("| Direction | Description | Leads to |\n")
            outfile.writelines("|:--|:--|:--|\n")

            for direction, door in rooms["doors"].items():
                for d in door:
                    if d["type"] == "trapped":
                        trap = d["trap"].replace("\n", "")
                        try:
                            outfile.writelines(f"| {direction} | {d['desc']} ***Trap:*** {trap} | {d['out_id']} |\n")
                        except:
                            outfile.writelines(f"| {direction} | {d['desc']} ***Trap:*** {trap} | n/a |\n")
                    elif d["type"] == "secret":
                        secret = d["secret"].replace("\n", "")
                        try:
                            outfile.writelines(f"| {direction} | {d['desc']} ***Secret:*** {secret} | {d['out_id']} |\n")
                        except:
                            outfile.writelines(f"| {direction} | {d['desc']} ***Secret:*** {secret} | n/a |\n")
                    else:
                        try:
                            outfile.writelines(f"| {direction} | {d['desc']} | {d['out_id']} |\n")
                        except:
                            outfile.writelines(f"| {direction} | {d['desc']} | n/a |\n")           

            outfile.writelines(":\n")

outfile.close()