from typing import Any

import discord
from discord.ext import commands

from services.artifacts.embeds import create_artifact_embed
from services.artifacts.locales import locales
from services.artifacts.processor import ArtifactProcessor, CalcType


Ctx = commands.Context[Any]


class LangConv(commands.Converter[str]):
    async def convert(self, ctx: Ctx, argument: str) -> str:
        if argument not in locales:
            await ctx.reply('その言語対応してない')
            argument = 'ja'
        return argument


class Artifact(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.processor = ArtifactProcessor()

    @commands.hybrid_command()
    async def crit(
        self, ctx: Ctx, attachment: discord.Attachment, lang: LangConv = 'ja'
    ):
        """画像からスコア計算: 会心率 * 2 + 会心ダメージ"""
        await self._process(ctx, lang, attachment, 'crit')  # type: ignore

    @commands.hybrid_command()
    async def atk(
        self, ctx: Ctx, attachment: discord.Attachment, lang: LangConv = 'ja'
    ):
        """画像からスコア計算: 会心率 * 2 + 会心ダメージ + 攻撃力%"""
        await self._process(ctx, lang, attachment, 'atk')  # type: ignore

    @commands.hybrid_command()
    async def hp(
        self, ctx: Ctx, attachment: discord.Attachment, lang: LangConv = 'ja'
    ):
        """画像からスコア計算: 会心率 * 2 + 会心ダメージ + HP%"""
        await self._process(ctx, lang, attachment, 'hp')  # type: ignore

    @commands.hybrid_command(name='def')
    async def _def(
        self, ctx: Ctx, attachment: discord.Attachment, lang: LangConv = 'ja'
    ):
        """画像からスコア計算: 会心率 * 2 + 会心ダメージ + 防御力%"""
        await self._process(ctx, lang, attachment, 'def')  # type: ignore

    @commands.hybrid_command()
    async def em(
        self, ctx: Ctx, attachment: discord.Attachment, lang: LangConv = 'ja'
    ):
        """画像からスコア計算: 会心率 * 2 + 会心ダメージ + 元素熟知 * 0.25"""
        await self._process(ctx, lang, attachment, 'em')  # type: ignore

    @commands.hybrid_command()
    async def er(
        self, ctx: Ctx, attachment: discord.Attachment, lang: LangConv = 'ja'
    ):
        """画像からスコア計算: 会心率 * 2 + 会心ダメージ + 元素チャージ効率"""
        await self._process(ctx, lang, attachment, 'er')  # type: ignore

    async def _process(
        self,
        ctx: Ctx,
        lang: str,
        attachment: discord.Attachment,
        calc_type: CalcType,
    ) -> None:
        await ctx.defer()
        translations, stats, score, rate = await self.processor.analyze(
            lang, attachment.url, calc_type
        )
        await ctx.reply(embed=create_artifact_embed(translations, stats, score, rate))


async def setup(bot: commands.Bot):
    await bot.add_cog(Artifact(bot))
