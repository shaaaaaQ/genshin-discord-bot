from io import BytesIO

from discord.ext import commands
from PIL import Image
import discord
import requests
import pyocr

from .theoretical_artifact_score import ArtifactScore


tools = pyocr.get_available_tools()

locales = {
    'en': {
        'code': 'eng',
        'crit_rate': 'CRIT Rate',
        'crit_dmg': 'CRIT DMG',
        'atk': 'ATK',
        'hp': 'HP'
    },
    'ru': {
        'code': 'rus',
        'crit_rate': 'Шанс крит. попадания',
        'crit_dmg': 'Крит. урон',
        'atk': 'Сила атаки',
        'hp': 'HP'
    },
    'vi': {
        'code': 'vie',
        'crit_rate': 'Tỷ Lệ Bạo Kích',
        'crit_dmg': 'ST Bạo Kích',
        'atk': 'Tấn Công',
        'hp': 'HP'
    },
    'th': {
        'code': 'tha',
        'crit_rate': 'อัตราคริ',
        'crit_dmg': 'ความแรงคริ',
        'atk': 'พลังโจมตี',
        'hp': 'พลังชีวิต'
    },
    'pt': {
        'code': 'por',
        'crit_rate': 'Taxa Crítica',
        'crit_dmg': 'Dano Crítico',
        'atk': 'ATQ',
        'hp': 'Vida'
    },
    'ko': {
        'code': 'kor',
        'crit_rate': '치명타 확률',
        'crit_dmg': '치명타 피해',
        'atk': '공격력',
        'hp': 'HP'
    },
    'ja': {
        'code': 'jpn',
        'crit_rate': '会心率',
        'crit_dmg': '会心ダメージ',
        'atk': '攻撃力',
        'hp': 'HP'
    },
    'id': {
        'code': 'ind',
        'crit_rate': 'CRIT Rate',
        'crit_dmg': 'CRIT DMG',
        'atk': 'ATK',
        'hp': 'HP'
    },
    'fr': {
        'code': 'fra',
        'crit_rate': 'Taux CRIT',
        'crit_dmg': 'DGT CRIT',
        'atk': 'ATQ',
        'hp': 'PV'
    },
    'es': {
        'code': 'spa',
        'crit_rate': 'Prob. CRIT',
        'crit_dmg': 'Daño CRIT',
        'atk': 'ATQ',
        'hp': 'Vida'
    },
    'de': {
        'code': 'deu',
        'crit_rate': 'KT',
        'crit_dmg': 'KSCH',
        'atk': 'ANG',
        'hp': 'LP'
    },
    'zh-TW': {
        'code': 'chi_tra',
        'crit_rate': '暴擊率',
        'crit_dmg': '暴擊傷害',
        'atk': '攻擊力',
        'hp': '生命值'
    },
    'zh-CN': {
        'code': 'chi_sim',
        'crit_rate': '暴击率',
        'crit_dmg': '暴击伤害',
        'atk': '攻击力',
        'hp': '生命值'
    },
    'it': {
        'code': 'ita',
        'crit_rate': 'Tasso di CRIT',
        'crit_dmg': 'DAN da CRIT',
        'atk': 'ATT',
        'hp': 'PS'
    },
    'tr': {
        'code': 'tur',
        'crit_rate': 'Kritik Oranı',
        'crit_dmg': 'Kritik Hasar',
        'atk': 'Saldırı',
        'hp': 'Can'
    }
}


class LangConv(commands.Converter):
    async def convert(self, ctx, lang):
        if lang not in locales.keys():
            await ctx.reply('その言語対応してない')
            lang = 'ja'
        return lang


class Artifact(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredAttachment):
            await ctx.reply('添付ファイルがない')
        elif isinstance(error, commands.CommandNotFound):
            pass
        else:
            await ctx.reply('error')
            print(error)

    @commands.hybrid_command()
    async def crit(self, ctx, attachment: discord.Attachment,
                   lang: LangConv = 'ja'):
        """
        画像からスコア計算(会心のみ)
        会心率 * 2 + 会心ダメージ
        """
        await self.proc(ctx, lang, attachment, 'crit')

    @commands.hybrid_command()
    async def atk(self, ctx, attachment: discord.Attachment,
                  lang: LangConv = 'ja'):
        """
        画像からスコア計算(攻撃力%)
        会心率 * 2 + 会心ダメージ + 攻撃力%
        """
        await self.proc(ctx, lang, attachment, 'atk')

    @commands.hybrid_command()
    async def hp(self, ctx, attachment: discord.Attachment,
                 lang: LangConv = 'ja'):
        """
        画像からスコア計算(HP%)
        会心率 * 2 + 会心ダメージ + HP%
        """
        await self.proc(ctx, lang, attachment, 'hp')

    async def proc(self, ctx, lang, attachment, mh):
        t = locales[lang]
        url = attachment.url
        stats = self.get_stats(t, url)
        score, rate = self.calc_score(t, stats)[mh]
        embed = self.create_embed(t, stats, score, rate)
        await ctx.reply(embed=embed)

    def get_stats(self, t, url):
        img = Image.open(BytesIO(requests.get(url).content))
        text = tools[0].image_to_string(img, t['code'])
        print(text)
        stats = []
        for text in text.splitlines():
            if (text.startswith('+ ') or
                text.startswith('* ') or
                    text.startswith('; ')):
                text = '・' + text[2:]
            if text.endswith('%6'):
                text = text[:-1]
            if text.startswith('・'):
                stats.append(text)
        return stats

    def get_value(self, stat):
        return float(stat.split('+')[1].replace('%', ''))

    def calc_score(self, t, stats):
        extracted_stats = {}
        for stat in stats:
            stat = stat[1:]
            value = self.get_value(stat)
            if stat.startswith(t['crit_rate']):
                extracted_stats['crit_rate'] = value
            if stat.startswith(t['crit_dmg']):
                extracted_stats['crit_dmg'] = value
            if stat.startswith(t['atk']) and stat.endswith('%'):
                extracted_stats['rated_atk'] = value
            if stat.startswith(t['hp']) and stat.endswith('%'):
                extracted_stats['rated_hp'] = value
        score = ArtifactScore(**extracted_stats)
        return {
            'crit': (
                score.calc_general_rate('crit_only'),
                score.calc_theoretical_rate(['crit_dmg', 'crit_rate']),
            ),
            'atk': (
                score.calc_general_rate('rated_atk'),
                score.calc_theoretical_rate(['crit_dmg', 'crit_rate', 'rated_atk']),
            ),
            'hp': (
                score.calc_general_rate('rated_hp'),
                score.calc_theoretical_rate(['crit_dmg', 'crit_rate', 'rated_hp']),
            ),
        }

    def create_embed(self, t, stats, score, rate):
        embed = discord.Embed()
        embed.add_field(name='サブステータス',
                        value='\n'.join(stats), inline=False)
        embed.add_field(name='スコア', value=score, inline=False)
        embed.add_field(name='理論値比', value=f'{rate}%', inline=False)
        return embed


async def setup(bot):
    await bot.add_cog(Artifact(bot))
