import json
import sys


# set check value
def set_check(check):
    """Count the number of characters in a file"""
    infile = open("homebrewery.txt", "r")
    data = infile.read()
    return len(data)


# add a page marker check
def file_size(check):
    """Count the number of characters in a file"""
    infile = open("homebrewery.txt", "r")
    data = infile.read()
    if (len(data) - check) > 2450:
        outfile = open("homebrewery.txt", "a")
        outfile.write("\page\n")
        outfile.close()
        return len(data)
    else:
        return check


# globals
check = 0

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
    outfile.write(f"![map]({sys.argv[2]}){{position:absolute;mix-blend-mode:color-burn;transform:rotate(-30deg);width:500%;top:-1000px;}}\n")
    outfile.write(":\n")

outfile.write("{{margin-top:225px}}\n")
outfile.write(f"# {data['settings']['name']}\n")
outfile.write("{{margin-top:25px}}\n")
outfile.write("{{wide\n")
outfile.write(f"##### {data['details']['history']}\n")
outfile.write("::\n")
outfile.write(f"##### A randomly generated D&D 5e donjon dungeon for APL{data['settings']['level']}\n")
outfile.write("::::\n")
outfile.write(f"##### Created using [Homebrewery](https://homebrewery.naturalcrit.com), [Donjon](https://donjon.bin.sh) and [donjon_to_homebrewery](https://github.com/telboy007/donjon_to_homebrewery)\n")
outfile.write("}}\n")
outfile.write("\page\n")

""" map page """
if len(sys.argv) == 3:
    outfile.write("## Map\n")
    outfile.write(f"![map]({sys.argv[2]}){{width:680px;}}\n")
    outfile.write("Courtesy of <a href=\"https://donjon.bin.sh\">donjon.bin.sh</a>\n")
    outfile.write("\page\n")

""" general features """

# picture, watercolour stain & credits
outfile.write("![dungeon entrance](https://imgur.com/IWsK6KL.png){position:absolute;mix-blend-mode:multiply;left:-200px;top:-50px}\n")
outfile.write("{{artist,top:-5px,right:10px,color:white\n")
outfile.write("##### Dungeon's Entrance\n")
outfile.write("[by Gaetano Caltabiano](https://www.artstation.com/ghendral)\n")
outfile.write("}}\n")
outfile.write("<!-- Full page stain -->\n")
outfile.write("![stain](https://i.imgur.com/H0ZaKgc.png){position:absolute;top:0px;left:0px;width:816px;-webkit-transform:scaleX(-1);transform:scaleX(-1);}\n")
outfile.write("{{artist,top:-5px,left:10px\n")
outfile.write("##### Full Page Watercolor Stains\n")
outfile.write("[by u/flameableconcrete](https://homebrewery.naturalcrit.com/share/SkKsdJmKf)\n")
outfile.write("}}\n")

outfile.write("## Description\n")

outfile.write("The dungeon has the following features, these may include skill checks to perform certain actions.\n")
outfile.write("{{descriptive\n")
outfile.write("#### General Features\n")
outfile.write("| Type | Detail |\n")
outfile.write("|:--|:--|\n")
outfile.write(f"| Floors | {data['details']['floor']} |\n")
outfile.write(f"| Walls | {data['details']['walls']} |\n")
outfile.write(f"| Temperature | {data['details']['temperature']} |\n")
outfile.write(f"| Lighting | {data['details']['illumination']} |\n")
outfile.write("}}\n")

""" corridor features """

outfile.write("Some of the corridors marked on the map have special features detailed below.\n")
outfile.write("{{descriptive\n")
outfile.write("#### Corridor Features\n")
outfile.write("| Type | Detail |\n")
outfile.write("|:--|:--|\n")

for key, val in data["corridor_features"].items():
    detail = val["detail"].replace("\n", " ")
    outfile.write(f"| {val['key']} | {detail} |\n")

outfile.write("}}\n")

""" wandering monsters """

outfile.write("## Random Encounters\n")

outfile.write("As well as the monsters occupying certain rooms in the dungeon, there are roaming groups with a specific goal.  This will help you place them in the dungeon or when the party encounter them.\n")
outfile.write("{{classTable,frame\n")
outfile.write("#### Wandering Monsters\n")
outfile.write("| Roll | Detail |\n")
outfile.write("|:--|:--|\n")

for key, val in data["wandering_monsters"].items():
    group = val.replace("\n", " ")
    outfile.write(f"| {key} | {group} |\n")
    
outfile.write("}}\n")
outfile.write("\page\n")

# set page marker check
outfile.close()
check = set_check(check)
outfile = open("homebrewery.txt", "a")

""" Locations """

outfile.write("## Locations\n")

for egress in data["egress"]:
    outfile.write("### Getting In\n")
    outfile.write(f"The entrance into this dungeon can be found on the GM version of the map at ***row: {egress['row']}*** and ***column: {egress['col']}***, which enters the {egress['type']} from the {egress['dir']}.\n")

""" rooms / locations """

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

                """ traps """
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

                """ hidden treasure """
                if "hidden_treasure" in rooms["contents"]["detail"]:
                    outfile.write("{{classTable,frame\n")
                    outfile.write("#### Hidden Treasure!\n")
                    for item in rooms["contents"]["detail"]["hidden_treasure"]:
                        if item == "--":
                            continue
                        else:
                            item = item.replace("\n","")
                            outfile.write(f"* {item}\n")
                    
                    outfile.write("}}\n")

                # check for page marker
                outfile.close()
                check = file_size(check)
                outfile = open("homebrewery.txt", "a")

                """ room description """
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

                """ monsters and treasure """
                if "monster" in rooms["contents"]["detail"]:
                    for thing in rooms["contents"]["detail"]["monster"]:
                        if thing == "--":
                            continue
                        elif thing.startswith("Treasure"):
                            thing.replace("\n","")
                            outfile.write(":\n")
                            outfile.write("{{descriptive\n")
                            outfile.write("#### Treasure\n")
                            outfile.write(f"{thing}\n")
                            outfile.write("}}\n")
                        else:
                            outfile.write("::\n")
                            outfile.write(f"This room is occupied by **{thing}**\n")

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

        """ exits """
        if "doors" in rooms:
            outfile.write("#### Exits\n")
            outfile.write("| Direction | Description | Leads to |\n")
            outfile.write("|:--|:--|:--|\n")

            for direction, door in rooms["doors"].items():
                for d in door:
                    if d["type"] == "trapped":
                        trap = d["trap"].replace("\n", "")
                        try:
                            outfile.write(f"| {direction} | {d['desc']} ***Trap:*** {trap} | {d['out_id']} |\n")
                        except:
                            outfile.write(f"| {direction} | {d['desc']} ***Trap:*** {trap} | n/a |\n")
                    elif d["type"] == "secret":
                        secret = d["secret"].replace("\n", "")
                        try:
                            outfile.write(f"| {direction} | {d['desc']} ***Secret:*** {secret} | {d['out_id']} |\n")
                        except:
                            outfile.write(f"| {direction} | {d['desc']} ***Secret:*** {secret} | n/a |\n")
                    else:
                        try:
                            outfile.write(f"| {direction} | {d['desc']} | {d['out_id']} |\n")
                        except:
                            outfile.write(f"| {direction} | {d['desc']} | n/a |\n")           

            outfile.write(":\n")
        
        # check for page marker
        outfile.close()
        check = file_size(check)
        outfile = open("homebrewery.txt", "a")

outfile.close()
