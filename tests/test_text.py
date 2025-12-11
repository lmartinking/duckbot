from unittest import SkipTest

from duckbot.text import tokens, plain, verbs, nouns, adjs, LANGUAGE_MODEL


if LANGUAGE_MODEL != "en_core_web_md":
    raise SkipTest("These tests assume a particular language model")


def test_tokens():
    toks = tokens("This is a bot")
    assert len(toks) == 4


def test_tokens_with_contractions():
    toks = tokens("That's said he's good")
    assert len(toks) == 6


def test_plain():
    assert ["This", "is", "a", "bot"] == plain(tokens("This is a bot"))


def test_verbs():
    assert ["running"] == verbs(tokens("big running bot"))


def test_nouns():
    assert ["bot"] == nouns(tokens("big running bot"))


def test_adjs():
    assert ["big"] == adjs(tokens("big running bot"))
