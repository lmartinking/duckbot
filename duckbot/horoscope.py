from typing import Optional, Callable

import aiohttp
import logging
from async_lru import alru_cache

from parsel import Selector


log = logging.getLogger("bot")


SCOPES_WESTERN = ("aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces")
SCOPES_WESTERN_ICONS = ("♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓")

SCOPES_CHINESE = ("rat", "ox", "tiger", "rabbit", "dragon", "snake", "horse", "goat", "monkey", "rooster", "dog", "pig")
SCOPES_CHINESE_ICONS = ("🐀", "🐂", "🐅", "🐇", "🐉", "🐍", "🐎", "🐐", "🐒", "🐓", "🐕", "🐖")


def icon_for_sign(sign: str) -> Optional[str]:
    if sign.lower() in SCOPES_WESTERN:
        return SCOPES_WESTERN_ICONS[SCOPES_WESTERN.index(sign.lower())]
    if sign.lower() in SCOPES_CHINESE:
        return SCOPES_CHINESE_ICONS[SCOPES_CHINESE.index(sign.lower())]
    return None


def url_for_sign(sign: str) -> str:
    if sign in SCOPES_WESTERN:
        return f"https://www.astrology.com/horoscope/daily/{sign.lower()}.html"
    if sign in SCOPES_CHINESE:
        # These are not in "calendar" order, so we need to map them to the correct index
        idx_map = {
            "ox": 1,
            "goat": 2,
            "rat": 3,
            "snake": 4,
            "dragon": 5,
            "tiger": 6,
            "rabbit": 7,
            "horse": 8,
            "monkey": 9,
            "rooster": 10,
            "dog": 11,
            "pig": 12,
        }
        idx = idx_map[sign.lower()]
        return f"https://www.horoscope.com/us/horoscopes/chinese/horoscope-chinese-daily-today.aspx?sign={idx}"


def parser_for_sign(sign: str) -> Optional[Callable]:
    if sign in SCOPES_WESTERN:
        return parse_astrology_com_scope_page
    if sign in SCOPES_CHINESE:
        return parse_horoscope_com_scope_page
    return None


async def fetch_html(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            return await r.text()


def parse_astrology_com_scope_page(html: str) -> Optional[str]:
    sel = Selector(text=html)
    if p := sel.css("div#content p").get():
        inner = Selector(text=p)
        return " ".join(inner.css("::text").getall()).strip()


def parse_horoscope_com_scope_page(html: str) -> Optional[str]:
    sel = Selector(text=html)
    if p := sel.css("div.main-horoscope p").get():
        inner = Selector(text=p)
        return " ".join(inner.css("::text").getall()).strip()


@alru_cache(ttl=3600)
async def get_horoscope(sign: str) -> Optional[str]:
    if sign.lower() not in (SCOPES_WESTERN + SCOPES_CHINESE):
        return None
    url = url_for_sign(sign)
    html = await fetch_html(url)
    parser = parser_for_sign(sign)
    text = parser(html) if parser else None
    if not text:
        return None
    icon = icon_for_sign(sign) or ""
    text = f"{icon} **{sign.capitalize()}**: {text}"
    return text
