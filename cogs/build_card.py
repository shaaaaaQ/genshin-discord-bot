from io import BytesIO
from concurrent.futures import ProcessPoolExecutor
import asyncio
from discord.ext import commands
from artifacter_image_gen import Generator
from enkanetwork import EnkaNetworkAPI
import discord
from .build_card_constants import calc_types, prop_id_ja

client = EnkaNetworkAPI(lang='jp')


class View(discord.ui.View):
    def __init__(self, characters):
        super().__init__(timeout=8)
        self.characters = characters
        for i, character in enumerate(characters):
            self.character.add_option(
                label=character.name,
                description=f'Lv.{character.level}',
                value=i
            )
        for i, calc_type in enumerate(calc_types):
            tmp = []
            for r in calc_type['rates']:
                type_ = r['type']
                rate = r['rate']
                if rate == 1:
                    tmp.append(prop_id_ja[type_])
                else:
                    tmp.append(f'{prop_id_ja[type_]} * {rate}')
            desc = ' + '.join(tmp)
            self.calc_type.add_option(
                label=calc_type['label'],
                description=desc,
                value=i
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

        character = self.characters[int(self.character.values[0])]
        calc_type = calc_types[int(self.calc_type.values[0])]

        with ProcessPoolExecutor() as executor:
            future = executor.submit(
                Generator(character).generate, **calc_type)
            dot = 1
            while not future.done():
                await self.message.edit(view=None, content=f'生成中{"."*dot}')
                dot += 1
                if dot > 3:
                    dot = 1
                await asyncio.sleep(1)
            image = future.result()
        f = BytesIO()
        image.save(f, format='png')
        f.seek(0)
        self.message = await self.message.edit(
            content=None,
            attachments=[discord.File(f, 'card.png')]
        )


class BuildCard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def build(self, ctx, uid: int):
        async with client:
            data = await client.fetch_user(uid)

        player = data.player
        characters = data.characters

        if not characters:
            if not player.nickname:
                await ctx.reply('error')
            else:
                await ctx.reply(f'キャラクターが公開されてない\n(プレイヤー名: {player.nickname})')
            return
        view = View(characters)
        view.message = await ctx.reply(view=view)


async def setup(bot):
    await bot.add_cog(BuildCard(bot))
