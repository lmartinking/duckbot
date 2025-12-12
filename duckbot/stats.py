import logging

from contextlib import closing

from discord import Guild, TextChannel, User, Message, Reaction

from .kdb import make_connection_from_config
from .text import tokens, plain, verbs, nouns, adjs


log = logging.getLogger('stats')


async def process_reaction(guild: Guild, channel: TextChannel, reaction: Reaction):
    # TODO...
    pass


async def process_message(guild: Guild, channel: TextChannel, user: User, message: Message):
    log.info(f"process_message: guild: {guild} channel: {channel} user: {user} text: `{message.content}`")

    # Message parsing
    msg_toks = tokens(message.content)

    msg_plain = plain(msg_toks)
    msg_verbs = verbs(msg_toks)
    msg_nouns = nouns(msg_toks)
    msg_adjs  = adjs(msg_toks)

    log.info("Message tokens: %s", msg_toks)

    with closing(make_connection_from_config()) as con:
        con.asyn("adduser", user.id, f"{user}")
        con.asyn("addguild", guild.id, guild.name)
        con.asyn("addchannel", channel.id, channel.name, guild.id)

        for word_type, word_list in (("all", msg_plain), ("verb", msg_verbs), ("noun", msg_nouns), ("adj", msg_adjs)):
            if word_list:
                con.asyn("adduserwords", user.id, word_type, word_list)

                # For collecting overall word stats per channel
                con.asyn("adduserwords", channel.id, word_type, word_list)

        if not message.edited_at:
            timestamp = message.created_at.isoformat()
            con.asyn("addmessage", message.id, channel.id, user.id, timestamp)
