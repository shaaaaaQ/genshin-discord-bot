import asyncio
import logging
from decimal import Decimal
from io import BytesIO
from typing import Any, Literal

import discord
import requests
from discord.ext import commands
from PIL import Image

from .artifact_locales import locales
from .artifact_constants import AttrKeys
from .artifact_score import ArtifactScore, G_CalcType
from .paddle_ocr import PaddleOCRReader

Ctx = commands.Context[Any]
CalcType = Literal['hp', 'atk', 'def', 'crit', 'em', 'er']

PADDLE_LANGS = {
    'en': 'en',
    'ru': 'ru',
    'vi': 'vi',
    'th': 'th',
    'pt': 'pt',
    'ko': 'korean',
    'ja': 'japan',
    'id': 'id',
    'fr': 'fr',
    'es': 'es',
    'de': 'de',
    'zh-TW': 'chinese_cht',
    'zh-CN': 'ch',
    'it': 'it',
    'tr': 'tr',
}

logger = logging.getLogger(__name__)


class LangConv(commands.Converter[str]):
    async def convert(self, ctx: Ctx, argument: str) -> str:
        if argument not in locales:
            await ctx.reply('その言語対応してない')
            argument = 'ja'
        return argument


class Artifact(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ocr_readers: dict[str, PaddleOCRReader] = {}

        # calc_score メソッドで使用
        self.command_calc_map: dict[CalcType, tuple[G_CalcType, list[AttrKeys]]]= {
            # 算出ロジックタイプ: (一般スコアロジック名, 論理値比算出対象属性一覧)
            'crit': ('crit_only', ['crit_dmg', 'crit_rate']),
            'atk': ('rated_atk', ['crit_dmg', 'crit_rate', 'rated_atk']),
            'hp': ('rated_hp', ['crit_dmg', 'crit_rate', 'rated_hp']),
            'def': ('rated_def', ['crit_dmg', 'crit_rate', 'rated_def']),
            'em': ('em', ['crit_dmg', 'crit_rate', 'elemental_mastery']),
            'er': ('er', ['crit_dmg', 'crit_rate', 'charge_rate']),
        }

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

    @commands.hybrid_command(name='def')
    async def _def(self, ctx: Ctx, attachment: discord.Attachment,
                   lang: LangConv = 'ja'):  # type: ignore
        """
        画像からスコア計算(防御力%)
        会心率 * 2 + 会心ダメージ + 防御力%
        """
        await self.proc(ctx, lang, attachment, 'def')  # type: ignore

    @commands.hybrid_command()
    async def em(self, ctx: Ctx, attachment: discord.Attachment,
                 lang: LangConv = 'ja'):  # type: ignore
        """
        画像からスコア計算(会心+元素熟知)
        会心率 * 2 + 会心ダメージ + 元素熟知 * 0.25
        """
        await self.proc(ctx, lang, attachment, 'em')  # type: ignore

    @commands.hybrid_command()
    async def er(self, ctx: Ctx, attachment: discord.Attachment,
                 lang: LangConv = 'ja'):  # type: ignore
        """
        画像からスコア計算(元素チャージ効率)
        会心率 * 2 + 会心ダメージ + 元素チャージ効率
        """
        await self.proc(ctx, lang, attachment, 'er')  # type: ignore

    async def proc(self, ctx: Ctx, lang: str, attachment: discord.Attachment, calc_type: CalcType):
        t = locales[lang]
        url = attachment.url
        reader = self.ocr_readers.setdefault(
            lang,
            PaddleOCRReader(PADDLE_LANGS[lang]),
        )
        stats = await asyncio.to_thread(self.get_stats, t, url, reader)
        score, rate = self.calc_score(stats, calc_type)
        embed = self.create_embed(t, stats, score, rate)
        await ctx.reply(embed=embed)

    def get_stats(
        self,
        t: dict[str, str],
        url: str,
        reader: PaddleOCRReader,
    ) -> dict[str, Any]:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        with Image.open(BytesIO(response.content)) as img:
            ocr_lines = reader.read_lines(img)
        logger.debug('PaddleOCR result: %s', ocr_lines)
        return self.parse_stats(t, ocr_lines)

    def parse_stats(self, t: dict[str, str], ocr_lines: list[str]) -> dict[str, Any]:
        stats: dict[str, Any] = {}
        for text in ocr_lines:
            text = text.strip().lstrip('・·• ')
            # 日本語モデルが繁体字を返す場合がある。
            text = text.replace('攻擊力', '攻撃力')
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
        return float(stat.split('+')[1].replace('%', '').replace(',', ''))

    def calc_score(self, stats: dict[str, Any], calc_type: CalcType) -> tuple[Decimal, Decimal]:
        score = ArtifactScore(**stats)
                
        logic_name, target_attrs = self.command_calc_map[calc_type]

        return (
            score.calc_general_rate(logic_name),
            score.calc_theoretical_rate(target_attrs),
        )

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
