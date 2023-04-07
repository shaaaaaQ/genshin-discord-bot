from io import BytesIO
from discord.ext import commands
from PIL import Image
from decimal import Decimal
import requests
import pyocr

engine = pyocr.get_available_tools()[0]


def has_attachment():
    def predicate(ctx):
        return ctx.message.attachments
    return commands.check(predicate)


class Artifact(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @has_attachment()
    async def crit(self, ctx):
        url = ctx.message.attachments[0].url
        stats = self.get_stats(url)
        score = 0
        for stat in stats:
            value = self.get_value(stat)
            if stat.startswith('・会心率'):
                score += value*2
            if stat.startswith('・会心ダメージ'):
                score += value
        await ctx.send(score)

    @commands.command()
    @has_attachment()
    async def atk(self, ctx):
        url = ctx.message.attachments[0].url
        stats = self.get_stats(url)
        score = 0
        for stat in stats:
            value = self.get_value(stat)
            if stat.startswith('・会心率'):
                score += value*2
            if stat.startswith('・会心ダメージ'):
                score += value
            if stat.startswith('・攻撃力') and stat.endswith('%'):
                score += value
        await ctx.send(score)

    @commands.command()
    @has_attachment()
    async def hp(self, ctx):
        url = ctx.message.attachments[0].url
        stats = self.get_stats(url)
        score = 0
        for stat in stats:
            value = self.get_value(stat)
            if stat.startswith('・会心率'):
                score += value*2
            if stat.startswith('・会心ダメージ'):
                score += value
            if stat.startswith('・HP') and stat.endswith('%'):
                score += value
        await ctx.send(score)

    def get_stats(self, url):
        img = Image.open(BytesIO(requests.get(url).content))
        text = engine.image_to_string(img, lang='jpn')
        print(text)
        return filter(lambda s: s.startswith('・'), text.splitlines())

    def get_value(self, stat):
        return Decimal(stat.split('+')[1].replace('%', ''))


async def setup(bot):
    await bot.add_cog(Artifact(bot))
