import asyncio
import logging
import sqlite3

from services.database import DATABASE_PATH


logger = logging.getLogger(__name__)


def _connect() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, timeout=5)
    connection.execute(
        '''
        CREATE TABLE IF NOT EXISTS user_uids (
            discord_user_id INTEGER PRIMARY KEY,
            uid TEXT NOT NULL
        )
        '''
    )
    connection.commit()
    return connection


def _get_user_uid(discord_user_id: int) -> str | None:
    connection = _connect()
    try:
        row = connection.execute(
            'SELECT uid FROM user_uids WHERE discord_user_id = ?',
            (discord_user_id,),
        ).fetchone()
        return row[0] if row is not None else None
    finally:
        connection.close()


def _save_user_uid(discord_user_id: int, uid: str) -> None:
    connection = _connect()
    try:
        connection.execute(
            '''
            INSERT INTO user_uids (discord_user_id, uid) VALUES (?, ?)
            ON CONFLICT(discord_user_id) DO UPDATE SET uid = excluded.uid
            ''',
            (discord_user_id, uid),
        )
        connection.commit()
    finally:
        connection.close()


async def get_user_uid(discord_user_id: int) -> str | None:
    try:
        return await asyncio.to_thread(_get_user_uid, discord_user_id)
    except (OSError, sqlite3.Error):
        logger.exception('保存済みUIDの読み込みに失敗しました')
        return None


async def save_user_uid(discord_user_id: int, uid: str) -> None:
    try:
        await asyncio.to_thread(_save_user_uid, discord_user_id, uid)
    except (OSError, sqlite3.Error):
        logger.exception('UIDの保存に失敗しました')
