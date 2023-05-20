"""Module providing location / room helper functions"""


def sum_up_treasure(string, infest):
    """5e random dungeons can end up having lots of little currency amounts"""
    if infest == "dnd_5e":
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
        return f"{str(result[:-2]).replace(',;', ',')}"
    return None


def add_magical_items_to_list(string, room_loc):
    """ 
        compiles ref table for magic items - 5e only 
        format: magic_item[name (quantity if applicable)] = dmg page number/room location id    
    """
    magic_items = {}
    raw_magic_items = string.split(',')
    for index, raw_magic_item in enumerate(raw_magic_items):
        if 'dmg' in raw_magic_item:
            item_name = format_magic_item_name(raw_magic_items[index - 1])
            magic_items[item_name] = f"{raw_magic_item.strip().replace(')', '').replace(' ', ' p.')}/{room_loc}"

    return magic_items


def format_magic_item_name(item_name):
    """ nicely format magic item names """
    if ' x ' in item_name:
        singular_item = item_name.split(' x ')
        item_name = f"{singular_item[1].strip()} ({singular_item[0].strip()})"

    return item_name.replace('(uncommon','**U**').replace('(common','**C**').replace('(rare', '**R**').replace('(very rare', '**VR**').replace('(legendary', '**L**').replace('(artifact', '**A**').strip()


def compile_monster_and_combat_details(data, rule_set, final_list_of_monsters, combat_list, xp_list):
    """ compiles ref table for monsters based on rule set """
    if rule_set == "dnd_5e":
        encounter_details = []
        # decide if we have a list or a string to deal with
        if isinstance(data, list):
            for item in data:
                for key, value in item.items():
                    encounter_details.append(value)
        else:
            # add string as the single member of list
            encounter_details = [data]

        for encounter in encounter_details:
            monsters, combat = encounter.split(';')
            # can have more than one enemy type in monsters
            monster_list = monsters.split(' and ')
            combat_and_xp = combat.split(',')

            # deal with monsters
            for monster in monster_list:
                if ' x ' in monster:
                    monster = monster.split(' x ')[1]
                final_list_of_monsters.append(monster.strip())

            # deal with combats
            combat_list.append(combat_and_xp[0].strip())

            # get xp amount and add to list
            xp_list.append(combat_and_xp[1].strip().split(' ')[0].strip())

        return final_list_of_monsters, combat_list, xp_list
    if rule_set == "dnd_4e":
        encounter_details = []
        # decide if we have a list or a string to deal with
        if isinstance(data, list):
            for item in data:
                for key, value in item.items():
                    encounter_details.append(value)
        else:
            # add string as the single member of list
            encounter_details = [data]

        # get monster name and book details and add to list
        for encounter in encounter_details:
            monsters = encounter.split(') and ')

            # deal with monsters
            for monster in monsters:
                if ' x ' in monster:
                    monster = monster.split(' x ')[1]
                if ', ' in monster:
                    monster = monster.strip().split(',')
                final_list_of_monsters.append(monster[0])

                # get xp amount and add to list
                xp_list.append(monster[1].strip().split(' ')[0].strip())

        return final_list_of_monsters, combat_list, xp_list
    return [], [], []


def extract_book_details(book_details, infest):
    """ split out name and source book(s) (used on monster list) - 5e and 4e only"""
    if infest == "dnd_5e":
        split = book_details.split('(')
        name = split[0].strip()
        book_details = split[1].split(',')
        book = book_details[1].strip().replace(')','').replace(' ', ' p.')
        if len(book_details) > 2:
            book = f"{book} / {book_details[2].strip().replace(')','').replace(' ', ' p.')}"
        return name, book
    if infest == "dnd_4e":
        split = book_details.split('(')
        name = split[0].strip()
        book = split[1].strip().replace(' ', ' p.')
        return name, book
    return None
