import logging

import discord
from discord.ext import commands

from . import stats
from . import cmd

log = logging.getLogger('bot')


class DuckBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.messages = True

        super().__init__(command_prefix='?', description='Duckbot!', intents=intents)

        self.listen(self.on_ready)
        self.listen(self.on_reaction_add)
        self.listen(self.on_message)

    async def on_ready(self):
        log.info(f'Logged in as {self.user} (ID: {self.user.id})')

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        message: discord.Message = reaction.message
        guild: discord.Guild = message.channel.guild
        channel: discord.TextChannel = message.channel
        user: discord.User = message.author
        users: discord.User = await reaction.users().flatten()

        log.info(f"In: server:`{guild}` id:{guild.id}  Channel: name:`{channel}` id:{channel.id}  Reaction `{reaction}` by `{[u.name for u in users]}` to Message author:`{user}` text:`{message.content}`")

        await stats.process_reaction(guild, channel, reaction)

    async def on_message(self, message: discord.Message):
        guild: discord.Guild = message.channel.guild
        channel: discord.TextChannel = message.channel
        user: discord.User = message.author

        # Ignore our own messages
        if user == self.user:
            return

        # Commands are invoked by: @duckbot ....
        if message.content.strip().startswith(self.user.mention):
            await cmd.process_message(guild, channel, user, message, bot=self)
            return

        log.info(f"In: server:`{guild}` id:{guild.id}  Channel: name:`{channel}` id:{channel.id}   Message author:`{user}` text:`{message.content}`")

        await stats.process_message(guild, channel, user, message)


def main():
    from .config import TOKEN

    logging.basicConfig(level=logging.INFO)

    bot = DuckBot()
    bot.run(TOKEN)


if __name__ == '__main__':
    main()
