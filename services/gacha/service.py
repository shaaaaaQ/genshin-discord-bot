import asyncio
import logging
import os
import time
from dataclasses import dataclass

import aiohttp
import discord

from services.application_emojis import get_application_emoji


logger = logging.getLogger(__name__)
DEFAULT_API_URL = 'https://api.ennead.cc/mihoyo'
API_URL = (os.getenv('HOYOVERSE_API_URL') or DEFAULT_API_URL).rstrip('/')

ELEMENT_NAMES = {
    'Anemo': '風',
    'Cryo': '氷',
    'Dendro': '草',
    'Electro': '雷',
    'Geo': '岩',
    'Hydro': '水',
    'Pyro': '炎',
}
RARITY_MARKERS = {
    4: '🟪',
    5: '🟨',
}


class GachaError(Exception):
    """A gacha lookup failure that can be shown to the user."""


@dataclass(frozen=True, slots=True)
class GachaItem:
    name: str
    rarity: int
    icon: str | None = None
    element: str | None = None


@dataclass(frozen=True, slots=True)
class GachaBanner:
    name: str
    version: str | None
    characters: tuple[GachaItem, ...]
    weapons: tuple[GachaItem, ...]
    start_time: int | None
    end_time: int | None


def _parse_timestamp(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError('Invalid banner timestamp')
    timestamp = int(value)
    return timestamp if timestamp > 0 else None


def _parse_items(value: object, *, characters: bool) -> tuple[GachaItem, ...]:
    if not isinstance(value, list):
        raise ValueError('Expected a featured item list')

    result: list[GachaItem] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError('Invalid featured item')
        name = item.get('name')
        rarity = item.get('rarity')
        if not isinstance(name, str) or not name.strip():
            raise ValueError('Missing featured item name')
        if isinstance(rarity, bool) or not isinstance(rarity, (int, str)):
            raise ValueError('Missing featured item rarity')
        try:
            rarity_number = int(rarity)
        except ValueError as error:
            raise ValueError('Invalid featured item rarity') from error

        icon = item.get('icon')
        element = item.get('element') if characters else None
        result.append(
            GachaItem(
                name=name.strip(),
                rarity=rarity_number,
                icon=icon if isinstance(icon, str) and icon else None,
                element=(
                    element
                    if isinstance(element, str) and element
                    else None
                ),
            )
        )
    return tuple(result)


def parse_gacha_banners(data: object) -> list[GachaBanner]:
    if not isinstance(data, dict) or not isinstance(data.get('banners'), list):
        raise ValueError('Expected a banner list')

    result: list[GachaBanner] = []
    for item in data['banners']:
        if not isinstance(item, dict):
            raise ValueError('Invalid banner entry')
        name = item.get('name')
        if not isinstance(name, str) or not name.strip():
            raise ValueError('Missing banner name')

        version = item.get('version')
        if version is not None and not isinstance(version, (str, int, float)):
            raise ValueError('Invalid banner version')
        result.append(
            GachaBanner(
                name=name.strip(),
                version=str(version) if version is not None else None,
                characters=_parse_items(
                    item.get('characters', []), characters=True
                ),
                weapons=_parse_items(item.get('weapons', []), characters=False),
                start_time=_parse_timestamp(item.get('start_time')),
                end_time=_parse_timestamp(item.get('end_time')),
            )
        )
    return result


class GachaClient:
    def __init__(self, api_url: str = API_URL) -> None:
        self.api_url = api_url.rstrip('/')
        self._session: aiohttp.ClientSession | None = None

    async def start(self) -> None:
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'genshin-discord-bot'},
        )

    async def close(self) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def fetch(self) -> list[GachaBanner]:
        if self._session is None:
            raise RuntimeError('GachaClient has not been started')
        try:
            async with self._session.get(
                f'{self.api_url}/genshin/calendar',
                params={'lang': 'ja-jp'},
            ) as response:
                if response.status == 429:
                    raise GachaError(
                        'ガチャ情報取得APIが混み合っています。'
                        '少し待ってからお試しください。'
                    )
                response.raise_for_status()
                data = await response.json(content_type=None)
            return parse_gacha_banners(data)
        except GachaError:
            raise
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as error:
            logger.warning('hoyoverse-api gacha lookup failed: %s', error)
            raise GachaError(
                'ガチャ情報を取得できませんでした。時間をおいて再度お試しください。'
            ) from error


def _banner_status(banner: GachaBanner, now: int) -> str:
    if banner.start_time is not None and now < banner.start_time:
        return '開催予定'
    if banner.end_time is not None and now > banner.end_time:
        return '終了'
    return '開催中'


def _format_period(banner: GachaBanner) -> str:
    if banner.start_time is not None and banner.end_time is not None:
        return (
            f'<t:{banner.start_time}:F> ～ <t:{banner.end_time}:F>\n'
            f'終了 <t:{banner.end_time}:R>'
        )
    if banner.end_time is not None:
        return f'<t:{banner.end_time}:F> まで\n終了 <t:{banner.end_time}:R>'
    return '期間情報なし'


def _format_items(items: tuple[GachaItem, ...], *, characters: bool) -> str:
    if not items:
        return '情報なし'
    lines: list[str] = []
    for item in sorted(items, key=lambda entry: entry.rarity, reverse=True):
        marker = RARITY_MARKERS.get(item.rarity)
        rarity_label = marker or f'★{item.rarity}'
        element_label = ''
        if characters and item.element:
            emoji = get_application_emoji(f'element_{item.element.casefold()}')
            element = ELEMENT_NAMES.get(item.element, item.element)
            element_label = f'{emoji or f"[{element}]"} '
        lines.append(f'{rarity_label} {element_label}{item.name}')
    return '\n'.join(lines)


def _field_name(banner: GachaBanner) -> str:
    five_stars = [
        item.name
        for item in banner.characters or banner.weapons
        if item.rarity == 5
    ]
    featured = f' — {" / ".join(five_stars)}' if five_stars else ''
    return f'{banner.name}{featured}'[:256]


def _common_period(banners: list[GachaBanner]) -> tuple[int | None, int | None] | None:
    periods = {(banner.start_time, banner.end_time) for banner in banners}
    return next(iter(periods)) if len(periods) == 1 else None


def create_gacha_embeds(
    banners: list[GachaBanner], *, now: int | None = None
) -> list[discord.Embed]:
    if not banners:
        embed = discord.Embed(
            title='ガチャ情報',
            description='現在表示できるガチャ情報はありません。',
            colour=discord.Colour.gold(),
        )
        embed.set_footer(text='Powered by hoyoverse-api')
        return [embed]

    current_time = int(time.time()) if now is None else now
    versions = sorted({banner.version for banner in banners if banner.version})
    version = f'｜Ver.{versions[0]}' if len(versions) == 1 else ''
    period = _common_period(banners)
    common_status = _banner_status(banners[0], current_time) if period else None
    description = None
    if period:
        description = f'**{common_status}**\n{_format_period(banners[0])}'

    embed = discord.Embed(
        title=f'ガチャ情報{version}',
        description=description,
        colour=(
            discord.Colour.gold()
            if common_status in (None, '開催中')
            else discord.Colour.blue()
        ),
    )
    for banner in banners:
        lines: list[str] = []
        if period is None:
            lines.extend(
                (
                    f'**{_banner_status(banner, current_time)}**',
                    _format_period(banner),
                )
            )
        if banner.characters:
            lines.append(_format_items(banner.characters, characters=True))
        if banner.weapons:
            lines.append(_format_items(banner.weapons, characters=False))
        embed.add_field(
            name=_field_name(banner),
            value='\n'.join(lines) or 'ピックアップ情報なし',
            inline=False,
        )

    featured = banners[0].characters or banners[0].weapons
    if featured and featured[0].icon:
        embed.set_thumbnail(url=featured[0].icon)
    embed.set_footer(text='Powered by hoyoverse-api')
    return [embed]
