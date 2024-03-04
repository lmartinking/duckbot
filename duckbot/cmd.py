from typing import List

import asyncio
import logging
import textwrap
import random
import json

import sparklines

from discord import Guild, TextChannel, User, Message
from discord.ext import commands
from discord.ext.commands import view as commands_view

from . import kdb
from . config import FORTUNE_PATH, CAPYCOIN_HOST
from . capycoin import action_signup, action_funds, action_send
from . weather import latest_mars_weather


log = logging.getLogger('cmd')


def parse_obj(bot: commands.Bot, obj: str):
    if obj.startswith("<#") and obj.endswith(">"):
        chan_id = int(obj[2:-1])
        return bot.get_channel(chan_id)
    elif obj.startswith("<@") and obj.endswith(">"):
        user_id = int(obj[2:-1])
        return bot.get_user(user_id)
    if obj == "server":
        return obj


async def user_stats(con: kdb.QConnection, user: User) -> str:
    log.info(f"Stats for user: {user}")
    result = con("{ .j.j user_stats x }", user.id)
    result = json.loads(result)
    fmt_words = lambda x: ", ".join(x)
    spark = sparklines.sparklines(result['spark'])[0]
    message = textwrap.dedent(f"""
    Stats for `{user}`:
      • **Word count**: {result['total']}
      • **Top verbs**: {fmt_words(result['verbs'])}
      • **Top nouns**: {fmt_words(result['nouns'])}
      • **Top adjs**:  {fmt_words(result['adjs'])}
    Messages per day: `{spark}`
    """)
    return message


async def channel_stats(con: kdb.QConnection, channel: TextChannel) -> str:
    log.info(f"Stats for channel: {channel}")
    result = con("{ .j.j channel_stats x }", channel.id)
    result = json.loads(result)

    rows = ["`#%-2d %6d %s`" % (idx+1, row["messageid"], row["name"]) for idx, row in enumerate(result['topusers'])]
    rows = "\n".join(rows)

    fmt_words = lambda x: ", ".join(x)

    message = textwrap.dedent(f"""
    Stats for `{channel}`:
      • **Message count**: {result['total']}
      • **Top verbs**: {fmt_words(result['verbs'])}
      • **Top nouns**: {fmt_words(result['nouns'])}
      • **Top adjs**:  {fmt_words(result['adjs'])}
    Most chatty users:
    """) + rows
    return message


async def server_stats(con: kdb.QConnection, channel: TextChannel) -> List[str]:
    guild: Guild = channel.guild
    log.info(f"Stats for guild: {guild}")
    result = con("{ .j.j guild_stats x }", guild.id)
    result = json.loads(result)

    chan_rows = ["`#%-2d %6d %s`" % (idx+1, row["messages"], row["name"]) for idx, row in enumerate(result['channel_messages'])]
    chan_rows = "\n".join(chan_rows)

    user_rows = ["`#%-2d %6d %s`" % (idx+1, row["messages"], row["name"]) for idx, row in enumerate(result['user_messages'])]
    user_rows = "\n".join(user_rows)

    user_words_rows = ["`#%-2d %6d %s`" % (idx+1, row["wordcounts"], row["name"]) for idx, row in enumerate(result['user_word_counts'])]
    user_words_rows = "\n".join(user_words_rows)

    messages = [
        textwrap.dedent(f"""
        Stats for server `{guild}`:
          • **Total channels**: {result['total_channels']}
          • **Total messages**: {result['total_messages']}
          • **Active users**: {result['seen_users']}"""),

        textwrap.dedent(f"""
        Channel message counts:
        """) + chan_rows,

        textwrap.dedent(f"""
        User messages:
        """) + user_rows,

        textwrap.dedent(f"""
        User words:
        """) + user_words_rows,
    ]

    return messages


async def stats_command(ctx: commands.Context):
    channel: TextChannel = ctx.channel

    if len(ctx.args) != 1:
        await channel.send(f"The `stats` command only takes 1 parameter, a `@user` or `#channel`, or 'server'")
        return

    obj = parse_obj(ctx.bot, ctx.args[0])
    log.info(f"Stats target: {obj}")

    con = kdb.make_connection_from_config()

    # TODO: Use Jinja for better formatting

    if isinstance(obj, User):
        message = await user_stats(con, obj)
        await channel.send(message)

    if isinstance(obj, TextChannel):
        message = await channel_stats(con, obj)
        await channel.send(message)

    if obj == "server":
        messages = await server_stats(con, channel)
        for m in messages:
            await channel.send(m)


async def ping_command(ctx: commands.Context):
    channel: TextChannel = ctx.channel
    message: Message = ctx.message
    reply = f"{message.author.mention} pong!"
    await channel.send(reply)


async def sup_command(ctx: commands.Context):
    channel: TextChannel = ctx.channel
    message: Message = ctx.message
    choice = random.choice(["sup?", "sup!", "meh", "wazza!", r"¯\_(ツ)_/¯", "ಠ_ಠ", "(◉ω◉)", "(^o^)", ""])
    reply = f"{message.author.mention} {choice}"
    await channel.send(reply)


async def fortune_command(ctx: commands.Context):
    channel: TextChannel = ctx.channel
    proc = await asyncio.create_subprocess_exec(FORTUNE_PATH, stdout=asyncio.subprocess.PIPE)
    await proc.wait()
    output = await proc.stdout.read()
    reply = [f"> {l.decode('utf-8')}" for l in output.splitlines()]  # Quote the fortune output...
    await channel.send("\n".join(reply))


async def weather_command(ctx: commands.Context):
    channel: TextChannel = ctx.channel

    if len(ctx.args) != 1:
        await channel.send(f"The `weather` command only takes 1 parameter: `mars`")
        return

    obj = ctx.args[0]

    if obj == 'mars':
        w = await latest_mars_weather()
        msg = f"🪐 Mars weather on `{w.earth_date}`. Min: `{w.min_temp}` Max: `{w.max_temp}` Atmosphere: `{w.atmosphere}` UV: `{w.uv_index}`"
        await channel.send(msg)
    else:
        await channel.send(f"The `weather` command only supports Mars weather at the moment")


async def help_command(ctx: commands.Context):
    channel: TextChannel = ctx.channel
    message = textwrap.dedent("""
    I am a very basic bot at the moment. Currently I support:
     • `stats @user` - report on chat stats for a particular user
     • `stats #channel` - report on chat stats for a particular channel
     • `stats server` - report on chat stats for the current server
     • `fortune` - show a random fortune!
    """)
    if CAPYCOIN_HOST:
        message += textwrap.dedent("""
         • `coin signup` - create a new CapyCoin account
         • `coin send @user <amount>` - send <amount> coin to a particular user
         • `coin funds` - find out how many coin you have!
        """)
    await channel.send(message)


async def unhandled_command(ctx: commands.Context):
    log.info("Unhandled command: {ctx.command} args: {ctx.command.args}")


async def capycoin_command(ctx: commands.Context):
    log.info(f"CapyCoin command: {ctx}")

    channel: TextChannel = ctx.channel

    if not ctx.args:
        await channel.send(f"The `coin` command has the following actions: `signup`, `send`, `funds`")
        return

    action = ctx.args[0]

    message: Message = ctx.message
    action_user = message.author

    if action == 'signup':
        message = await action_signup(action_user)
        await channel.send(message)

    if action == 'send':
        if len(ctx.args) != 3:
            await channel.send("The `send` action needs a @user and an `amount`.")
            return

        obj = parse_obj(ctx.bot, ctx.args[1])

        log.info(f"CapyCoin Send target: {obj}")
        if isinstance(obj, User):
            amount = ctx.args[2]
            message = await action_send(action_user, obj, amount)
            await channel.send(message)

    if action == 'funds':
        message = await action_funds(action_user)
        await channel.send(message)


async def process_message(guild: Guild, channel: TextChannel, user: User, message: Message, bot: commands.Bot):
    cmd_toks = [t for t in message.content.split()]

    if cmd_toks[0] == bot.user.mention:
        cmd_toks = cmd_toks[1:]

    cmd, *args = cmd_toks

    log.info("Command: %s Args: %s", cmd, args)

    ctx = commands.Context(bot=bot, command=cmd, args=args, message=message, prefix=bot.user.mention, view=commands_view.StringView(''))
    cmd_map = {
        'help':  help_command,
        'stats': stats_command,
        'ping':  ping_command,
        'sup':   sup_command,
        'fortune': fortune_command,
        'coin':    capycoin_command,
        'weather': weather_command,
    }

    cmd = cmd_map.get(cmd, unhandled_command)
    await cmd(ctx)
