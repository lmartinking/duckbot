from unittest.mock import Mock, patch, call, AsyncMock

import pytest

from duckbot.bot import DuckBot


def test_init_listeners():
    listen = Mock()

    with patch.object(DuckBot, 'listen', listen):
        bot = DuckBot()

        assert listen.call_count == 3
        assert listen.call_args_list[0] == call(bot.on_ready)
        assert listen.call_args_list[1] == call(bot.on_reaction_add)
        assert listen.call_args_list[2] == call(bot.on_message)


@pytest.mark.asyncio
@patch('duckbot.bot.cmd')
@patch('duckbot.bot.stats', new_callable=AsyncMock)
@patch('duckbot.bot.DuckBot.user')
async def test_on_message_normal_message(bot_user, stats, cmd):
    message = Mock(name='message')
    bot_user.mention = '<@1234>'
    message.content = 'hello there'

    await DuckBot().on_message(message)

    assert cmd.call_count == 0
    assert stats.process_message.called_once_with(message.channel.guild, message.channel, message.author, message)


@pytest.mark.asyncio
@patch('duckbot.bot.cmd')
@patch('duckbot.bot.stats')
@patch('duckbot.bot.DuckBot.user')
async def test_on_message_command_message(bot_user, stats, cmd):
    cmd.process_message = AsyncMock(name='process_message')

    message = Mock(name='message')
    bot_user.mention = '<@1234>'
    message.content = '<@1234> some command'

    bot = DuckBot()
    await bot.on_message(message)

    assert stats.call_count == 0
    assert cmd.process_message.called_once_with(message.channel.guild, message.channel, message.author, message, bot=bot)


@pytest.mark.asyncio
@patch('duckbot.bot.cmd')
@patch('duckbot.bot.stats')
@patch('duckbot.bot.DuckBot.user')
async def test_on_message_own_message(bot_user, stats, cmd):
    message = Mock(name='message')
    message.author = bot_user

    await DuckBot().on_message(message)

    assert stats.call_count == 0
    assert cmd.call_count == 0
