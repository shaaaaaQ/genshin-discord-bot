import logging
import os

import discord
from discord import Message
from discord.ext import commands
from dotenv import load_dotenv

from services.application_emojis import sync_application_emojis

logger = logging.getLogger(__name__)
discord.utils.setup_logging(level=logging.INFO)

cogs = [
    'cogs.errors',
    'cogs.artifact',
    'cogs.build_card',
    'cogs.codes',
    'cogs.events',
    'cogs.gacha',
    'cogs.stage',
    'cogs.profile',
]


def get_prefix(bot: commands.Bot, message: Message):
    return commands.when_mentioned_or(os.getenv('COMMAND_PREFIX', '-'))(bot, message)


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix=get_prefix,
            intents=intents
        )

    async def setup_hook(self):
        await sync_application_emojis(self)
        for cog in cogs:
            await self.load_extension(cog)
        await self.tree.sync()

    async def on_ready(self):
        logger.info('ready')

    async def on_message(self, message: Message):
        if message.author.bot:
            return

        await self.process_commands(message)


if __name__ == '__main__':
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise SystemExit('DISCORD_TOKEN を環境変数または .env に設定してください。')
    Bot().run(token, log_handler=None)
