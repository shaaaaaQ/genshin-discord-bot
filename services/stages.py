import asyncio
import logging
import os
from typing import Literal
from urllib.parse import urlencode

import aiohttp
import discord


logger = logging.getLogger(__name__)
DEFAULT_BASE_URL = 'https://octavia.kj415j45.space'
BASE_URL = (os.getenv('OCTAVIA_API_URL') or DEFAULT_BASE_URL).rstrip('/')
REGIONS = {
    'os_asia': 'Asia',
    'os_usa': 'America',
    'os_euro': 'Europe',
    'os_cht': 'Taiwan / Hong Kong / Macau',
    'cn_gf01': 'China (Celestia)',
    'cn_qd01': 'China (Irminsul)',
}
Region = Literal['os_asia', 'os_usa', 'os_euro', 'os_cht', 'cn_gf01', 'cn_qd01']


class StageError(Exception):
    """A stage lookup failure that can be shown to the user."""


class StageClient:
    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None

    async def start(self) -> None:
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )

    async def close(self) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def fetch(self, guid: str, region: str | None = None) -> dict:
        if self._session is None:
            raise RuntimeError('StageClient has not been started')
        params = {'id': guid}
        if region:
            params['region'] = region
        try:
            async with self._session.get(
                f'{BASE_URL}/api/stage', params=params
            ) as response:
                if response.status == 404:
                    raise StageError(
                        '幻境が見つかりませんでした。GUIDとサーバーを確認してください。'
                    )
                if response.status == 429:
                    raise StageError(
                        'Octavia APIが混み合っています。少し待ってからお試しください。'
                    )
                if response.status == 400:
                    raise StageError('GUIDまたはサーバーを確認してください。')
                response.raise_for_status()
                data = await response.json()
            if not isinstance(data, dict) or not isinstance(data.get('level'), dict):
                raise ValueError('Missing level')
            level = data['level']
            if not isinstance(level.get('meta'), dict) or not level.get('id'):
                raise ValueError('Missing stage metadata')
            return data
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as error:
            logger.warning('Octavia lookup failed for GUID %s: %s', guid, error)
            raise StageError(
                'ステージ情報を取得できませんでした。時間をおいて再度お試しください。'
            ) from error


def _clipped(value, limit):
    text = str(value)
    return text if len(text) <= limit else text[:limit - 1] + '…'


def _image_url(value):
    return value if isinstance(value, str) and value.startswith('https://') else None


def _stage_url(level):
    region = level.get('region')
    if region not in REGIONS:
        return f'{BASE_URL}/?{urlencode({"stages": level["id"]})}'
    domain = 'act.miyoushe.com' if region in ('cn_gf01', 'cn_qd01') else 'act.hoyolab.com'
    query = urlencode({'id': level['id'], 'region': region})
    return f'https://{domain}/ys/ugc_community/mx/#/pages/level-detail/index?{query}'


def create_stage_embed(data: dict) -> discord.Embed:
    level = data['level']
    meta = level['meta']
    description = '\n\n'.join(dict.fromkeys(
        str(value) for value in (meta.get('intro'), meta.get('description')) if value
    ))
    embed = discord.Embed(
        title=_clipped(meta.get('name') or '名前不明の幻境', 256),
        url=_stage_url(level),
        description=_clipped(description, 2400) or None,
        colour=discord.Colour.teal(),
    )

    def field(name, value):
        if value is not None and value != '':
            embed.add_field(name=name, value=_clipped(value, 256))

    field('GUID', level['id'])
    field('サーバー', REGIONS.get(level.get('region'), level.get('region')))
    author = data.get('author') or {}
    profiles = [author.get(key) or {} for key in ('game', 'hyl', 'mys')]
    name = next((p['name'] for p in profiles if p.get('name')), '作者不明')
    avatar = next(
        (_image_url(p.get('avatar')) for p in profiles if _image_url(p.get('avatar'))),
        None,
    )
    embed.set_author(name=_clipped(name, 256), icon_url=avatar)
    players = meta.get('players') or {}
    minimum, maximum = players.get('min'), players.get('max')
    if minimum is not None and maximum is not None:
        field('参加人数', f'{minimum}人' if minimum == maximum else f'{minimum}～{maximum}人')
    else:
        field('参加人数', players.get('str'))
    field('ジャンル', meta.get('type'))
    field('カテゴリ', meta.get('category'))
    field('タグ', ' / '.join(meta.get('tags') or []))
    field('人気度', meta.get('hotScore'))
    field('好評率', meta.get('goodRate'))
    field('コメント数', meta.get('comments'))
    field('バージョン', (level.get('version') or {}).get('latest'))
    cover = meta.get('cover') or {}
    images = cover.get('images') or []
    image = next(
        (url for url in images if _image_url(url)),
        _image_url(cover.get('videoCover')),
    )
    if image:
        embed.set_image(url=image)
    status = data.get('status') or {}
    notes = ['Powered by Octavia']
    if status.get('cache'):
        notes.append('Cached data')
    if status.get('removed'):
        notes.append('Possibly removed')
    if status.get('upstream') is False:
        notes.append('Upstream unavailable')
    embed.set_footer(text=' / '.join(notes))
    return embed
