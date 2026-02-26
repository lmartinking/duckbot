from collections import namedtuple
from functools import cache


TAROT_DECK = {
    "Major Arcana": {
        "The Fool": "New beginnings, innocence, spontaneity",
        "The Magician": "Manifestation, resourcefulness, power",
        "The High Priestess": "Intuition, mystery, inner knowledge",
        "The Empress": "Nurturing, abundance, creativity",
        "The Emperor": "Authority, structure, leadership",
        "The Hierophant": "Tradition, spiritual wisdom, conformity",
        "The Lovers": "Union, choices, alignment of values",
        "The Chariot": "Determination, control, victory",
        "Strength": "Courage, compassion, inner power",
        "The Hermit": "Soul-searching, introspection, guidance",
        "Wheel of Fortune": "Change, cycles, fate",
        "Justice": "Fairness, truth, accountability",
        "The Hanged Man": "Surrender, new perspective, pause",
        "Death": "Transformation, endings, rebirth",
        "Temperance": "Balance, moderation, harmony",
        "The Devil": "Attachment, temptation, materialism",
        "The Tower": "Sudden upheaval, revelation, collapse",
        "The Star": "Hope, renewal, inspiration",
        "The Moon": "Illusion, fear, subconscious",
        "The Sun": "Joy, success, vitality",
        "Judgement": "Awakening, reckoning, renewal",
        "The World": "Completion, fulfillment, integration",
    },
    "Minor Arcana": {
        "Wands": {
            "Ace": "Inspiration, new opportunity",
            "Two": "Planning, future direction",
            "Three": "Expansion, progress",
            "Four": "Celebration, stability",
            "Five": "Conflict, competition",
            "Six": "Victory, recognition",
            "Seven": "Defense, perseverance",
            "Eight": "Speed, swift movement",
            "Nine": "Resilience, persistence",
            "Ten": "Burden, responsibility",
            "Page": "Exploration, enthusiasm",
            "Knight": "Action, impulsiveness",
            "Queen": "Confidence, independence",
            "King": "Vision, leadership",
        },
        "Cups": {
            "Ace": "New love, emotional beginning",
            "Two": "Partnership, mutual attraction",
            "Three": "Friendship, celebration",
            "Four": "Apathy, contemplation",
            "Five": "Loss, regret",
            "Six": "Nostalgia, childhood memories",
            "Seven": "Illusion, choices",
            "Eight": "Walking away, seeking deeper meaning",
            "Nine": "Satisfaction, wishes fulfilled",
            "Ten": "Emotional harmony, family happiness",
            "Page": "Creativity, emotional openness",
            "Knight": "Romance, charm",
            "Queen": "Compassion, emotional depth",
            "King": "Emotional balance, diplomacy",
        },
        "Pentacles": {
            "Ace": "New financial opportunity",
            "Two": "Balance, adaptability",
            "Three": "Teamwork, collaboration",
            "Four": "Control, holding on",
            "Five": "Financial hardship, isolation",
            "Six": "Generosity, support",
            "Seven": "Patience, long-term growth",
            "Eight": "Skill-building, diligence",
            "Nine": "Independence, luxury",
            "Ten": "Wealth, legacy",
            "Page": "Learning, ambition",
            "Knight": "Reliability, hard work",
            "Queen": "Practicality, nurturing",
            "King": "Prosperity, stability",
        },
        "Swords": {
            "Ace": "Clarity, truth",
            "Two": "Indecision, stalemate",
            "Three": "Heartbreak, sorrow",
            "Four": "Rest, recovery",
            "Five": "Conflict, defeat",
            "Six": "Transition, moving on",
            "Seven": "Deception, strategy",
            "Eight": "Restriction, self-doubt",
            "Nine": "Anxiety, worry",
            "Ten": "Betrayal, painful ending",
            "Page": "Curiosity, vigilance",
            "Knight": "Assertiveness, haste",
            "Queen": "Perceptiveness, independence",
            "King": "Authority, intellect",
        },
    },
}


Card = namedtuple("Card", ["name", "meaning"])


@cache
def get_all_cards() -> list[Card]:
    cards = []
    for suit, ranks in TAROT_DECK["Minor Arcana"].items():
        for rank in ranks:
            c = Card(f"{rank} of {suit}", TAROT_DECK["Minor Arcana"][suit][rank])
            cards.append(c)
    for card in TAROT_DECK["Major Arcana"]:
        cards.append(Card(card, TAROT_DECK["Major Arcana"][card]))
    return cards


def draw_cards(count: int) -> list[Card]:
    import random

    all_cards = get_all_cards()
    return random.sample(all_cards, count)
