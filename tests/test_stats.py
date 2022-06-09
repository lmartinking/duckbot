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

    assert con.sendAsync.call_count == 7
    con.sendAsync.call_args_list[0] == ("adduser", user.id, f"{user}")
    con.sendAsync.call_args_list[1] == ("addguild", guild.id, guild.name)
    con.sendAsync.call_args_list[2] == ("addchannel", channel.id, channel.name, guild.id)
    con.sendAsync.call_args_list[3] == ("adduserwords", "all", ["a", "big", "test", "message"])
    con.sendAsync.call_args_list[4] == ("adduserwords", "noun", ["test", "message"])
    con.sendAsync.call_args_list[5] == ("adduserwords", "adj", ["big"])
    con.sendAsync.call_args_list[6] == ("addmessage", message.id, channel.id, user.id, message.created_at.isoformat())

    con.close.assert_called_once()
