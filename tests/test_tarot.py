from duckbot.tarot import get_all_cards, draw_cards


TAROT_DECK_SIZE = 78


def test_get_all_cards():
    cards = get_all_cards()
    assert len(cards) == TAROT_DECK_SIZE

    for name, meaning in cards:
        assert isinstance(name, str)
        assert isinstance(meaning, str)
        assert len(name) > 0
        assert len(meaning) > 0


def test_draw_cards():
    drawn = draw_cards(3)
    assert len(drawn) == 3

    all_cards = draw_cards(TAROT_DECK_SIZE)
    assert len(all_cards) == TAROT_DECK_SIZE
    assert len(set(all_cards)) == TAROT_DECK_SIZE  # Ensure all cards are unique
