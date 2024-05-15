"""Module providing chatgpt api helper functions"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ai prompts
DUNGEON_FLAVOUR_PROMPT = "Enhance the dungeon description using maximum 3 paragraphs in present tense. Mention details, sights and sounds of the entrance but not inside the dungeon.  No reference to skill checks. Ruleset is {0}. Dungeon description is {1}: {2}"
DUNGEON_BOSS_AND_LAIR_PROMPT = "Suggest a monster from the {0} ruleset to be the dungeon boss based on the dungeon's description of {1} and features of {2}.  It should be a challenge for a party size of {3}, and average party level of {4}.  Describe the lair and up to three lair actions the dungeon boss will use."
ADVENTURE_HOOKS_PROMPT = "Suggest two adventure hooks for a {0} dungeon based on it's description of {1} and features of {2}, including named NPC contact points and their flavour text."


def send_prompt_to_chatgpt(prompt: str) -> str:
    """Send prompt text to chatgpt and return response"""
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        organization=os.getenv("OPENAI_ORG"),
        project=os.getenv("OPENAI_PROJECT_ID"),
    )

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are helping enhance a D&D 5e dungeon crawl adventure by providing evocative and dramatic suggestions.",
            },
            {"role": "user", "content": f"{prompt}"},
        ],
    )
    return completion.choices[0].message.content


def expand_dungeon_overview_via_ai(
    rule_set: str, blurb: str, dungeon_detail: str
) -> str:
    """Asks ChatGPT to expand the descripton of the dungeon"""
    prompt_text = DUNGEON_FLAVOUR_PROMPT.format(rule_set, blurb, dungeon_detail)
    try:
        response = send_prompt_to_chatgpt(prompt_text)
    except Exception as error:
        raise SystemError(error) from error

    return response


def suggest_a_bbeg_via_ai(
    rule_set: str, blurb: str, dungeon_detail: str, party_size: int, dungeon_level: int
) -> str:
    """Asks ChatGPT to suggest a dungeon boss and lair flavour text"""
    prompt_text = DUNGEON_BOSS_AND_LAIR_PROMPT.format(
        rule_set, blurb, dungeon_detail, party_size, dungeon_level
    )
    try:
        response = send_prompt_to_chatgpt(prompt_text)
    except Exception as error:
        raise SystemError(error) from error

    return response


def suggest_adventure_hooks_via_ai(
    rule_set: str, dungeon_detail: str, dungeon_boss: str
) -> str:
    """Asks ChatGPT to suggest two adventure hooks for the dungeon"""
    prompt_text = ADVENTURE_HOOKS_PROMPT.format(rule_set, dungeon_detail, dungeon_boss)
    try:
        response = send_prompt_to_chatgpt(prompt_text)
    except Exception as error:
        raise SystemError(error) from error

    return response
