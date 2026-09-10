import logging

import discord
from discord.ext import commands

from services.gacha import GachaClient, GachaError, create_gacha_embeds


logger = logging.getLogger(__name__)


class Gacha(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = GachaClient()

    async def cog_load(self) -> None:
        await self.client.start()

    async def cog_unload(self) -> None:
        await self.client.close()

    @commands.hybrid_command(description='現在の原神のガチャ情報を表示します')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def gacha(self, ctx: commands.Context) -> None:
        """現在の原神のガチャ情報を表示します。"""
        await ctx.defer()
        try:
            banners = await self.client.fetch()
            embeds = create_gacha_embeds(banners)
        except GachaError as error:
            await ctx.reply(str(error), mention_author=False)
            return
        except (KeyError, TypeError, ValueError, AttributeError):
            logger.exception('Invalid hoyoverse-api gacha response')
            await ctx.reply(
                'ガチャ情報の形式を読み取れませんでした。', mention_author=False
            )
            return

        await ctx.reply(
            embed=embeds[0],
            mention_author=False,
            allowed_mentions=discord.AllowedMentions.none(),
        )
        for embed in embeds[1:]:
            await ctx.send(
                embed=embed,
                allowed_mentions=discord.AllowedMentions.none(),
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Gacha(bot))
