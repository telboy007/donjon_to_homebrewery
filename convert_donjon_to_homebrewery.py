import json
import sys

# Open file to write content to
outfile = open("homebrewery.txt", "w")

# Opening JSON file
filename = sys.argv[1]
f = open(filename)
  
# returns JSON object as a dictionary
data = json.load(f)

""" title page """
if sys.argv[2]:
    outfile.writelines(f"<img src=\"{sys.argv[2]}\" style=\"position:absolute;mix-blend-mode: color-burn;transform:rotate(-30deg);width:500%;top:-1000px;\" />\n")
    outfile.writelines(":\n")

outfile.writelines("{{margin-top:225px}}\n")
outfile.writelines(f"# {data['settings']['name']}\n")
outfile.writelines("{{margin-top:25px}}\n")
outfile.writelines("{{wide\n")
outfile.writelines(f"##### {data['details']['history']}\n")
outfile.writelines("::\n")
outfile.writelines(f"##### A randomly generated donjon dungeon for APL{data['settings']['level']}\n")
outfile.writelines("}}\n")
outfile.writelines("\page\n")

""" map page """
if sys.argv[2]:
    outfile.writelines("## Map\n")
    outfile.writelines(f"<img src=\"{sys.argv[2]}.png\" style=\"width:680px\" />\n")
    outfile.writelines("Courtesy of <a href=\"https://donjon.bin.sh\">donjon.bin.sh</a>\n")
    outfile.writelines("\page\n")

""" general features """

outfile.writelines("## Description\n")

outfile.writelines("The generated dungeon has the following features, which may include skill checks to perform certain actions.\n")
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

outfile.writelines("Some of the corridors marked on the map have special features that are detailed below.\n")
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

outfile.writelines("As well as the monsters occupying certain rooms in the dungeon, there are roaming groups with their current action/purpose.  This will help you place them in the dungeon or when the party encounter them.\n")
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
    outfile.writelines(f"The entrance into this dungeon can be found on the map at ***row: {egress['row']}*** and ***column: {egress['col']}*** on the DM version of the map, which enters the {egress['type']} from the {egress['dir']}.\n")

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
                        try:
                            outfile.writelines("|" + str(direction) + "|" + str(d["desc"]) + " ***Trap:*** " + str(d["trap"]).replace("\n", "") + "|" + str(d["out_id"]) + "|\n")
                        except:
                            outfile.writelines("|" + str(direction) + "|" + str(d["desc"]) + " ***Trap:*** " + str(d["trap"]).replace("\n", "") + "|n/a|\n")     
                    elif d["type"] == "secret":
                            try:
                                outfile.writelines("|" + str(direction) + "|" + str(d["desc"]) + " ***Secret:*** " + str(d["secret"]).replace("\n", "") + "|" + str(d["out_id"]) + "|\n")
                            except:
                                outfile.writelines("|" + str(direction) + "|" + str(d["desc"]) + " ***Secret:*** " + str(d["secret"]).replace("\n", "") + "|n/a|\n")     
                    else:
                        try:
                            outfile.writelines("|" + str(direction) + "|" + str(d["desc"]) + "|" + str(d["out_id"]) + "|\n")
                        except:
                            outfile.writelines("|" + str(direction) + "|" + str(d["desc"]) + "|n/a|\n")              

            outfile.writelines(":\n")

outfile.close()