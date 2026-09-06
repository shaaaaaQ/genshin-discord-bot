import logging
from collections import Counter

import discord
import enka
from discord import app_commands
from discord.ext import commands

from .application_emojis import get_application_emoji


logger = logging.getLogger(__name__)

ELEMENT_COLOURS = {
    enka.gi.Element.ANEMO: 0x74C2A8,
    enka.gi.Element.GEO: 0xD3A550,
    enka.gi.Element.ELECTRO: 0xA882C9,
    enka.gi.Element.DENDRO: 0x9DB844,
    enka.gi.Element.PYRO: 0xE77C63,
    enka.gi.Element.CRYO: 0x9FD6E3,
    enka.gi.Element.HYDRO: 0x4A90E2,
}
ARTIFACT_PARTS = {
    enka.gi.EquipmentType.FLOWER: '生の花',
    enka.gi.EquipmentType.FEATHER: '死の羽',
    enka.gi.EquipmentType.SANDS: '時の砂',
    enka.gi.EquipmentType.GOBLET: '空の杯',
    enka.gi.EquipmentType.CIRCLET: '理の冠',
}
STYGIAN_DIFFICULTIES = {
    1: ('イージー', 'stygian_easy'),
    2: ('ノーマル', 'stygian_normal'),
    3: ('ハード', 'stygian_hard'),
    4: ('マスター', 'stygian_master'),
    5: ('エクストラ', 'stygian_extra'),
    6: ('アルティメット', 'stygian_ultimate'),
}


def profile_url(uid: str) -> str:
    return f'https://enka.network/u/{uid}/'


def format_optional(value, suffix='') -> str:
    return f'{value}{suffix}' if value is not None else '非公開'


def format_seconds(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    return f'{minutes}分{seconds:02d}秒' if minutes else f'{seconds}秒'


def format_stygian(difficulty: int, clear_time: int | None) -> str:
    name, emoji_name = STYGIAN_DIFFICULTIES.get(
        difficulty, (f'難度 {difficulty}', '')
    )
    emoji = get_application_emoji(emoji_name)
    result = emoji or name
    if clear_time is not None:
        separator = ' ' if emoji else ' / '
        result += f'{separator}{format_seconds(clear_time)}'
    return result


def create_player_embed(data: enka.gi.ShowcaseResponse) -> discord.Embed:
    player = data.player
    embed = discord.Embed(
        title=player.nickname or '名前不明',
        url=profile_url(data.uid),
        description=player.signature or None,
        colour=discord.Colour.blurple(),
    )
    if player.profile_picture_icon.side_icon_ui_path:
        embed.set_thumbnail(url=player.profile_picture_icon.circle)
    if player.namecard.ui_path:
        embed.set_image(url=player.namecard.full)

    embed.add_field(name='冒険ランク', value=player.level)
    embed.add_field(name='世界ランク', value=player.world_level)
    embed.add_field(name='アチーブメント', value=f'{player.achievements:,}')

    abyss = '未挑戦 / 非公開'
    if player.abyss_floor:
        abyss = f'{player.abyss_floor}-{player.abyss_level}'
        if player.abyss_stars is not None:
            abyss += f' / {player.abyss_stars}★'
    embed.add_field(name='深境螺旋', value=abyss)

    theater = '未挑戦 / 非公開'
    if player.theater_act:
        theater = f'第{player.theater_act}幕'
        if player.theater_stars is not None:
            theater += f' / {player.theater_stars}★'
    embed.add_field(name='幻想シアター', value=theater)

    stygian = '未挑戦 / 非公開'
    if player.stygian_difficulty is not None:
        stygian = format_stygian(
            player.stygian_difficulty, player.stygian_clear_time
        )
    embed.add_field(name='幽境の激戦', value=stygian)

    embed.add_field(
        name='好感度Lv.10',
        value=format_optional(player.max_friendship_character_count, '人'),
    )
    embed.add_field(
        name='公開キャラクター', value=f'{len(player.showcase_characters)}人'
    )
    embed.set_footer(text='Powered by Enka.Network')
    return embed


def get_stat(character: enka.gi.Character, stat_type: enka.gi.FightPropType):
    stat = character.stats.get(stat_type)
    return stat.formatted_value if stat is not None else '—'


def format_weapon(weapon: enka.gi.Weapon) -> str:
    stats = '\n'.join(f'{stat.name}: **{stat.formatted_value}**' for stat in weapon.stats)
    return (
        f'**{weapon.name}**  {"★" * weapon.rarity}\n'
        f'Lv.{weapon.level}/{weapon.max_level}・精錬{weapon.refinement}\n{stats}'
    )


def format_talents(character: enka.gi.Character) -> str:
    order = {talent_id: index for index, talent_id in enumerate(character.talent_order)}
    talents = sorted(character.talents, key=lambda talent: order.get(talent.id, 99))
    lines = []
    for talent in talents[:3]:
        level = f'**{talent.level}**' if talent.is_upgraded else str(talent.level)
        lines.append(f'{talent.name or "天賦"}: Lv.{level}')
    return '\n'.join(lines) or '情報なし'


def format_artifact(artifact: enka.gi.Artifact) -> str:
    sub_stats = ' / '.join(
        f'{stat.name} {stat.formatted_value}' for stat in artifact.sub_stats
    )
    return (
        f'**{artifact.set_name}**  +{artifact.level}\n'
        f'{artifact.main_stat.name}: **{artifact.main_stat.formatted_value}**\n'
        f'{sub_stats or "サブ効果なし"}'
    )


def create_character_embed(
    data: enka.gi.ShowcaseResponse,
    character: enka.gi.Character,
) -> discord.Embed:
    embed = discord.Embed(
        title=character.name,
        url=profile_url(data.uid),
        description=(
            f'Lv.{character.level}/{character.max_level}・命ノ星座 '
            f'{character.constellations_unlocked}・好感度 {character.friendship_level}'
        ),
        colour=ELEMENT_COLOURS.get(character.element, discord.Colour.blurple().value),
    )
    if character.icon.side_icon_ui_path:
        embed.set_thumbnail(url=character.icon.front)
    if character.namecard is not None and character.namecard.ui_path:
        embed.set_image(url=character.namecard.full)
    player = data.player
    embed.set_author(
        name=player.nickname or data.uid,
        url=profile_url(data.uid),
        icon_url=(
            player.profile_picture_icon.circle
            if player.profile_picture_icon.side_icon_ui_path else None
        ),
    )

    stats = [
        ('HP', enka.gi.FightPropType.FIGHT_PROP_MAX_HP),
        ('攻撃力', enka.gi.FightPropType.FIGHT_PROP_CUR_ATTACK),
        ('防御力', enka.gi.FightPropType.FIGHT_PROP_CUR_DEFENSE),
        ('元素熟知', enka.gi.FightPropType.FIGHT_PROP_ELEMENT_MASTERY),
        ('会心率', enka.gi.FightPropType.FIGHT_PROP_CRITICAL),
        ('会心ダメージ', enka.gi.FightPropType.FIGHT_PROP_CRITICAL_HURT),
        ('元素チャージ効率', enka.gi.FightPropType.FIGHT_PROP_CHARGE_EFFICIENCY),
    ]
    stat_text = '\n'.join(f'{name}: **{get_stat(character, kind)}**' for name, kind in stats)
    specialized = character.specialized_stat
    if specialized.value > 0:
        stat_text += f'\n{specialized.name}: **{specialized.formatted_value}**'
    embed.add_field(name='ステータス', value=stat_text, inline=True)
    embed.add_field(name='武器', value=format_weapon(character.weapon), inline=True)
    embed.add_field(name='天賦', value=format_talents(character), inline=False)

    set_counts = Counter(artifact.set_name for artifact in character.artifacts)
    active_sets = [
        f'{name} {4 if count >= 4 else 2}セット'
        for name, count in set_counts.items()
        if count >= 2
    ]
    if active_sets:
        embed.add_field(name='セット効果', value='\n'.join(active_sets), inline=False)

    artifacts = sorted(
        character.artifacts,
        key=lambda artifact: list(ARTIFACT_PARTS).index(artifact.equip_type),
    )
    for artifact in artifacts:
        embed.add_field(
            name=ARTIFACT_PARTS.get(artifact.equip_type, '聖遺物'),
            value=format_artifact(artifact),
            inline=False,
        )
    embed.set_footer(text='Powered by Enka.Network')
    return embed


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
                description=f'Lv.{character.level} / C{character.constellations_unlocked}',
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
    @app_commands.describe(uid='原神のUID')
    async def profile(self, ctx: commands.Context, uid: str):
        uid = uid.strip()
        if not uid.isascii() or not uid.isdecimal() or len(uid) not in (9, 10):
            await ctx.reply('UIDは9～10桁の半角数字で入力してください。', mention_author=False)
            return

        await ctx.defer()
        try:
            async with enka.GenshinClient(enka.gi.Language.JAPANESE) as client:
                data = await client.fetch_showcase(uid)
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
