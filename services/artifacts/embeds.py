from decimal import Decimal

import discord


def create_artifact_embed(
    translations: dict[str, str],
    stats: dict[str, float],
    score: Decimal,
    rate: Decimal,
) -> discord.Embed:
    embed = discord.Embed()
    stats_text = []
    for attr, value in stats.items():
        suffix = '' if attr.startswith(('fixed', 'elemental_mastery')) else '%'
        stats_text.append(f'{translations[attr]}+{value}{suffix}')
    embed.add_field(name='サブステータス', value='\n'.join(stats_text), inline=False)
    embed.add_field(name='スコア', value=score, inline=False)
    embed.add_field(name='理論値比', value=f'{rate}%', inline=False)
    return embed
