import logging
from decimal import Decimal
from io import BytesIO
from typing import Any, Literal

import discord
import pyocr
import requests
from discord.ext import commands
from PIL import Image

from .artifact_locales import locales
from .artifact_score import ArtifactScore

tools: list[Any] = pyocr.get_available_tools()

Ctx = commands.Context[Any]

logger = logging.getLogger(__name__)


class LangConv(commands.Converter[str]):
    async def convert(self, ctx: Ctx, argument: str) -> str:
        if argument not in locales.keys():
            await ctx.reply('その言語対応してない')
            argument = 'ja'
        return argument


class Artifact(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Ctx, error: Exception):
        if isinstance(error, commands.MissingRequiredAttachment):
            await ctx.reply('添付ファイルがない')
        elif isinstance(error, commands.CommandNotFound):
            pass
        else:
            await ctx.reply('error')
            logger.error(error)

    @commands.hybrid_command()
    async def crit(self, ctx: Ctx, attachment: discord.Attachment,
                   lang: LangConv = 'ja'):  # type: ignore
        """
        画像からスコア計算(会心のみ)
        会心率 * 2 + 会心ダメージ
        """
        await self.proc(ctx, lang, attachment, 'crit')  # type: ignore

    @commands.hybrid_command()
    async def atk(self, ctx: Ctx, attachment: discord.Attachment,
                  lang: LangConv = 'ja'):  # type: ignore
        """
        画像からスコア計算(攻撃力%)
        会心率 * 2 + 会心ダメージ + 攻撃力%
        """
        await self.proc(ctx, lang, attachment, 'atk')  # type: ignore

    @commands.hybrid_command()
    async def hp(self, ctx: Ctx, attachment: discord.Attachment,
                 lang: LangConv = 'ja'):  # type: ignore
        """
        画像からスコア計算(HP%)
        会心率 * 2 + 会心ダメージ + HP%
        """
        await self.proc(ctx, lang, attachment, 'hp')  # type: ignore

    async def proc(self, ctx: Ctx, lang: str, attachment: discord.Attachment, calc_type: Literal['hp', 'atk', 'crit']):
        t = locales[lang]
        url = attachment.url
        stats = self.get_stats(t, url)
        score, rate = self.calc_score(stats)[calc_type]
        embed = self.create_embed(t, stats, score, rate)
        await ctx.reply(embed=embed)

    def get_stats(self, t: dict[str, str], url: str) -> list[str]:
        img = Image.open(BytesIO(requests.get(url).content))  # type: ignore
        ocr_text: str = tools[0].image_to_string(img, t['code'])
        logger.debug(ocr_text)
        stats: dict[str, Any] = {}
        for text in ocr_text.splitlines():
            if text.startswith(('+ ', '* ', '; ', '・ ')):
                text = text[2:]
            if text.endswith('%6'):
                text = text[:-1]
            if text.startswith('・'):
                text = text[1:]
            for attr, attr_name in t.items():
                if text.startswith(f'{attr_name}+'):
                    if attr.startswith('fixed') and text.endswith('%'):
                        continue
                    elif attr.startswith('rated') and not text.endswith('%'):
                        continue
                    elif attr.startswith(('fixed', 'elemental_mastery')):
                        stats[attr] = int(self.get_value(text))
                    else:
                        stats[attr] = self.get_value(text)
        logger.debug(stats)
        return stats

    def get_value(self, stat: str):
        return float(stat.split('+')[1].replace('%', ''))

    def calc_score(self, stats: dict[str, Any]):
        score = ArtifactScore(**stats)
        return {
            'crit': (
                score.calc_general_rate('crit_only'),
                score.calc_theoretical_rate(['crit_dmg', 'crit_rate']),
            ),
            'atk': (
                score.calc_general_rate('rated_atk'),
                score.calc_theoretical_rate(
                    ['crit_dmg', 'crit_rate', 'rated_atk']),
            ),
            'hp': (
                score.calc_general_rate('rated_hp'),
                score.calc_theoretical_rate(
                    ['crit_dmg', 'crit_rate', 'rated_hp']),
            ),
        }

    def create_embed(self, t: dict[str, str], stats: dict[str, float], score: Decimal, rate: Decimal):
        embed = discord.Embed()
        stats_str: list[str] = []
        for attr, value in stats.items():
            if attr.startswith(('fixed', 'elemental_mastery')):
                stats_str.append(f'{t[attr]}+{value}')
            else:
                stats_str.append(f'{t[attr]}+{value}%')

        embed.add_field(name='サブステータス',
                        value='\n'.join(stats_str), inline=False)
        embed.add_field(name='スコア', value=score, inline=False)
        embed.add_field(name='理論値比', value=f'{rate}%', inline=False)
        return embed


async def setup(bot: commands.Bot):
    await bot.add_cog(Artifact(bot))
