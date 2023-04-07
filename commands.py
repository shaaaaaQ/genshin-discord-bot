from io import BytesIO
from discord.ext import commands
from PIL import Image
from decimal import Decimal
import discord
import requests
import pyocr

tools = pyocr.get_available_tools()


def has_attachment():
    def predicate(ctx):
        return ctx.message.attachments
    return commands.check(predicate)


class Artifact(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply('添付ファイルがない')
        else:
            await ctx.reply('error')

    @commands.command()
    @has_attachment()
    async def crit(self, ctx):
        """
        画像からスコア計算(会心のみ)
        会心率 * 2 + 会心ダメージ
        """
        url = ctx.message.attachments[0].url
        stats = self.get_stats(url)
        score = 0
        for stat in stats:
            value = self.get_value(stat)
            if stat.startswith('・会心率'):
                score += value*2
            if stat.startswith('・会心ダメージ'):
                score += value
        embed = self.create_embed(stats, score)
        await ctx.reply(embed=embed)

    @commands.command()
    @has_attachment()
    async def atk(self, ctx):
        """
        画像からスコア計算(攻撃力%)
        会心率 * 2 + 会心ダメージ + 攻撃力%
        """
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
        embed = self.create_embed(stats, score)
        await ctx.reply(embed=embed)

    @commands.command()
    @has_attachment()
    async def hp(self, ctx):
        """
        画像からスコア計算(HP%)
        会心率 * 2 + 会心ダメージ + HP%
        """
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
        embed = self.create_embed(stats, score)
        await ctx.reply(embed=embed)

    def get_stats(self, url):
        img = Image.open(BytesIO(requests.get(url).content))
        text = tools[0].image_to_string(img, lang='jpn')
        print(text)
        return list(filter(lambda s: s.startswith('・'), text.splitlines()))

    def get_value(self, stat):
        return Decimal(stat.split('+')[1].replace('%', ''))

    def create_embed(self, stats, score):
        embed = discord.Embed()
        embed.add_field(name='サブステータス', value='\n'.join(stats), inline=False)
        embed.add_field(name='スコア', value=score, inline=False)
        return embed


async def setup(bot):
    await bot.add_cog(Artifact(bot))
