import pytest

from duckbot.horoscope import get_horoscope, icon_for_sign, fetch_and_parse_horoscope, SCOPES_WESTERN, SCOPES_CHINESE


@pytest.mark.asyncio
async def test_fetch_and_parse_horoscope(subtests):
    for sign in SCOPES_WESTERN + SCOPES_CHINESE:
        today_text = None
        for tomorrow in (False, True):
            with subtests.test(sign=sign, tomorrow=tomorrow):
                horoscope = await fetch_and_parse_horoscope(sign, tomorrow=tomorrow)
                assert horoscope is not None, f"Horoscope for {sign} should not be None"

                if not tomorrow:
                    today_text = horoscope
                else:
                    assert horoscope != today_text, f"Tomorrow's horoscope for {sign} should be different from today's"


@pytest.mark.asyncio
async def test_get_horoscope(subtests):
    for sign in SCOPES_WESTERN + SCOPES_CHINESE:
        with subtests.test(sign=sign):
            icon = icon_for_sign(sign)
            horoscope = await get_horoscope(sign)
            assert horoscope is not None, f"Horoscope for {sign} should not be None"
            assert sign.lower() in horoscope.lower(), f"Horoscope text for {sign} should contain the sign name"
            assert icon in horoscope, f"Horoscope text for {sign} should contain the icon {icon}"
