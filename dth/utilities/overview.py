"""Module providing tools to generate randomised content from donjon.bin.sh

NOTE: donjon.bin.sh's random generator pages call a small JSON RPC endpoint
internally to populate their tables (visible via browser devtools network
tab). We call that endpoint directly instead of rendering the page in a
headless browser and scraping the resulting HTML - this avoids depending on
requests-html/pyppeteer (which bundles/downloads its own Chromium and has
been unmaintained for years) just to read a JSON array of strings.

IMPORTANT - maintenance risk: `rpc-fantasy.fcgi` / `rpc-5e.fcgi` are
undocumented internal endpoints used by donjon.bin.sh's own front-end
JavaScript - they are not a published/versioned public API, so the URL,
parameters or response shape could change without notice and break these
functions. donjon.bin.sh's robots.txt (checked July 2026) allows crawling
generally ("Allow: /") and only restricts use of their content for AI
training; there's no published API terms of service either way. Request
volume from this tool is tiny (at most two requests per dungeon conversion
run), and the generated output already credits donjon.bin.sh with a link
back. If you rely on this heavily, consider reaching out to the site owner
(contact details on donjon.bin.sh) to confirm this kind of low-volume,
personal-use API access is fine.
"""

import requests

RPC_TIMEOUT = 10

# Identify ourselves honestly rather than spoofing a browser user agent -
# donjon.bin.sh doesn't publish an API, so being transparent about what is
# making the request (and why) is the polite/low-risk approach.
USER_AGENT = (
    "donjon-to-homebrewery/1.0 (+https://github.com/telboy007/donjon_to_homebrewery)"
)

REQUEST_HEADERS = {"User-Agent": USER_AGENT}


def generate_boss_treasure_horde(dungeon_level: int) -> str:
    """Fetch a random 5e treasure hoard for the given dungeon level"""
    url = "https://donjon.bin.sh/5e/random/rpc-5e.fcgi"
    params = {"type": "Treasure Hoard", "cr": dungeon_level, "n": 1}

    try:
        response = requests.get(
            url, params=params, headers=REQUEST_HEADERS, timeout=RPC_TIMEOUT
        )
        response.raise_for_status()
        results = response.json()
    except (requests.RequestException, ValueError):
        return ""

    if results and results[0]:
        return results[0]
    return ""


def generate_dungeon_graffiti(count: int = 10) -> list[str]:
    """Fetch a list of random dungeon graffiti lines"""
    url = "https://donjon.bin.sh/fantasy/random/rpc-fantasy.fcgi"
    params = {"type": "Dungeon Graffiti", "n": count}

    try:
        response = requests.get(
            url, params=params, headers=REQUEST_HEADERS, timeout=RPC_TIMEOUT
        )
        response.raise_for_status()
        results = response.json()
    except (requests.RequestException, ValueError):
        return []

    return [item for item in results if item]
