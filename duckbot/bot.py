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
        intents.message_content = True

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

    async def on_direct_message(self, message: discord.Message):
        user = message.author
        if user == self.user:
            return

        log.info(f"DM: Message author:`{user}` text:`{message.content}`")
        await cmd.process_message(None, message.channel, user, message, bot=self)

    def get_channel(self, channel_or_thread) -> discord.TextChannel:
        if hasattr(channel_or_thread, 'parent'):
            channel: discord.TextChannel = channel_or_thread.parent
        else:
            channel: discord.TextChannel = channel_or_thread
        return channel

    async def on_message(self, message: discord.Message):
        if not hasattr(message.channel, 'guild'):
            await self.on_direct_message(message)
            return

        guild: discord.Guild = message.channel.guild
        channel: discord.TextChannel = self.get_channel(message.channel)
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
