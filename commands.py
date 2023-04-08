from io import BytesIO
from discord.ext import commands
from PIL import Image
from decimal import Decimal
import discord
import requests
import pyocr


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
        score = self.calc_score(t, stats)[mh]
        embed = self.create_embed(t, stats, score)
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
        return Decimal(stat.split('+')[1].replace('%', ''))

    def calc_score(self, t, stats):
        score = {
            'crit': 0,
            'atk': 0,
            'hp': 0
        }
        for stat in stats:
            stat = stat[1:]
            value = self.get_value(stat)
            if stat.startswith(t['crit_rate']):
                score['crit'] += value*2
            if stat.startswith(t['crit_dmg']):
                score['crit'] += value
            if stat.startswith(t['atk']) and stat.endswith('%'):
                score['atk'] += value
            if stat.startswith(t['hp']) and stat.endswith('%'):
                score['hp'] += value
        score['atk'] += score['crit']
        score['hp'] += score['crit']
        print(score)
        return score

    def create_embed(self, t, stats, score):
        embed = discord.Embed()
        embed.add_field(name='サブステータス',
                        value='\n'.join(stats), inline=False)
        embed.add_field(name='スコア', value=score, inline=False)
        return embed


async def setup(bot):
    await bot.add_cog(Artifact(bot))
