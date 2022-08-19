from typing import List

import spacy
import spacy.tokens.token
import contractions

from .config import LANGUAGE_MODEL


TokenList = List[spacy.tokens.token.Token]


nlp: spacy.Language = spacy.load(LANGUAGE_MODEL)


def tokens(text: str) -> TokenList:
    text = contractions.fix(text, slang=False)
    doc = nlp(text)
    toks = list(doc)
    return toks


def tokens_basic(text: str) -> List[str]:
    return [t.text for t in tokens(text) if not t.is_punct]


def tokens_by_type(toks: TokenList, typ: str):
    return [t.text for t in toks if t.pos_ == typ]


def plain(toks: TokenList) -> List[str]:
    return [t.text for t in toks if not t.is_punct]


def verbs(toks: TokenList) -> List[str]:
    return tokens_by_type(toks, "VERB")


def nouns(toks: TokenList) -> List[str]:
    return tokens_by_type(toks, "NOUN")


def adjs(toks: TokenList) -> List[str]:
    return tokens_by_type(toks, "ADJ")
