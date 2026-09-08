import enka


async def fetch_profile(uid: str) -> enka.gi.ShowcaseResponse:
    async with enka.GenshinClient(enka.gi.Language.JAPANESE) as client:
        return await client.fetch_showcase(uid)
