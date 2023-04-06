from discord.ext import commands
import discord

import config


def get_prefixes(bot, message):
    prefixes = [
        f'<@{bot.user.id}>',
        config.prefix
    ]
    return prefixes


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix=get_prefixes,
            intents=intents
        )
        self.connections = {}

    async def setup_hook(self):
        await self.load_extension('commands')

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
