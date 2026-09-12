import unittest
from unittest.mock import AsyncMock

from cogs.codes import Codes
from services.codes import CodesNotificationSetting, RedemptionCode


class CodesNotificationTests(unittest.IsolatedAsyncioTestCase):
    def test_check_interval_is_fifteen_minutes(self) -> None:
        self.assertEqual(Codes.check_for_new_codes.minutes, 15)

    def make_cog(
        self,
        setting: CodesNotificationSetting,
        codes: list[RedemptionCode],
    ) -> tuple[Codes, AsyncMock, AsyncMock]:
        cog = object.__new__(Codes)
        cog.state = AsyncMock()
        cog.state.get_settings.return_value = [setting]
        cog.state.get_channel_id.return_value = setting.channel_id
        cog.client = AsyncMock()
        cog.client.fetch.return_value = codes
        channel = AsyncMock()
        cog._notification_channel = AsyncMock(return_value=channel)
        return cog, channel, cog.state

    async def test_new_codes_are_notified_and_saved(self) -> None:
        setting = CodesNotificationSetting(1, 10, {'old'})
        codes = [
            RedemptionCode('OLD', ('Mora x100',)),
            RedemptionCode('NEW', ('Primogem x60',)),
        ]
        cog, channel, state = self.make_cog(setting, codes)

        await Codes.check_for_new_codes.coro(cog)

        channel.send.assert_awaited_once()
        embed = channel.send.await_args.kwargs['embed']
        self.assertEqual(embed.title, '交換コード')
        self.assertEqual(embed.url, 'https://genshin.hoyoverse.com/ja/gift')
        self.assertEqual(embed.description, '新しい交換コードが追加されました。')
        self.assertEqual([field.name for field in embed.fields], ['NEW'])
        self.assertIn(
            'https://genshin.hoyoverse.com/ja/gift?code=NEW',
            embed.fields[0].value,
        )
        state.save_active_keys.assert_awaited_once_with(1, {'old', 'new'})

    async def test_first_check_only_saves_a_baseline(self) -> None:
        setting = CodesNotificationSetting(1, 10, None)
        codes = [RedemptionCode('CURRENT', ())]
        cog, channel, state = self.make_cog(setting, codes)

        await Codes.check_for_new_codes.coro(cog)

        channel.send.assert_not_awaited()
        state.save_active_keys.assert_awaited_once_with(1, {'current'})

    async def test_failed_notification_is_retried_later(self) -> None:
        setting = CodesNotificationSetting(1, 10, set())
        codes = [RedemptionCode('NEW', ())]
        cog, channel, state = self.make_cog(setting, codes)
        channel.send.side_effect = TypeError('send failed')

        with self.assertLogs('cogs.codes', level='ERROR'):
            await Codes.check_for_new_codes.coro(cog)

        state.save_active_keys.assert_not_awaited()


if __name__ == '__main__':
    unittest.main()
