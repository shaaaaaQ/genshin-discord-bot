import logging
from dataclasses import dataclass
from pathlib import Path

import aiohttp
import discord


logger = logging.getLogger(__name__)
EMOJI_DIRECTORY = Path(__file__).resolve().parent.parent / 'emojis'
EMOJI_CACHE_DIRECTORY = EMOJI_DIRECTORY / '.cache'
MAX_EMOJI_BYTES = 256 * 1024


@dataclass(frozen=True)
class EmojiAsset:
    filename: str
    url: str | None = None


EMOJI_ASSETS = {
    f'stygian_{name}': EmojiAsset(
        filename=f'UI_LeyLineChallenge_Medal_{index}.png',
        url=f'https://enka.network/ui/UI_LeyLineChallenge_Medal_{index}.png',
    )
    for index, name in enumerate(
        ('easy', 'normal', 'hard', 'master', 'extra', 'ultimate'), start=1
    )
}

_application_emojis: dict[str, discord.Emoji] = {}


def get_application_emoji(name: str) -> str:
    """登録済みApplication EmojiをDiscordのメッセージ表記で返す。"""
    emoji = _application_emojis.get(name)
    return str(emoji) if emoji is not None else ''


async def load_emoji_image(
    session: aiohttp.ClientSession,
    asset: EmojiAsset,
) -> bytes | None:
    local_path = EMOJI_DIRECTORY / asset.filename
    if local_path.is_file():
        try:
            return local_path.read_bytes()
        except OSError:
            logger.exception('Application Emoji素材の読み込みに失敗しました: %s', local_path)

    if asset.url is None:
        logger.warning('Application Emoji素材がありません: %s', local_path)
        return None

    cache_path = EMOJI_CACHE_DIRECTORY / asset.filename
    if cache_path.is_file():
        try:
            return cache_path.read_bytes()
        except OSError:
            logger.exception('Application Emojiキャッシュの読み込みに失敗しました: %s', cache_path)

    try:
        async with session.get(asset.url) as response:
            response.raise_for_status()
            image = await response.read()
    except (aiohttp.ClientError, TimeoutError):
        logger.exception('Application Emoji素材の取得に失敗しました: %s', asset.url)
        return None

    if not image.startswith(b'\x89PNG\r\n\x1a\n') or len(image) > MAX_EMOJI_BYTES:
        logger.error('Application Emoji素材の形式またはサイズが不正です: %s', asset.url)
        return None

    try:
        EMOJI_CACHE_DIRECTORY.mkdir(parents=True, exist_ok=True)
        cache_path.write_bytes(image)
    except OSError:
        logger.warning(
            'Application Emoji素材を保存できませんでした: %s', cache_path, exc_info=True
        )

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
        for name, asset in EMOJI_ASSETS.items():
            if name in existing:
                continue

            image = await load_emoji_image(session, asset)
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
