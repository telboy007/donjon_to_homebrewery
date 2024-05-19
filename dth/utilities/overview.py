"""Module providing tools to generate randomised content from donjon.bon.sh"""

from bs4 import BeautifulSoup
from requests_html import HTMLSession


def generate_boss_treasure_horde(dungeon_level: int) -> str | str:
    """Web scrape 5e donjon loot generator"""

    url = f"https://donjon.bin.sh/5e/random/#type=treasure;treasure-cr={dungeon_level};treasure-loot_type=treasure_hoard"
    session = HTMLSession()
    response = session.get(url)
    response.html.render()

    # parse the html and find the treasure
    soup = BeautifulSoup(response.html.html, "html.parser")
    contents = soup.find_all("div", class_="content")

    if contents:
        return contents[0].text
    return ""


def generate_dungeon_graffiti() -> str | str:
    """Web scrape 5e donjon loot generator"""

    url = "https://donjon.bin.sh/fantasy/random/#type=dungeon_graffiti"
    session = HTMLSession()
    response = session.get(url)
    response.html.render()

    # parse the html and find the table
    soup = BeautifulSoup(response.html.html, "html.parser")
    contents = soup.find_all("div", class_="content")

    if contents:
        return contents
    return ""
