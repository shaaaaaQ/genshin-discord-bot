import logging
from typing import Any

import discord
from discord import Message
from discord.ext import commands

import config

logger = logging.getLogger(__name__)
discord.utils.setup_logging(level=logging.INFO)

cogs = [
    'cogs.artifact',
    'cogs.build_card',
    'cogs.profile'
]


def get_prefix(bot: commands.Bot, message: Message):
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

    def run(
        self,
        token: str = config.token,
        **kwargs: Any,
    ):
        super().run(token, **kwargs)

    async def on_ready(self):
        logger.info('ready')

    async def on_message(self, message: Message):
        if message.author.bot:
            return

        await self.process_commands(message)


if __name__ == '__main__':
    Bot().run(log_handler=None)
