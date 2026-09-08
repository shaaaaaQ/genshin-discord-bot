import asyncio
import logging
import os
from dataclasses import dataclass
from urllib.parse import urlencode

import aiohttp
import discord


logger = logging.getLogger(__name__)
DEFAULT_API_URL = 'https://api.ennead.cc/mihoyo'
API_URL = (os.getenv('HOYOVERSE_API_URL') or DEFAULT_API_URL).rstrip('/')
REDEEM_URL = 'https://genshin.hoyoverse.com/en/gift'


class CodesError(Exception):
    """A code lookup failure that can be shown to the user."""


@dataclass(frozen=True, slots=True)
class RedemptionCode:
    code: str
    rewards: tuple[str, ...]

    @property
    def key(self) -> str:
        """Stable identifier for comparing results from periodic checks."""
        return self.code.casefold()

    @property
    def redeem_url(self) -> str:
        return f'{REDEEM_URL}?{urlencode({"code": self.code})}'


def parse_codes(data: object) -> list[RedemptionCode]:
    if not isinstance(data, dict) or not isinstance(data.get('active'), list):
        raise ValueError('Expected an active code list')

    result: list[RedemptionCode] = []
    for item in data['active']:
        if not isinstance(item, dict):
            raise ValueError('Invalid code entry')
        code = item.get('code')
        if not isinstance(code, str) or not code.strip():
            raise ValueError('Missing code')
        code = code.strip()

        raw_rewards = item.get('rewards')
        if raw_rewards is None:
            raw_rewards = item.get('reward', [])
        if not isinstance(raw_rewards, list):
            raise ValueError('Invalid rewards')
        rewards = tuple(
            reward.strip()
            for reward in raw_rewards
            if isinstance(reward, str) and reward.strip()
        )
        result.append(RedemptionCode(code=code, rewards=rewards))
    return result


class CodesClient:
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

    async def fetch(self) -> list[RedemptionCode]:
        if self._session is None:
            raise RuntimeError('CodesClient has not been started')
        try:
            async with self._session.get(
                f'{self.api_url}/genshin/codes'
            ) as response:
                if response.status == 429:
                    raise CodesError(
                        'コード取得APIが混み合っています。少し待ってからお試しください。'
                    )
                response.raise_for_status()
                data = await response.json(content_type=None)
            return parse_codes(data)
        except CodesError:
            raise
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as error:
            logger.warning('hoyoverse-api lookup failed: %s', error)
            raise CodesError(
                '交換コードを取得できませんでした。時間をおいて再度お試しください。'
            ) from error


def create_codes_embeds(codes: list[RedemptionCode]) -> list[discord.Embed]:
    if not codes:
        embed = discord.Embed(
            title='原神の交換コード',
            description='現在利用できる交換コードはありません。',
            colour=discord.Colour.gold(),
        )
        embed.set_footer(text='Powered by hoyoverse-api')
        return [embed]

    embeds: list[discord.Embed] = []
    page: list[RedemptionCode] = []
    page_chars = 100
    pages: list[list[RedemptionCode]] = []
    for entry in codes:
        rewards = ' / '.join(entry.rewards) or '報酬情報なし'
        entry_chars = len(entry.code[:256]) + min(len(rewards), 960) + 80
        if page and (len(page) == 25 or page_chars + entry_chars > 5500):
            pages.append(page)
            page = []
            page_chars = 100
        page.append(entry)
        page_chars += entry_chars
    pages.append(page)

    for index, page in enumerate(pages):
        embed = discord.Embed(
            title='原神の交換コード' if index == 0 else '原神の交換コード（続き）',
            colour=discord.Colour.gold(),
            url=REDEEM_URL,
        )
        for entry in page:
            rewards = ' / '.join(entry.rewards) or '報酬情報なし'
            if len(rewards) > 960:
                rewards = rewards[:959] + '…'
            embed.add_field(
                name=entry.code[:256],
                value=f'{rewards}\n[交換ページを開く]({entry.redeem_url})\n\u200b',
                inline=False,
            )
        if index == 0:
            embed.set_footer(text='Powered by hoyoverse-api')
        embeds.append(embed)
    return embeds
