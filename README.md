[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Homebrewery v3](https://img.shields.io/badge/homebrewery-v3-blue.svg)](https://homebrewery.naturalcrit.com/)

# donjon_to_homebrewery
Converts certain [donjon](https://donjon.bin.sh) random dungeons into nice homebrewery v3 formatted text to copy and paste.

NOTE: It will add page markers to break up room locations, but some minor edits may still be required.

Tested with (but YMMV):
1. AD&D
1. D&D 4e
1. D&D 5e

NOTE: don't forget to grab both maps (gm and player) from donjon as well as the json! :)

To use:
1. Clone repo
1. Copy json from donjon into repo folder
1. cd into repo
1. `pip install pipenv`
1. `pipenv shell`
1. `python convert_donjon_to_homebrewery.py your_filename.json`

Optional:
1. You can provide a url as a second and third command line argument for the gm and player maps (in that order)
1. `python convert_donjon_to_homebrewery.py your_filename.json https://imgur.something.png https://imgur.something.png`

You can now copy and paste the contents of homebrewery.txt into your [homebrewery](https://homebrewery.naturalcrit.com/) document.
