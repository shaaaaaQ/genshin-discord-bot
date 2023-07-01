import logging

import discord
from discord.ext import commands
from enkanetwork import EnkaNetworkAPI, EquipmentsType
from enkanetwork.model.character import CharacterInfo

client = EnkaNetworkAPI(lang='jp')

logger = logging.getLogger(__name__)

ja = {
    'Anemo': '風',
    'Cryo': '氷',
    'Dendro': '草',
    'Electro': '雷',
    'Geo': '岩',
    'Hydro': '水',
    'Pyro': '炎',
    'EQUIP_BRACER': "花",
    'EQUIP_NECKLACE': "羽",
    'EQUIP_SHOES': "時計",
    'EQUIP_RING': "杯",
    'EQUIP_DRESS': "冠"
}

percent_stats = [
    'FIGHT_PROP_HP_PERCENT',
    'FIGHT_PROP_ATTACK_PERCENT',
    'FIGHT_PROP_DEFENSE_PERCENT',
    'FIGHT_PROP_CRITICAL',
    'FIGHT_PROP_CRITICAL_HURT',
    'FIGHT_PROP_CHARGE_EFFICIENCY',
    'FIGHT_PROP_HEAL_ADD',
    'FIGHT_PROP_PHYSICAL_ADD_HURT',
    'FIGHT_PROP_FIRE_ADD_HURT',
    'FIGHT_PROP_ELEC_ADD_HURT',
    'FIGHT_PROP_WATER_ADD_HURT',
    'FIGHT_PROP_WIND_ADD_HURT',
    'FIGHT_PROP_ICE_ADD_HURT',
    'FIGHT_PROP_ROCK_ADD_HURT',
    'FIGHT_PROP_GRASS_ADD_HURT',
]


def create_player_embed(data):
    player = data.player
    profile = data.profile

    # player.avatarの元素かなんかに合わせて色変えたい
    embed = discord.Embed(
        description=player.signature
    )
    embed.set_author(
        name=player.nickname,
        url=profile.url,
        icon_url=player.avatar.icon.url
    )
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
        '与える治療効果': stats.FIGHT_PROP_HEAL_ADD.to_percentage(),
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
        bonus = f'{ja[character.element]}元素ダメージ'

    artifacts = []

    for equip in character.equipments:
        if equip.type == EquipmentsType.WEAPON:
            weapon = equip
        elif equip.type == EquipmentsType.ARTIFACT:
            artifacts.append(equip)

    # 元素かなんかに合わせて色変えたい
    embed = discord.Embed(
        title=character.name,
        description=f'Lv.{character.level} / C{character.constellations_unlocked} / 好感度{character.friendship_level}'
    )
    embed.set_author(
        name=data.player.nickname,
        url=data.profile.url,
        icon_url=data.player.avatar.icon.url
    )
    embed.set_thumbnail(url=character.image.icon.url)
    embed.add_field(
        name='ステータス',
        value=f'''
```ansi
\u001b[0mHP: \u001b[36m{stats.FIGHT_PROP_MAX_HP.to_rounded()}
\u001b[0m攻撃力: \u001b[36m{stats.FIGHT_PROP_CUR_ATTACK.to_rounded()}
\u001b[0m防御力: \u001b[36m{stats.FIGHT_PROP_CUR_DEFENSE.to_rounded()}
\u001b[0m元素熟知: \u001b[36m{stats.FIGHT_PROP_ELEMENT_MASTERY.to_rounded()}
\u001b[0m会心率: \u001b[36m{stats.FIGHT_PROP_CRITICAL.to_percentage()}%
\u001b[0m会心ダメージ: \u001b[36m{stats.FIGHT_PROP_CRITICAL_HURT.to_percentage()}%
\u001b[0m元素チャージ効率: \u001b[36m{stats.FIGHT_PROP_CHARGE_EFFICIENCY.to_percentage()}%
\u001b[0m{bonus}: \u001b[36m{bonuses[bonus]}%
```
        '''
    )

    texts = []
    for i, name in enumerate(['通常攻撃', '元素スキル', '元素爆発']):
        skill = character.skills[i]
        texts.append(
            f'\u001b[0m{name}: \u001b[{"34" if skill.is_boosted else "36" }m{skill.level}')
    text = '\n'.join(texts)
    embed.add_field(
        name='天賦',
        value=f'''
```ansi
{text}
```
        '''
    )

    texts = [
        f'\u001b[1;36m{weapon.detail.name}',
        f'\u001b[0mLevel: \u001b[36m{weapon.level}',
        f'\u001b[0m精錬ランク: \u001b[36m{weapon.refinement}',
        '',
        f'\u001b[0m基礎攻撃力: \u001b[36m{weapon.detail.mainstats.value}'
    ]
    if weapon.detail.substats:
        substat = weapon.detail.substats[0]
        texts.append(
            f'\u001b[0m{substat.name}: \u001b[36m{substat.value}{"%" if substat.prop_id in percent_stats else ""}')
    text = '\n'.join(texts)
    embed.add_field(
        name='武器',
        value=f'''
```ansi
{text}
```
        '''
    )

    for artifact in artifacts:
        mainstat = artifact.detail.mainstats
        substats = artifact.detail.substats
        texts = [
            f'\u001b[1;33m{artifact.detail.name} \u001b[36m+{artifact.level}',
            f'\u001b[0m{mainstat.name}: \u001b[36m{mainstat.value}{"%" if mainstat.prop_id in percent_stats else ""}'
        ]
        if substats:
            texts.append('')
            for stat in substats:
                texts.append(
                    f'\u001b[0m{stat.name}: \u001b[36m{stat.value}{"%" if stat.prop_id in percent_stats else ""}')
        text = '\n'.join(texts)
        embed.add_field(
            name=ja[artifact.detail.artifact_type.value],
            value=f'''
```ansi
{text}
```
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
