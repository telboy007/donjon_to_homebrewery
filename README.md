[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Homebrewery v3](https://img.shields.io/badge/homebrewery-v3-blue.svg)](https://homebrewery.naturalcrit.com/)

# donjon_to_homebrewery
Converts [donjon](https://donjon.bin.sh) random dungeons into nice homebrewery v3 formatted text to copy and paste.  It will add page markers to break up room locations, but some minor edits may still be required to the final document.

This tool has been tested with:
1. AD&D
1. D&D 4e
1. D&D 5e

NOTE: don't forget to grab both maps (gm and player) from donjon as well as the json! :)

To install:
1. Clone repo
1. Copy json from donjon into repo folder
1. cd into repo
1. `pip install pipenv`
1. `pipenv shell` (NOTE: you may need to install pyenv to install python 3.8)

To run:
1. Run the command `python convert_donjon_to_homebrewery.py your_filename.json`
1. If you have the GM and Player maps, host them on an image hosting site and add the urls as arguments
  1. `python convert_donjon_to_homebrewery.py your_filename.json https://imgur.something.png https://imgur.something.png`

You can now copy and paste the contents of homebrewery.txt into your [homebrewery](https://homebrewery.naturalcrit.com/) document.

Troubleshooting:
1. Raise an issue here and if possible provide the json / json file that is causing problems.
