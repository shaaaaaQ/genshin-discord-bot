from io import BytesIO
from discord.ext import commands
from PIL import Image
import math
import requests
import pyocr

engine = pyocr.get_available_tools()[0]


def get_stats(url):
    img = Image.open(BytesIO(requests.get(url).content))
    text = engine.image_to_string(img, lang='jpn')
    print(text)
    return filter(lambda s: s.startswith('・'), text.splitlines())


class Artifact(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def crit(self, ctx):
        if not ctx.message.attachments:
            print('nai')
            return

        url = ctx.message.attachments[0].url
        stats = get_stats(url)
        score = 0
        for stat in stats:
            print(stat)
            value = float(stat.split('+')[1].replace('%', ''))
            print(value)
            if stat.startswith('・会心率'):
                score += value*2
            if stat.startswith('・会心ダメージ'):
                score += value
        await ctx.send(math.floor(score*10)/10)

    @commands.command()
    async def atk(self, ctx):
        if not ctx.message.attachments:
            print('nai')
            return

        url = ctx.message.attachments[0].url
        stats = get_stats(url)
        score = 0
        for stat in stats:
            print(stat)
            value = float(stat.split('+')[1].replace('%', ''))
            print(value)
            if stat.startswith('・会心率'):
                score += value*2
            if stat.startswith('・会心ダメージ'):
                score += value
            if stat.startswith('・攻撃力') and stat.endswith('%'):
                score += value
        await ctx.send(math.floor(score*10)/10)

    @commands.command()
    async def hp(self, ctx):
        if not ctx.message.attachments:
            print('nai')
            return

        url = ctx.message.attachments[0].url
        stats = get_stats(url)
        score = 0
        for stat in stats:
            print(stat)
            value = float(stat.split('+')[1].replace('%', ''))
            print(value)
            if stat.startswith('・会心率'):
                score += value*2
            if stat.startswith('・会心ダメージ'):
                score += value
            if stat.startswith('・HP') and stat.endswith('%'):
                score += value
        await ctx.send(math.floor(score*10)/10)


async def setup(bot):
    await bot.add_cog(Artifact(bot))
