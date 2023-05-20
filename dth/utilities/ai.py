"""Module providing chatgpt api helper functions"""
import os
import openai
from dotenv import load_dotenv

load_dotenv()

# ai prompts
DUNGEON_FLAVOUR_PROMPT = "Expand the following text for a {0} dungeon adding excitement, drama and suspense in a few parapgraphs.  Only talk about details, sights and sounds of the dungeon's entrance and not inside the dungeon and make no reference to skill checks. For reference the dungeon details are {1}): {2}"
DUNGEON_BOSS_AND_LAIR_PROMPT = "Based on following text what {0} monster should be the boss of the dungeon and what would it's lair look like based on {1}: {2}?"
ADVENTURE_HOOKS_PROMPT = "Please suggest two adventure hooks for a {0} dungeon based on {1} and {2}, with contact points and relevant names."


def send_prompt_to_chatgpt(prompt):
    """ Send prompt text to chatgpt and return response """
    openai.api_key = os.getenv("CHATGPT_TOKEN")
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": f"{prompt}"}
        ]
    )
    return completion.choices[0].message["content"]


def expand_dungeon_overview_via_ai(rule_set, blurb, dungeon_detail):
    """ Asks ChatGPT to suggest a dungeon boss and lair flavour text """
    prompt_text = DUNGEON_FLAVOUR_PROMPT.format(rule_set, blurb, dungeon_detail)
    try:
        response = send_prompt_to_chatgpt(prompt_text)
    except Exception as error:
        raise SystemError(error) from error

    return response


def suggest_a_bbeg_via_ai(rule_set, blurb, dungeon_detail):
    """ Asks ChatGPT to suggest two adventure hooks for the dungeon """
    prompt_text = DUNGEON_BOSS_AND_LAIR_PROMPT.format(rule_set, blurb, dungeon_detail)
    try:
        response = send_prompt_to_chatgpt(prompt_text)
    except Exception as error:
        raise SystemError(error) from error

    return response


def suggest_adventure_hooks_via_ai(rule_set, dungeon_detail, dungeon_boss):
    """ Asks ChatGPT to suggest a dungeon boss and lair details """
    prompt_text = ADVENTURE_HOOKS_PROMPT.format(rule_set, dungeon_detail, dungeon_boss)
    try:
        response = send_prompt_to_chatgpt(prompt_text)
    except Exception as error:
        raise SystemError(error) from error

    return response
