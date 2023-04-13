from discord.ext import commands
import discord

import config

cogs = [
    'cogs.artifact',
    'cogs.build_card'
]


def get_prefix(bot, message):
    return commands.when_mentioned_or(config.prefix)(bot, message)


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix=get_prefix,
            intents=intents
        )

    async def setup_hook(self):
        for cog in cogs:
            await self.load_extension(cog)
        await self.tree.sync()

    def run(self):
        super().run(config.token)

    async def on_ready(self):
        print('ready')

    async def on_message(self, message):
        if message.author.bot:
            return

        await self.process_commands(message)


if __name__ == '__main__':
    Bot().run()
