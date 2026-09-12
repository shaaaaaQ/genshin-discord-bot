import asyncio
import logging
import os
from dataclasses import dataclass

import aiohttp
import discord


logger = logging.getLogger(__name__)
DEFAULT_API_URL = 'https://api.ennead.cc/mihoyo'
API_URL = (os.getenv('HOYOVERSE_API_URL') or DEFAULT_API_URL).rstrip('/')


class EventsError(Exception):
    """An event lookup failure that can be shown to the user."""


@dataclass(frozen=True, slots=True)
class EventReward:
    name: str
    amount: int | None
    icon: str | None = None


@dataclass(frozen=True, slots=True)
class GameEvent:
    name: str
    image_url: str | None
    start_time: int | None
    end_time: int | None
    rewards: tuple[EventReward, ...]
    special_reward: EventReward | None


def _parse_timestamp(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError('Invalid event timestamp')
    timestamp = int(value)
    return timestamp if timestamp > 0 else None


def _parse_reward(value: object) -> EventReward:
    if not isinstance(value, dict):
        raise ValueError('Invalid event reward')
    name = value.get('name')
    if not isinstance(name, str) or not name.strip():
        raise ValueError('Missing event reward name')

    amount_value = value.get('amount')
    if amount_value is None:
        amount = None
    elif isinstance(amount_value, bool) or not isinstance(
        amount_value, (int, float)
    ):
        raise ValueError('Invalid event reward amount')
    else:
        amount = int(amount_value)

    icon = value.get('icon')
    return EventReward(
        name=name.strip(),
        amount=amount,
        icon=icon if isinstance(icon, str) and icon else None,
    )


def parse_events(data: object) -> list[GameEvent]:
    if not isinstance(data, dict) or not isinstance(data.get('events'), list):
        raise ValueError('Expected an event list')

    result: list[GameEvent] = []
    for item in data['events']:
        if not isinstance(item, dict):
            raise ValueError('Invalid event entry')
        name = item.get('name')
        if not isinstance(name, str) or not name.strip():
            raise ValueError('Missing event name')

        image_url = item.get('image_url')
        rewards_value = item.get('rewards', [])
        if not isinstance(rewards_value, list):
            raise ValueError('Invalid event reward list')
        special_value = item.get('special_reward')

        result.append(
            GameEvent(
                name=name.strip(),
                image_url=(
                    image_url
                    if isinstance(image_url, str) and image_url
                    else None
                ),
                start_time=_parse_timestamp(item.get('start_time')),
                end_time=_parse_timestamp(item.get('end_time')),
                rewards=tuple(_parse_reward(reward) for reward in rewards_value),
                special_reward=(
                    _parse_reward(special_value)
                    if special_value is not None
                    else None
                ),
            )
        )
    return result


class EventsClient:
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

    async def fetch(self) -> list[GameEvent]:
        if self._session is None:
            raise RuntimeError('EventsClient has not been started')
        try:
            async with self._session.get(
                f'{self.api_url}/genshin/calendar',
                params={'lang': 'ja-jp'},
            ) as response:
                if response.status == 429:
                    raise EventsError(
                        'イベント情報取得APIが混み合っています。'
                        '少し待ってからお試しください。'
                    )
                response.raise_for_status()
                data = await response.json(content_type=None)
            return parse_events(data)
        except EventsError:
            raise
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as error:
            logger.warning('hoyoverse-api event lookup failed: %s', error)
            raise EventsError(
                'イベント情報を取得できませんでした。時間をおいて再度お試しください。'
            ) from error


def _format_period(event: GameEvent) -> str | None:
    if event.start_time is not None and event.end_time is not None:
        return (
            f'<t:{event.start_time}:d> ～ <t:{event.end_time}:d>'
            f'（終了 <t:{event.end_time}:R>）'
        )
    if event.end_time is not None:
        return f'<t:{event.end_time}:d>まで（終了 <t:{event.end_time}:R>）'
    if event.start_time is not None:
        return f'<t:{event.start_time}:d>から'
    return None


def _format_rewards(event: GameEvent) -> str | None:
    candidates = [event.special_reward] if event.special_reward is not None else []
    candidates.extend(
        reward
        for reward in event.rewards
        if reward.amount is None or reward.amount > 0
    )
    unique: list[EventReward] = []
    seen: set[str] = set()
    for reward in candidates:
        if reward.name in seen:
            continue
        seen.add(reward.name)
        unique.append(reward)

    if not unique:
        return None
    shown = unique[:3]
    labels = [
        f'{reward.name} ×{reward.amount}'
        if reward.amount is not None and reward.amount > 0
        else reward.name
        for reward in shown
    ]
    if len(unique) > len(shown):
        labels.append(f'ほか{len(unique) - len(shown)}種')
    return ' / '.join(labels)


def create_events_embed(events: list[GameEvent]) -> discord.Embed:
    embed = discord.Embed(title='イベント情報', colour=discord.Colour.green())
    embed.set_footer(text='Powered by hoyoverse-api')
    dated_events = [
        event
        for event in events
        if event.start_time is not None or event.end_time is not None
    ]
    if not dated_events:
        embed.description = '現在表示できるゲーム内イベントはありません。'
        return embed

    displayed_count = 0
    character_count = len(embed.title or '') + len(embed.footer.text or '')
    for event in dated_events[:25]:
        period = _format_period(event)
        lines = [period] if period is not None else []
        rewards = _format_rewards(event)
        if rewards:
            lines.append(f'主な報酬：{rewards}')
        field_name = event.name[:256]
        field_value = ('\n'.join(lines) or '報酬情報なし')[:1024]
        if displayed_count and character_count + len(field_name) + len(field_value) > 5_500:
            break
        embed.add_field(name=field_name, value=field_value, inline=False)
        displayed_count += 1
        character_count += len(field_name) + len(field_value)

    if len(dated_events) > displayed_count:
        embed.description = (
            f'全{len(dated_events)}件のうち{displayed_count}件を表示しています。'
        )
    return embed
