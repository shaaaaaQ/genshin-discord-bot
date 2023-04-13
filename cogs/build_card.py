from discord.ext import commands
from artifacter_image_gen import Generator
from enkanetwork import EnkaNetworkAPI
import discord

client = EnkaNetworkAPI(lang='jp')


class BuildCard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def build(self, ctx, uid: int):
        async with client:
            data = await client.fetch_user(uid)
            img = Generator(data.characters[0]).generate('RATED_ATK')
            await ctx.reply('o')


async def setup(bot):
    await bot.add_cog(BuildCard(bot))
