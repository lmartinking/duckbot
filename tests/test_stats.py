from unittest.mock import Mock, AsyncMock, patch

import pytest

import duckbot.stats


@pytest.mark.asyncio
async def test_process_message():
    guild = Mock(name='guild')
    user = Mock(name='user')
    channel = Mock(name='channel')
    message = Mock(name='message')
    message.content = "a big test message"
    message.edited_at = None

    con = Mock(name='con')

    make_connection_from_config = Mock('make_connection_from_config', return_value=con)

    with patch("duckbot.stats.make_connection_from_config", make_connection_from_config):
        await duckbot.stats.process_message(guild, channel, user, message)

    make_connection_from_config.assert_called_once()

    assert con.sendAsync.call_count == 10
    assert con.sendAsync.call_args_list[0].args == ("adduser", user.id, f"{user}")
    assert con.sendAsync.call_args_list[1].args == ("addguild", guild.id, guild.name)
    assert con.sendAsync.call_args_list[2].args == ("addchannel", channel.id, channel.name, guild.id)

    assert con.sendAsync.call_args_list[3].args == ("adduserwords", user.id, "all", ["a", "big", "test", "message"])
    assert con.sendAsync.call_args_list[4].args == ("adduserwords", channel.id, "all", ["a", "big", "test", "message"])

    assert con.sendAsync.call_args_list[5].args == ("adduserwords", user.id, "noun", ["test", "message"])
    assert con.sendAsync.call_args_list[6].args == ("adduserwords", channel.id, "noun", ["test", "message"])

    assert con.sendAsync.call_args_list[7].args == ("adduserwords", user.id, "adj", ["big"])
    assert con.sendAsync.call_args_list[8].args == ("adduserwords", channel.id, "adj", ["big"])

    assert con.sendAsync.call_args_list[9].args == ("addmessage", message.id, channel.id, user.id, message.created_at.isoformat(), 4)

    con.close.assert_called_once()
