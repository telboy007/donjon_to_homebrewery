"""Module providing tools to generate boss loot (5e only)"""

from bs4 import BeautifulSoup
from requests_html import HTMLSession


def generate_boss_treasure_horde(dungeon_level):
    """Web scrape 5e donjon loot generator"""

    url = f"https://donjon.bin.sh/5e/random/#type=treasure;treasure-cr={dungeon_level};treasure-loot_type=treasure_hoard"
    session = HTMLSession()
    response = session.get(url)
    response.html.render()

    # parse the html and find the treasure
    soup = BeautifulSoup(response.html.html, "html.parser")
    contents = soup.find_all("div", class_="content")

    if contents != []:
        return contents[0].text
    else:
        return ""
