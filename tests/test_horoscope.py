import pytest


@pytest.mark.asyncio
async def test_get_horoscope(subtests):
    from duckbot.horoscope import get_horoscope, icon_for_sign, SCOPES_WESTERN, SCOPES_CHINESE
    for sign in SCOPES_WESTERN + SCOPES_CHINESE:
        with subtests.test(sign=sign):
            icon = icon_for_sign(sign)
            horoscope = await get_horoscope(sign)
            assert horoscope is not None, f"Horoscope for {sign} should not be None"
            assert sign.lower() in horoscope.lower(), f"Horoscope text for {sign} should contain the sign name"
            assert icon in horoscope, f"Horoscope text for {sign} should contain the icon {icon}"
