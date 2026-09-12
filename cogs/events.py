import logging

import discord
from discord.ext import commands

from services.events import EventsClient, EventsError, create_events_embed


logger = logging.getLogger(__name__)


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = EventsClient()

    async def cog_load(self) -> None:
        await self.client.start()

    async def cog_unload(self) -> None:
        await self.client.close()

    @commands.hybrid_command(description='現在の原神のゲーム内イベントを表示します')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def events(self, ctx: commands.Context) -> None:
        """現在の原神のゲーム内イベントを表示します。"""
        await ctx.defer()
        try:
            events = await self.client.fetch()
            embed = create_events_embed(events)
        except EventsError as error:
            await ctx.reply(str(error), mention_author=False)
            return
        except (KeyError, TypeError, ValueError, AttributeError):
            logger.exception('Invalid hoyoverse-api event response')
            await ctx.reply(
                'イベント情報の形式を読み取れませんでした。', mention_author=False
            )
            return

        await ctx.reply(
            embed=embed,
            mention_author=False,
            allowed_mentions=discord.AllowedMentions.none(),
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Events(bot))
