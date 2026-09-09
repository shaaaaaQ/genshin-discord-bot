import tempfile
import unittest
from pathlib import Path

from services.codes.state import CodesStateStore


class CodesStateStoreTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_setting_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = CodesStateStore(Path(directory) / 'settings.sqlite3')

            self.assertIsNone(await store.get_channel_id(1))

    async def test_channel_and_active_codes_are_saved_per_guild(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = CodesStateStore(Path(directory) / 'settings.sqlite3')

            await store.set_channel(1, 10)
            await store.set_channel(2, 20)
            await store.save_active_keys(1, {'second', 'first'})

            settings = {item.guild_id: item for item in await store.get_settings()}
            self.assertEqual(settings[1].channel_id, 10)
            self.assertEqual(settings[1].active_keys, {'first', 'second'})
            self.assertEqual(settings[2].channel_id, 20)
            self.assertIsNone(settings[2].active_keys)

    async def test_changing_channel_preserves_active_codes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = CodesStateStore(Path(directory) / 'settings.sqlite3')
            await store.set_channel(1, 10)
            await store.save_active_keys(1, {'code'})

            await store.set_channel(1, 11)

            setting = (await store.get_settings())[0]
            self.assertEqual(setting.channel_id, 11)
            self.assertEqual(setting.active_keys, {'code'})

    async def test_remove_deletes_the_server_setting(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = CodesStateStore(Path(directory) / 'settings.sqlite3')
            await store.set_channel(1, 10)

            self.assertTrue(await store.remove(1))
            self.assertFalse(await store.remove(1))
            self.assertIsNone(await store.get_channel_id(1))


if __name__ == '__main__':
    unittest.main()
