from typing import List, Dict

import aiohttp
from dataclasses import dataclass
from datetime import date
from async_lru import alru_cache

# This weather report is delayed but has more interesting information
URL_CURIOSITY = "https://mars.nasa.gov/rss/api/?feed=weather&category=msl&feedtype=json"

# This weather report is more up to date
URL_PERSERVERENCE = "https://mars.nasa.gov/rss/api/?feed=weather&category=mars2020&feedtype=json"


@dataclass
class WeatherReport:
    earth_date: str
    sol: str
    min_temp: float = None
    max_temp: float = None
    atmosphere: str = None
    uv_index: str = None


async def get_mars_weather(feed_url: str) -> List[Dict]:
    async with aiohttp.ClientSession() as session:
        async with session.get(feed_url) as r:
            d = await r.json()
            events = d.get('sols') or d.get('soles')
            events.sort(key=lambda x: int(x['sol']), reverse=True)
            return events


def blank_to_none(v):
    if v == "--":
        return None
    return v


def convert_feed_item(v: Dict) -> WeatherReport:
    atmosphere = blank_to_none(v.get('atmo_opacity'))
    uv_index=blank_to_none(v.get('local_uv_irradiance_index'))
    min_temp = blank_to_none(v['min_temp'])
    max_temp = blank_to_none(v['max_temp'])

    return WeatherReport(
        earth_date=v['terrestrial_date'],
        sol=int(v['sol']) if v['sol'] else None,
        min_temp=float(min_temp) if min_temp else None,
        max_temp=float(max_temp) if max_temp else None,
        atmosphere=atmosphere,
        uv_index=uv_index,
    )


def parse_earth_date(v: str) -> date:
    parts = [int(x) for x in v.split("-")]
    return date(year=parts[0], month=parts[1], day=parts[2])


@alru_cache(ttl=21600.0)
async def latest_mars_weather() -> WeatherReport:
    d1 = await get_mars_weather(URL_PERSERVERENCE)
    d2 = await get_mars_weather(URL_CURIOSITY)
    w1 = convert_feed_item(d1[0])
    w2 = convert_feed_item(d2[0])
    # Pick the latest report, with a preference towards Curiosity
    if parse_earth_date(w2.earth_date) >= parse_earth_date(w1.earth_date):
        return w2
    return w1
