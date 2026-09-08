from io import BytesIO
import asyncio
import logging

import discord
import enka
from discord import app_commands
from discord.ext import commands

from services.build_cards.constants import calc_types, prop_id_ja
from services.build_cards.service import fetch_characters, generate_card
from services.user_uids import get_user_uid, save_user_uid


logger = logging.getLogger(__name__)


class View(discord.ui.View):
    def __init__(self, characters: list[enka.gi.Character]):
        super().__init__()
        self.characters = characters
        for i, character in enumerate(characters):
            self.character.add_option(
                label=character.name,
                description=f'Lv.{character.level}',
                value=str(i)
            )
        for i, calc_type in enumerate(calc_types):
            tmp = []
            for prop_id, rate in calc_type['rates'].items():
                if rate == 1:
                    tmp.append(prop_id_ja[prop_id])
                else:
                    tmp.append(f'{prop_id_ja[prop_id]} * {rate}')
            desc = ' + '.join(tmp)
            self.calc_type.add_option(
                label=calc_type['label'],
                description=desc,
                value=str(i)
            )

    async def on_timeout(self):
        if not self.message.attachments:
            await self.message.edit(view=None, content='Timeout')

    @discord.ui.select(
        cls=discord.ui.Select,
        placeholder='キャラクター'
    )
    async def character(self, interaction: discord.Interaction, select):
        await interaction.response.defer()

    @discord.ui.select(
        cls=discord.ui.Select,
        placeholder='計算タイプ'
    )
    async def calc_type(self, interaction: discord.Interaction, select):
        await interaction.response.defer()

    @discord.ui.button(
        label='生成',
        style=discord.ButtonStyle.success
    )
    async def generate(self, interaction: discord.Interaction, button):
        if not self.character.values:
            await interaction.response.send_message(
                content='キャラクター選択してない',
                delete_after=5
            )
            return
        if not self.calc_type.values:
            await interaction.response.send_message(
                content='計算タイプ選択してない',
                delete_after=5
            )
            return

        await interaction.response.defer()
        character = self.characters[int(self.character.values[0])]
        calc_type = calc_types[int(self.calc_type.values[0])]

        task = asyncio.create_task(generate_card(character, calc_type))
        dot = 1
        while not task.done():
            await self.message.edit(view=None, content=f'生成中{"."*dot}')
            dot = dot % 3 + 1
            await asyncio.sleep(1)
        image = await task

        f = BytesIO()
        image.save(f, format='png')
        f.seek(0)
        self.message = await self.message.edit(
            content=None,
            attachments=[discord.File(f, 'card.png')]
        )


class UIDModal(discord.ui.Modal, title='UID入力'):
    uid = discord.ui.TextInput(
        label='原神UID',
        placeholder='UIDを入力してください',
        min_length=9,
        max_length=10
    )

    def __init__(self, cog: 'BuildCard'):
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        uid = self.uid.value.strip()
        if not uid.isascii() or not uid.isdecimal():
            await interaction.response.send_message(
                'UIDは半角数字で入力してください。',
                ephemeral=True
            )
            return

        await interaction.response.defer()
        try:
            view, error = await self.cog.create_view(uid)
        except Exception:
            logger.exception('UID %s のデータ取得に失敗しました', uid)
            await interaction.followup.send(
                'データの取得に失敗しました。UIDを確認して、もう一度お試しください。',
                ephemeral=True
            )
            return

        await save_user_uid(interaction.user.id, uid)
        if view is None:
            await interaction.followup.send(error or 'error', ephemeral=True)
            return

        view.message = await interaction.followup.send(view=view, wait=True)


class BuildCard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_view(self, uid: str) -> tuple[View | None, str | None]:
        characters, error = await fetch_characters(uid)
        return (View(characters), None) if characters else (None, error)

    @commands.hybrid_command()
    @app_commands.describe(uid='原神のUID（省略すると前回のUIDを使用）')
    async def build(self, ctx, uid: str | None = None):
        """公開キャラクターからビルドカードを作成します。

        UIDを省略すると、前回使用したUIDを利用します。
        """
        if uid is None:
            uid = await get_user_uid(ctx.author.id)

        if uid is None:
            if ctx.interaction:
                await ctx.interaction.response.send_modal(UIDModal(self))
            else:
                await ctx.reply(f'UIDを指定してください。例: `{ctx.prefix}build 123456789`')
            return

        uid = uid.strip()
        if not uid.isascii() or not uid.isdecimal() or len(uid) not in (9, 10):
            await ctx.reply('UIDは9～10桁の半角数字で入力してください。')
            return

        view, error = await self.create_view(uid)
        await save_user_uid(ctx.author.id, uid)
        if view is None:
            await ctx.reply(error or 'error')
            return

        view.message = await ctx.reply(view=view)


async def setup(bot):
    await bot.add_cog(BuildCard(bot))
