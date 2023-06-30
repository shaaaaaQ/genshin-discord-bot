import logging

import discord
from discord.ext import commands
from enkanetwork import EnkaNetworkAPI

client = EnkaNetworkAPI(lang='jp')

logger = logging.getLogger(__name__)


class Profile(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command()
    async def profile(self, ctx, uid: int):
        async with client:
            data = await client.fetch_user_by_uid(uid)

        player = data.player
        profile = data.profile

        # player.avatarの元素かなんかに合わせて色変えたい
        embed = discord.Embed(
            title=player.nickname,
            description=player.signature,
            url=profile.url
        )
        embed.set_thumbnail(url=player.avatar.icon.url)
        embed.add_field(
            name='冒険ランク',
            value=player.level
        )
        embed.add_field(
            name='世界ランク',
            value=player.world_level
        )
        embed.add_field(
            name='アチーブメント',
            value=player.achievement
        )
        embed.add_field(
            name='螺旋',
            value=f'{player.abyss_floor}-{player.abyss_room}'
        )

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Profile(bot))
