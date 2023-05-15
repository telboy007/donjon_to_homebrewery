"""Module providing chatgpt api helper functions"""
import os
import openai
from dotenv import load_dotenv

load_dotenv()


def expand_dungeon_overview_via_ai(blurb, dungeon_details):
    """ Asks ChatGPT to suggest dungeon flavour text """
    openai.api_key = os.getenv("CHATGPT_TOKEN")
    try:
        completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Expand on the description of a D&D 5e dungeon adding excitement, drama and suspense.  Only talk about details, sights and sounds of the dungeon's entrance and not inside.  Make no reference to skill checks or ft. (for reference the dungeon details are {dungeon_details}): {blurb}"}
            ]
        )
    except Exception as error:
        raise SystemError(error) from error

    return completion.choices[0].message["content"]


def suggest_a_bbeg_via_ai(expanded_description, dungeon_detail):
    """ Asks ChatGPT to suggest a dungeon boss and lair details """
    openai.api_key = os.getenv("CHATGPT_TOKEN")
    try:
        completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Based on the following text what D&D 5e monster should be the boss of the dungeons and what would their lair look like based on {dungeon_detail}: {expanded_description}"}
            ]
        )
    except Exception as error:
        raise SystemError(error) from error

    return completion.choices[0].message["content"]
