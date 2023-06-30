import logging

import discord
from discord.ext import commands
from enkanetwork import EnkaNetworkAPI
from enkanetwork.model.character import CharacterInfo

client = EnkaNetworkAPI(lang='jp')

logger = logging.getLogger(__name__)


def create_player_embed(data):
    player = data.player
    profile = data.profile

    # player.avatarの元素かなんかに合わせて色変えたい
    embed = discord.Embed(
        title=player.nickname,
        description=player.signature,
        url=profile.url
    )
    embed.set_thumbnail(url=player.avatar.icon.url)
    embed.add_field(
        name='冒険ランク',
        value=player.level
    )
    embed.add_field(
        name='世界ランク',
        value=player.world_level
    )
    embed.add_field(
        name='アチーブメント',
        value=player.achievement
    )
    embed.add_field(
        name='螺旋',
        value=f'{player.abyss_floor}-{player.abyss_room}'
    )
    return embed


def create_character_embed(data, character: CharacterInfo):
    # 元素かなんかに合わせて色変えたい
    embed = discord.Embed(
        title=data.player.nickname,
    )
    embed.set_thumbnail(url=character.image.icon.url)
    embed.add_field(
        name=character.name,
        value='hoge'
    )
    return embed


class View(discord.ui.View):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.page.add_option(
            label=data.player.nickname,
            description='Player',
            value=-1,
            default=True
        )
        for i, character in enumerate(data.characters):
            self.page.add_option(
                label=character.name,
                description=f'Lv.{character.level}',
                value=i
            )

    @discord.ui.select(
        cls=discord.ui.Select
    )
    async def page(self, interaction: discord.Interaction, select):
        await interaction.response.defer()
        index = int(select.values[0])
        if (index < 0):
            embed = create_player_embed(self.data)
        else:
            embed = create_character_embed(
                self.data, self.data.characters[index])

        await self.message.edit(embed=embed)


class Profile(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command()
    async def profile(self, ctx, uid: int):
        async with client:
            data = await client.fetch_user_by_uid(uid)

        view = View(data)
        view.message = await ctx.reply(
            embed=create_player_embed(data),
            view=view
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Profile(bot))
