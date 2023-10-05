import json
import textwrap

from unittest.mock import Mock, MagicMock, AsyncMock, patch, call, ANY

import pytest

from duckbot import cmd, weather


def make_command_mocks():
    return dict(
        help_command=AsyncMock(),
        stats_command=AsyncMock(),
        ping_command=AsyncMock(),
        sup_command=AsyncMock(),
        fortune_command=AsyncMock(),
        weather_command=AsyncMock(),
        unhandled_command=AsyncMock()
    )


@pytest.mark.asyncio
async def test_process_message_unhandled():
    message = Mock(name='message')
    message.content = '<@1234> blah blah'
    bot = Mock(name='bot')
    bot.user.mention = '<@1234>'

    with patch.multiple('duckbot.cmd', **make_command_mocks()):
        await cmd.process_message(None, None, None, message, bot=bot)

        assert cmd.help_command.call_count == 0
        assert cmd.stats_command.call_count == 0
        assert cmd.ping_command.call_count == 0
        assert cmd.sup_command.call_count == 0
        assert cmd.fortune_command.call_count == 0
        assert cmd.weather_command.call_count == 0

        assert cmd.unhandled_command.call_count == 1


@pytest.mark.asyncio
async def test_process_message_dispatch():
    message = Mock(name='message')
    message.content = '<@1234> fortune some more words'
    bot = Mock(name='bot')
    bot.user.mention = '<@1234>'

    with patch.multiple('duckbot.cmd', **make_command_mocks()):
        await cmd.process_message(None, None, None, message, bot=bot)

        assert cmd.help_command.call_count == 0
        assert cmd.stats_command.call_count == 0
        assert cmd.ping_command.call_count == 0
        assert cmd.sup_command.call_count == 0
        assert cmd.unhandled_command.call_count == 0

        ctx = cmd.commands.Context(
            bot=bot,
            command="fortune", args=["some", "more", "words"],
            message=message, prefix=bot.user.mention,
            view=cmd.commands_view.StringView(''))

        cmd.fortune_command.call_args == call(ctx)


@pytest.mark.asyncio
async def test_help_command():
    ctx = Mock(name='ctx', channel=AsyncMock())
    await cmd.help_command(ctx)
    ctx.channel.send.assert_called_once_with(ANY)


@pytest.mark.asyncio
async def test_sup_command():
    ctx = Mock(name='ctx', channel=AsyncMock())
    ctx.message.author.mention = '<@1234>'
    await cmd.sup_command(ctx)
    ctx.channel.send.call_args[0][0].startswith("<@1234> ")


@pytest.mark.asyncio
async def test_ping_command():
    ctx = Mock(name='ctx', channel=AsyncMock())
    ctx.message.author.mention = '<@1234>'
    await cmd.ping_command(ctx)
    ctx.channel.send.assert_called_once_with('<@1234> pong!')


@pytest.mark.asyncio
@patch('duckbot.cmd.latest_mars_weather')
async def test_weather_command_mars(latest_mars_weather):
    ctx = Mock(name='ctx', channel=AsyncMock())
    ctx.args = ['mars']
    latest_mars_weather.return_value = weather.WeatherReport(earth_date='2000-01-01', sol=123, min_temp=-100.0, max_temp=-10.0, atmosphere='Sunny', uv_index='Low')
    await cmd.weather_command(ctx)
    ctx.channel.send.assert_called_once_with('🪐 Mars weather on `2000-01-01`. Min: `-100.0` Max: `-10.0` Atmosphere: `Sunny` UV: `Low`')


@pytest.mark.asyncio
async def test_weather_command_no_args():
    ctx = Mock(name='ctx', channel=AsyncMock())
    ctx.args = []
    await cmd.weather_command(ctx)
    ctx.channel.send.assert_called_once_with('The `weather` command only takes 1 parameter: `mars`')


def test_parse_obj_channel():
    bot = Mock()
    bot.get_channel.return_value = "channel"
    assert cmd.parse_obj(bot, "<#1111>") == "channel"
    assert bot.get_channel.called_once_with(1111)


def test_parse_obj_user():
    bot = Mock()
    bot.get_user.return_value = "user"
    assert cmd.parse_obj(bot, "<@1234>") == "user"
    assert bot.get_user.called_once_with(1234)


def test_parse_obj_server():
    assert cmd.parse_obj(Mock('bot'), "server") == "server"


@pytest.mark.asyncio
@patch('duckbot.cmd.parse_obj')
@patch('duckbot.kdb.make_connection_from_config')
@patch('duckbot.cmd.user_stats')
async def test_stats_command_user(user_stats, make_connection_from_config, parse_obj):
    user = cmd.User(state=None, data=dict(username='user', id='1234', discriminator=1, avatar=None))

    ctx = Mock(name='Context', args=["<@1234>"])
    ctx.channel = AsyncMock(name='Channel')

    response_message = Mock('response_message')
    user_stats.return_value = response_message

    con = Mock(name='Connection')
    make_connection_from_config.return_value = con

    parse_obj.return_value = user

    await cmd.stats_command(ctx)

    parse_obj.assert_called_once_with(ctx.bot, ctx.args[0])
    user_stats.assert_called_once_with(con, user)
    ctx.channel.send.assert_called_once_with(response_message)


@pytest.mark.asyncio
@patch('duckbot.cmd.parse_obj')
@patch('duckbot.kdb.make_connection_from_config')
@patch('duckbot.cmd.channel_stats')
async def test_stats_command_channel(channel_stats, make_connection_from_config, parse_obj):
    user = cmd.TextChannel(state=None, guild=Mock(id=1), data=dict(name='chan', type='text', id=1234, position=0))

    ctx = Mock(name='Context', args=["<#1234>"])
    ctx.channel = AsyncMock(name='Channel')

    response_message = Mock('response_message')
    channel_stats.return_value = response_message

    con = Mock(name='Connection')
    make_connection_from_config.return_value = con

    parse_obj.return_value = user

    await cmd.stats_command(ctx)

    parse_obj.assert_called_once_with(ctx.bot, ctx.args[0])
    channel_stats.assert_called_once_with(con, user)
    ctx.channel.send.assert_called_once_with(response_message)


@pytest.mark.asyncio
@patch('duckbot.cmd.parse_obj')
@patch('duckbot.kdb.make_connection_from_config')
@patch('duckbot.cmd.server_stats')
async def test_stats_command_server(server_stats, make_connection_from_config, parse_obj):
    ctx = Mock(name='Context', args=["server"])
    ctx.channel = AsyncMock(name='Channel')

    response_message = Mock('response_message')
    server_stats.return_value = [response_message]

    con = Mock(name='Connection')
    make_connection_from_config.return_value = con

    parse_obj.return_value = "server"

    await cmd.stats_command(ctx)

    parse_obj.assert_called_once_with(ctx.bot, ctx.args[0])
    server_stats.assert_called_once_with(con, ctx.channel)
    ctx.channel.send.assert_called_once_with(response_message)


@pytest.mark.asyncio
async def test_user_stats():
    user = MagicMock(name='User')
    user.__str__.return_value = '<User>'

    result = {
        'total': 4,
        'verbs': ['a', 'b'],
        'nouns': ['c', 'd'],
        'adjs':  ['e', 'f'],
        'spark': [0, 1, 0, 1],
    }

    con = Mock(name='Connection')
    con.return_value = json.dumps(result)

    msg = await cmd.user_stats(con, user)

    assert msg == textwrap.dedent("""
    Stats for `<User>`:
      • **Word count**: 4
      • **Top verbs**: a, b
      • **Top nouns**: c, d
      • **Top adjs**:  e, f
    Messages per day: `▁█▁█`
    """)


@pytest.mark.asyncio
async def test_channel_stats():
    chan = MagicMock(name='Channel')
    chan.__str__.return_value = '<Channel>'

    result = {
        'total': 4,
        'verbs': ['a', 'b'],
        'nouns': ['c', 'd'],
        'adjs':  ['e', 'f'],
        'topusers': [
            {'messageid': 10, 'name': 'user1' },
            {'messageid': 5,  'name': 'user2' },
        ],
    }

    con = Mock(name='Connection')
    con.return_value = json.dumps(result)

    msg = await cmd.channel_stats(con, chan)

    assert msg == textwrap.dedent("""
    Stats for `<Channel>`:
      • **Message count**: 4
      • **Top verbs**: a, b
      • **Top nouns**: c, d
      • **Top adjs**:  e, f
    Most chatty users:
    `#1      10 user1`
    `#2       5 user2`""")


@pytest.mark.asyncio
async def test_server_stats():
    chan = MagicMock(name='Channel')
    chan.__str__.return_value = '<Channel>'
    chan.guild = MagicMock(name='Guild')
    chan.guild.__str__.return_value = '<Guild>'

    result = {
        'total_channels': 4,
        'total_messages': 10,
        'seen_users': 2,
        'channel_messages': [
            {'messages': 10, 'name': 'channel1' },
            {'messages': 5,  'name': 'channel2' },
        ],
        'user_messages': [
            {'messages': 100, 'name': 'user1' },
            {'messages': 50,  'name': 'user2' },
        ],
        'user_word_counts': [
            {'wordcounts': 1000, 'name': 'user1' },
            {'wordcounts': 500,  'name': 'user2' },
        ]
    }

    con = Mock(name='Connection')
    con.return_value = json.dumps(result)

    msgs = await cmd.server_stats(con, chan)

    assert msgs[0] == textwrap.dedent("""
    Stats for server `<Guild>`:
      • **Total channels**: 4
      • **Total messages**: 10
      • **Active users**: 2""")

    assert msgs[1] == textwrap.dedent("""
    Channel message counts:
    `#1      10 channel1`
    `#2       5 channel2`""")

    assert msgs[2] == textwrap.dedent("""
    User messages:
    `#1     100 user1`
    `#2      50 user2`""")

    assert msgs[3] == textwrap.dedent("""
    User words:
    `#1    1000 user1`
    `#2     500 user2`""")
