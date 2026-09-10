import logging

import discord
from discord import app_commands
from discord.ext import commands

from services.stages import (
    REGIONS,
    Region,
    StageClient,
    StageError,
    create_stage_embed,
)

logger = logging.getLogger(__name__)


class Stage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = StageClient()

    async def cog_load(self):
        await self.client.start()

    async def cog_unload(self):
        await self.client.close()

    @commands.hybrid_command(description="幻境のGUIDからステージ情報を表示します")
    @app_commands.describe(
        guid="幻境のGUID（半角数字）",
        region="サーバー（省略するとGUIDから自動判定）",
    )
    @app_commands.rename(region="server")
    @app_commands.choices(
        region=[
            app_commands.Choice(name=name, value=code) for code, name in REGIONS.items()
        ]
    )
    async def stage(
        self,
        ctx: commands.Context,
        guid: str,
        region: Region | None = None,
    ):
        """幻境のGUIDからステージ情報を表示します。"""
        guid = guid.strip()
        if (
            not guid.isascii()
            or not guid.isdecimal()
            or len(guid) > 20
            or int(guid) == 0
        ):
            await ctx.reply(
                "GUIDは20桁以内の正の半角数字で入力してください。",
                mention_author=False,
            )
            return
        await ctx.defer()
        try:
            data = await self.client.fetch(str(int(guid)), region)
            embed = create_stage_embed(data)
        except StageError as error:
            await ctx.reply(str(error), mention_author=False)
            return
        except (KeyError, TypeError, ValueError, AttributeError):
            logger.exception("Invalid Octavia response for GUID %s", guid)
            await ctx.reply(
                "ステージ情報の形式を読み取れませんでした。", mention_author=False
            )
            return
        await ctx.reply(
            embed=embed,
            mention_author=False,
            allowed_mentions=discord.AllowedMentions.none(),
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Stage(bot))
