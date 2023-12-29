"""Module providing chatgpt api helper functions"""
import os
import openai
from dotenv import load_dotenv

load_dotenv()

# ai prompts
DUNGEON_FLAVOUR_PROMPT = "Enhance following text by adding drama and suspense using at most 3 paragraphs in present tense. Mention details, sights and sounds of the entrance but not inside the dungeon.  No reference to skill checks. Ruleset is {0}. Dungeon details are {1}: {2}"
DUNGEON_BOSS_AND_LAIR_PROMPT = "Suggest a monster from the {0} ruleset to be the dungeon boss, party size of {3}, average party level of {4}, description of {1} and features of {2}.  Describe the lair and how the boss will use it to it's advantage."
ADVENTURE_HOOKS_PROMPT = "Suggest two adventure hooks for a {0} dungeon based on {1} and {2}, with named NPC contact points."


def send_prompt_to_chatgpt(prompt):
    """Send prompt text to chatgpt and return response"""
    openai.api_key = os.getenv("CHATGPT_TOKEN")
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": f"{prompt}"}]
    )
    return completion.choices[0].message["content"]


def expand_dungeon_overview_via_ai(rule_set, blurb, dungeon_detail):
    """Asks ChatGPT to suggest a dungeon boss and lair flavour text"""
    prompt_text = DUNGEON_FLAVOUR_PROMPT.format(rule_set, blurb, dungeon_detail)
    try:
        response = send_prompt_to_chatgpt(prompt_text)
    except Exception as error:
        raise SystemError(error) from error

    return response


def suggest_a_bbeg_via_ai(rule_set, blurb, dungeon_detail, party_size, dungeon_level):
    """Asks ChatGPT to suggest two adventure hooks for the dungeon"""
    prompt_text = DUNGEON_BOSS_AND_LAIR_PROMPT.format(
        rule_set, blurb, dungeon_detail, party_size, dungeon_level
    )
    try:
        response = send_prompt_to_chatgpt(prompt_text)
    except Exception as error:
        raise SystemError(error) from error

    return response


def suggest_adventure_hooks_via_ai(rule_set, dungeon_detail, dungeon_boss):
    """Asks ChatGPT to suggest a dungeon boss and lair details"""
    prompt_text = ADVENTURE_HOOKS_PROMPT.format(rule_set, dungeon_detail, dungeon_boss)
    try:
        response = send_prompt_to_chatgpt(prompt_text)
    except Exception as error:
        raise SystemError(error) from error

    return response
