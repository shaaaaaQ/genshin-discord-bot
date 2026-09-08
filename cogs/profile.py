import logging

import discord
import enka
from discord import app_commands
from discord.ext import commands

from services.profiles.embeds import create_character_embed, create_player_embed
from services.profiles.service import fetch_profile
from services.user_uids import get_user_uid, save_user_uid


logger = logging.getLogger(__name__)


class ProfileView(discord.ui.View):
    def __init__(self, data: enka.gi.ShowcaseResponse, author_id: int):
        super().__init__(timeout=180)
        self.data = data
        self.author_id = author_id
        self.message: discord.Message | None = None
        self.page.add_option(
            label=data.player.nickname or 'プロフィール',
            description='プレイヤー情報',
            value='profile',
        )
        for index, character in enumerate(data.characters):
            self.page.add_option(
                label=character.name,
                description=(
                    f'Lv.{character.level} / C{character.constellations_unlocked}'
                ),
                value=str(index),
            )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.author_id:
            return True
        await interaction.response.send_message(
            'このメニューはコマンドを実行した人だけ操作できます。', ephemeral=True
        )
        return False

    async def on_timeout(self):
        if self.message is not None:
            await self.message.edit(view=None)

    @discord.ui.select(placeholder='プロフィール / キャラクター')
    async def page(self, interaction: discord.Interaction, select: discord.ui.Select):
        value = select.values[0]
        embed = (
            create_player_embed(self.data)
            if value == 'profile'
            else create_character_embed(self.data, self.data.characters[int(value)])
        )
        await interaction.response.edit_message(embed=embed, view=self)


class Profile(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(description='原神の公開プロフィールを表示します')
    @app_commands.describe(uid='原神のUID（省略すると前回のUIDを使用）')
    async def profile(self, ctx: commands.Context, uid: str | None = None):
        if uid is None:
            uid = await get_user_uid(ctx.author.id)
        if uid is None:
            await ctx.reply(
                f'UIDを指定してください。例: `{ctx.prefix}profile 123456789`',
                mention_author=False,
            )
            return

        uid = uid.strip()
        if not uid.isascii() or not uid.isdecimal() or len(uid) not in (9, 10):
            await ctx.reply(
                'UIDは9～10桁の半角数字で入力してください。', mention_author=False
            )
            return

        await ctx.defer()
        try:
            data = await fetch_profile(uid)
        except enka.errors.PlayerDoesNotExistError:
            await ctx.reply('プレイヤーが見つかりませんでした。UIDを確認してください。')
            return
        except enka.errors.RateLimitedError:
            await ctx.reply('Enka.Networkが混み合っています。少し待ってからお試しください。')
            return
        except enka.errors.EnkaAPIError:
            logger.exception('Enka.NetworkからUID %sを取得できませんでした', uid)
            await ctx.reply('プロフィールを取得できませんでした。時間をおいて再度お試しください。')
            return
        except Exception:
            logger.exception('UID %sのプロフィール処理に失敗しました', uid)
            await ctx.reply('プロフィールの表示中にエラーが発生しました。')
            return

        await save_user_uid(ctx.author.id, uid)
        view = ProfileView(data, ctx.author.id) if data.characters else None
        message = await ctx.reply(
            embed=create_player_embed(data),
            view=view,
            mention_author=False,
            allowed_mentions=discord.AllowedMentions.none(),
        )
        if view is not None:
            view.message = message


async def setup(bot: commands.Bot):
    await bot.add_cog(Profile(bot))
