import logging

import discord
from discord.ext import commands

from services.codes import CodesClient, CodesError, create_codes_embeds


logger = logging.getLogger(__name__)


class Codes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = CodesClient()

    async def cog_load(self) -> None:
        await self.client.start()

    async def cog_unload(self) -> None:
        await self.client.close()

    @commands.hybrid_command(description='現在利用できる原神の交換コードを表示します')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def codes(self, ctx: commands.Context) -> None:
        await ctx.defer()
        try:
            codes = await self.client.fetch()
            embeds = create_codes_embeds(codes)
        except CodesError as error:
            await ctx.reply(str(error), mention_author=False)
            return
        except (KeyError, TypeError, ValueError, AttributeError):
            logger.exception('Invalid hoyoverse-api response')
            await ctx.reply(
                '交換コードの形式を読み取れませんでした。', mention_author=False
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
    await bot.add_cog(Codes(bot))
