import asyncio
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from services.database import DATABASE_PATH


@dataclass(frozen=True, slots=True)
class CodesNotificationSetting:
    guild_id: int
    channel_id: int
    active_keys: set[str] | None


class CodesStateStore:
    def __init__(self, path: Path = DATABASE_PATH) -> None:
        self.path = path

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, timeout=5)
        connection.execute(
            '''
            CREATE TABLE IF NOT EXISTS codes_notification_settings (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER NOT NULL,
                active_keys TEXT
            )
            '''
        )
        connection.commit()
        return connection

    def _get_channel_id(self, guild_id: int) -> int | None:
        connection = self._connect()
        try:
            row = connection.execute(
                '''
                SELECT channel_id FROM codes_notification_settings
                WHERE guild_id = ?
                ''',
                (guild_id,),
            ).fetchone()
            return row[0] if row is not None else None
        finally:
            connection.close()

    async def get_channel_id(self, guild_id: int) -> int | None:
        return await asyncio.to_thread(self._get_channel_id, guild_id)

    def _set_channel(self, guild_id: int, channel_id: int) -> None:
        connection = self._connect()
        try:
            connection.execute(
                '''
                INSERT INTO codes_notification_settings (guild_id, channel_id)
                VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE
                SET channel_id = excluded.channel_id
                ''',
                (guild_id, channel_id),
            )
            connection.commit()
        finally:
            connection.close()

    async def set_channel(self, guild_id: int, channel_id: int) -> None:
        await asyncio.to_thread(self._set_channel, guild_id, channel_id)

    def _remove(self, guild_id: int) -> bool:
        connection = self._connect()
        try:
            cursor = connection.execute(
                'DELETE FROM codes_notification_settings WHERE guild_id = ?',
                (guild_id,),
            )
            connection.commit()
            return cursor.rowcount > 0
        finally:
            connection.close()

    async def remove(self, guild_id: int) -> bool:
        return await asyncio.to_thread(self._remove, guild_id)

    def _get_settings(self) -> list[CodesNotificationSetting]:
        connection = self._connect()
        try:
            rows = connection.execute(
                '''
                SELECT guild_id, channel_id, active_keys
                FROM codes_notification_settings
                '''
            ).fetchall()
        finally:
            connection.close()

        result: list[CodesNotificationSetting] = []
        for guild_id, channel_id, raw_keys in rows:
            active_keys = None
            if raw_keys is not None:
                data = json.loads(raw_keys)
                if not isinstance(data, list) or not all(
                    isinstance(item, str) for item in data
                ):
                    raise ValueError('Invalid exchange code state')
                active_keys = set(data)
            result.append(
                CodesNotificationSetting(guild_id, channel_id, active_keys)
            )
        return result

    async def get_settings(self) -> list[CodesNotificationSetting]:
        return await asyncio.to_thread(self._get_settings)

    def _save_active_keys(self, guild_id: int, keys: set[str]) -> None:
        connection = self._connect()
        try:
            connection.execute(
                '''
                UPDATE codes_notification_settings SET active_keys = ?
                WHERE guild_id = ?
                ''',
                (json.dumps(sorted(keys)), guild_id),
            )
            connection.commit()
        finally:
            connection.close()

    async def save_active_keys(self, guild_id: int, keys: set[str]) -> None:
        await asyncio.to_thread(self._save_active_keys, guild_id, keys)
