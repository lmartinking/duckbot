from unittest.mock import patch

import pytest

from duckbot import weather


@pytest.mark.asyncio
async def test_latest_mars_weather_prefers_curiosity():
    perserverence_reports = [
        {
            "terrestrial_date": "2000-01-01",
            "sol": "1",
            "min_temp": "-100",
            "max_temp": "-10",
        }
    ]
    curiosity_reports = [
        {
            "terrestrial_date": "2000-01-01",
            "sol": "2",
            "min_temp": "-200",
            "max_temp": "-100",
        }
    ]

    with patch("duckbot.weather.get_mars_weather", side_effect=[perserverence_reports, curiosity_reports]):
        weather.latest_mars_weather.cache_clear()
        w = await weather.latest_mars_weather()

    assert w.earth_date == "2000-01-01"
    assert w.sol == 2
    assert w.min_temp == -200
    assert w.max_temp == -100


@pytest.mark.asyncio
async def test_latest_mars_weather_filters_empty_data():
    perserverence_reports = [
        {
            "terrestrial_date": "2000-01-02",
            "sol": "1",
            "min_temp": "-100",
            "max_temp": "-10",
        }
    ]
    curiosity_reports = [
        {
            "terrestrial_date": "2000-01-02",
            "sol": "2",
            "min_temp": "--",
            "max_temp": "--",
        },
        {
            "terrestrial_date": "2000-01-01",
            "sol": "2",
            "min_temp": "-200",
            "max_temp": "-100",
        },
    ]

    with patch("duckbot.weather.get_mars_weather", side_effect=[perserverence_reports, curiosity_reports]):
        weather.latest_mars_weather.cache_clear()
        w = await weather.latest_mars_weather()

    assert w.sol == 1
    assert w.earth_date == "2000-01-02"
