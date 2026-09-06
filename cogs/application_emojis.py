import logging
from pathlib import Path

import aiohttp
import discord


logger = logging.getLogger(__name__)
EMOJI_DIRECTORY = Path(__file__).resolve().parent.parent / 'emojis'
EMOJI_BASE_URL = 'https://enka.network/ui/'
MAX_EMOJI_BYTES = 256 * 1024
EMOJI_FILES = {
    'stygian_easy': 'UI_LeyLineChallenge_Medal_1.png',
    'stygian_normal': 'UI_LeyLineChallenge_Medal_2.png',
    'stygian_hard': 'UI_LeyLineChallenge_Medal_3.png',
    'stygian_master': 'UI_LeyLineChallenge_Medal_4.png',
    'stygian_extra': 'UI_LeyLineChallenge_Medal_5.png',
    'stygian_ultimate': 'UI_LeyLineChallenge_Medal_6.png',
}

_application_emojis: dict[str, discord.Emoji] = {}


def get_application_emoji(name: str) -> str:
    """登録済みApplication EmojiをDiscordのメッセージ表記で返す。"""
    emoji = _application_emojis.get(name)
    return str(emoji) if emoji is not None else ''


async def load_emoji_image(session: aiohttp.ClientSession, filename: str) -> bytes | None:
    path = EMOJI_DIRECTORY / filename
    if path.is_file():
        try:
            return path.read_bytes()
        except OSError:
            logger.exception('Application Emoji素材の読み込みに失敗しました: %s', path)

    url = f'{EMOJI_BASE_URL}{filename}'
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            image = await response.read()
    except (aiohttp.ClientError, TimeoutError):
        logger.exception('Application Emoji素材の取得に失敗しました: %s', url)
        return None

    if not image.startswith(b'\x89PNG\r\n\x1a\n') or len(image) > MAX_EMOJI_BYTES:
        logger.error('Application Emoji素材の形式またはサイズが不正です: %s', url)
        return None

    try:
        EMOJI_DIRECTORY.mkdir(parents=True, exist_ok=True)
        path.write_bytes(image)
    except OSError:
        logger.warning('Application Emoji素材を保存できませんでした: %s', path, exc_info=True)

    return image


async def sync_application_emojis(client: discord.Client) -> None:
    """起動時にApplication Emojiを取得し、不足している素材だけ登録する。"""
    try:
        existing = {
            emoji.name: emoji
            for emoji in await client.fetch_application_emojis()
        }
    except discord.HTTPException:
        logger.exception('Application Emojiの取得に失敗しました')
        return

    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for name, filename in EMOJI_FILES.items():
            if name in existing:
                continue

            image = await load_emoji_image(session, filename)
            if image is None:
                continue

            try:
                emoji = await client.create_application_emoji(name=name, image=image)
            except discord.HTTPException:
                logger.exception('Application Emoji %s の登録に失敗しました', name)
                continue

            existing[name] = emoji
            logger.info('Application Emoji %s を登録しました', name)

    _application_emojis.clear()
    _application_emojis.update(existing)
