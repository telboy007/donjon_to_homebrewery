# donjon_to_homebrewery
Converts 5e donjon random dungeons into nice homebrewery v3 formatted text to copy and paste.

NOTE: don't forget to grab the map from donjon as well as the json! :)

To use:
1. Clone repo
1. Copy json from donjon into repo folder
1. cd into repo
1. `pip install pipenv`
1. `pipenv shell`
1. `python convert_donjon_to_homebrewery.py your_filename.json`

Optional:
1. You can provide a url as a second command line argument for an image of the map
1. `python convert_donjon_to_homebrewery.py your_filename.json https://imgur.something.png`

You can now copy and paste the contents of homebrewery.txt into your [homebrewery](https://homebrewery.naturalcrit.com/) document.

