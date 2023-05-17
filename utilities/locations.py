"""Module providing location / room helper functions"""
magic_items = {}
combat_list = []
monster_list = []
xp_list = []


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


def compile_monster_and_combat_details(string, infest):
    """ compiles ref table for monsters - 4e and 5e only """
    if infest == "dnd_5e":
        # get monster name and book details and add to list
        monsters_and_combat = string.split(';')
        monsters = monsters_and_combat[0].split(' and ')
        print(f"input {monsters}")
        for monster in monsters:
            if ' x ' in monster:
                monster = monster.split(' x ')[1]
                monster_list.append(monster.strip())
                print(f"if {monster_list}")
            else:
                monster_list.append(monster.strip())
                print(f"else {monster_list}")
        # get combat type and add to list
        combat = monsters_and_combat[1].split(',')
        combat_list.append(combat[0].strip())
        # get xp amount and add to list
        xp_amount = combat[1].strip().split(' ')
        xp_list.append(xp_amount[0].strip())
        return monster_list, combat_list, xp_list
    if infest == "dnd_4e":
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
        return monster_list
    return None


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
