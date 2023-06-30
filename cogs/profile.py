import logging

import discord
from discord.ext import commands
from enkanetwork import EnkaNetworkAPI
from enkanetwork.model.character import CharacterInfo

client = EnkaNetworkAPI(lang='jp')

logger = logging.getLogger(__name__)

element_ja = {
    'Anemo': '風',
    'Cryo': '氷',
    'Dendro': '草',
    'Electro': '雷',
    'Geo': '岩',
    'Hydro': '水',
    'Pyro': '炎'
}


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
    stats = character.stats
    bonuses = {
        '与える治癒効果': stats.FIGHT_PROP_HEAL_ADD.to_percentage(),
        '物理ダメージ': stats.FIGHT_PROP_PHYSICAL_ADD_HURT.to_percentage(),
        '炎元素ダメージ': stats.FIGHT_PROP_FIRE_ADD_HURT.to_percentage(),
        '雷元素ダメージ': stats.FIGHT_PROP_ELEC_ADD_HURT.to_percentage(),
        '水元素ダメージ': stats.FIGHT_PROP_WATER_ADD_HURT.to_percentage(),
        '風元素ダメージ': stats.FIGHT_PROP_WIND_ADD_HURT.to_percentage(),
        '氷元素ダメージ': stats.FIGHT_PROP_ICE_ADD_HURT.to_percentage(),
        '岩元素ダメージ': stats.FIGHT_PROP_ROCK_ADD_HURT.to_percentage(),
        '草元素ダメージ': stats.FIGHT_PROP_GRASS_ADD_HURT.to_percentage()
    }
    bonus = max(bonuses, key=bonuses.get)
    if bonuses[bonus] == 0:
        bonus = f'{element_ja[character.element]}元素ダメージ'

    # 元素かなんかに合わせて色変えたい
    embed = discord.Embed(
        title=data.player.nickname,
        url=data.profile.url
    )
    embed.set_thumbnail(url=character.image.icon.url)
    embed.add_field(
        name=character.name,
        value=f'''
            Level: `{character.level}`
            好感度: `{character.friendship_level}`

            HP: `{stats.FIGHT_PROP_MAX_HP.to_rounded()}`
            攻撃力: `{stats.FIGHT_PROP_CUR_ATTACK.to_rounded()}`
            防御力: `{stats.FIGHT_PROP_CUR_DEFENSE.to_rounded()}`
            元素熟知: `{stats.FIGHT_PROP_ELEMENT_MASTERY.to_rounded()}`
            会心率: `{stats.FIGHT_PROP_CRITICAL.to_percentage()}%`
            会心ダメージ: `{stats.FIGHT_PROP_CRITICAL_HURT.to_percentage()}%`
            元素チャージ効率: `{stats.FIGHT_PROP_CHARGE_EFFICIENCY.to_percentage()}%`
            {bonus}: `{bonuses[bonus]}%`
        '''
    )
    return embed


class View(discord.ui.View):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.page.add_option(
            label=data.player.nickname,
            description='Player',
            value=-1
        )
        for i, character in enumerate(data.characters):
            self.page.add_option(
                label=character.name,
                description=f'Lv.{character.level}',
                value=i
            )

    async def on_timeout(self):
        await self.message.edit(view=None)

    @discord.ui.select(
        cls=discord.ui.Select,
        placeholder="Select"
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
