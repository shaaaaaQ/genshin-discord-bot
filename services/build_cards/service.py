import asyncio

import enka
from artifacter_image_gen import Generator
from PIL import Image


async def fetch_characters(uid: str) -> tuple[list[enka.gi.Character], str | None]:
    async with enka.GenshinClient(enka.gi.Language.JAPANESE) as client:
        data = await client.fetch_showcase(uid)

    if data.characters:
        return data.characters, None
    if data.player.nickname:
        return [], f'キャラクターが公開されてない\n(プレイヤー名: {data.player.nickname})'
    return [], 'error'


async def generate_card(character: enka.gi.Character, calc_type: dict) -> Image.Image:
    return await asyncio.to_thread(Generator(character).generate, **calc_type)
