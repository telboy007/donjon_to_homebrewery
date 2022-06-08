import json

# Open file to write content to
outfile = open("homebrewery.txt", "w")

# Opening JSON file
f = open("example.json")
  
# returns JSON object as a dictionary
data = json.load(f)

""" title page """

outfile.writelines("{{margin-top:225px}}\n")
outfile.writelines(f'# {data["settings"]["name"]}\n')
outfile.writelines("{{margin-top:25px}}\n")
outfile.writelines("{{wide\n")
outfile.writelines(f'##### {data["details"]["history"]}\n')
outfile.writelines("::\n")
outfile.writelines(f'##### A randomly generated donjon dungeon for APL{data["settings"]["level"]}\n')
outfile.writelines("}}\n")
outfile.writelines("\page\n")

""" general features """

outfile.writelines("## Description\n")

outfile.writelines("{{descriptive\n")
outfile.writelines("### General Features\n")
outfile.writelines("| Type | Detail |\n")
outfile.writelines("|:--|:--|\n")
outfile.writelines("| Floors |" + data["details"]["floor"] + "|\n")
outfile.writelines("| Walls |" + data["details"]["walls"] + "|\n")
outfile.writelines("| Temperature |" + data["details"]["temperature"] + "|\n")
outfile.writelines("| Lighting |" + data["details"]["illumination"] + "|\n")

""" corridor features """

outfile.writelines("### Corridor Features\n")
outfile.writelines("| Type | Detail |\n")
outfile.writelines("|:--|:--|\n")

for key, val in data["corridor_features"].items():
    outfile.writelines("|" + val["key"] + "|" + val["detail"].replace("\n", " ") + "|\n")

outfile.writelines("}}\n")

""" wandering monsters """

outfile.writelines("## Random Encounters\n")

outfile.writelines("{{classTable,frame\n")
outfile.writelines("### Wandering Monsters\n")
outfile.writelines("| Roll | Detail |\n")
outfile.writelines("|:--|:--|\n")

for key, val in data["wandering_monsters"].items():
    outfile.writelines("|" + key + "|" + val.replace("\n", " ") + "|\n")
    
outfile.writelines("}}\n")

""" dungeon exits & entrances """

outfile.writelines("### Exits and Entrances\n")
outfile.writelines("| Row | Column | Direction | Type | Level |\n")
outfile.writelines("|:--|:--|:--|:--|:--|\n")
for egress in data["egress"]:
    outfile.writelines("|" + str(egress["row"]) + "|" + str(egress["col"]) + "|" + str(egress["dir"]) + "|" + str(egress["type"]) + "|" + str(egress["depth"]) + "|\n")

""" rooms / locations """

if "rooms" in data:
    for rooms in data["rooms"]:
        if rooms is None:
            continue
        outfile.writelines("### Room " + str(rooms["id"]) + "\n")

        if "contents" in rooms:
            if "detail" in rooms["contents"]:

                """ traps """
                if "trap" in rooms["contents"]["detail"]:
                    outfile.writelines(":\n")
                    outfile.writelines("{{classTable,frame\n")
                    outfile.writelines("#### Trap!\n")
                    for item in rooms["contents"]["detail"]["trap"]:
                        desc = item.replace("\n","")
                        outfile.writelines(f'* {desc}\n')
                    
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
                            outfile.writelines("* " + item.replace("\n","") + "\n")
                    
                    outfile.writelines("}}\n")

                """ room description """
                if "room_features" in rooms["contents"]["detail"]:
                    outfile.writelines(":\n")
                    outfile.writelines("{{note\n")
                    outfile.writelines(rooms["contents"]["detail"]["room_features"] + ".\n")
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
                            outfile.writelines(":\n")
                            outfile.writelines("{{descriptive\n")
                            outfile.writelines("#### Treasure\n")
                            outfile.writelines(thing.replace("\n","") + "\n")
                            outfile.writelines("}}\n")
                        else:
                            outfile.writelines("::\n")
                            outfile.writelines("This room is occupied by **" + thing + "**\n")
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