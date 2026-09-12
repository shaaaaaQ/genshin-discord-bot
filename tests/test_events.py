import unittest

from services.events import create_events_embed, parse_events


class EventsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.response = {
            'events': [
                {
                    'id': 426,
                    'name': 'テストイベント',
                    'description': 'イベントの説明です。',
                    'image_url': 'https://example.com/event.png',
                    'start_time': 1_000,
                    'end_time': 2_000,
                    'rewards': [
                        {'name': 'モラ', 'amount': 10000, 'icon': None},
                        {'name': '経験値素材', 'amount': 0, 'icon': None},
                    ],
                    'special_reward': {
                        'name': '原石',
                        'amount': 420,
                        'icon': 'https://example.com/primogem.png',
                    },
                }
            ]
        }

    def test_parse_events(self) -> None:
        events = parse_events(self.response)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].name, 'テストイベント')
        self.assertEqual(events[0].special_reward.name, '原石')
        self.assertEqual(events[0].rewards[0].amount, 10000)

    def test_create_current_event_embed(self) -> None:
        embed = create_events_embed(parse_events(self.response))

        self.assertEqual(embed.title, 'イベント情報')
        self.assertEqual(embed.fields[0].name, 'テストイベント')
        self.assertIn('<t:1000:d> ～ <t:2000:d>', embed.fields[0].value)
        self.assertNotIn('イベントの説明です。', embed.fields[0].value)
        self.assertIn('主な報酬：原石 ×420 / モラ ×10000', embed.fields[0].value)
        self.assertNotIn('経験値素材', embed.fields[0].value)

    def test_event_without_period_is_hidden(self) -> None:
        self.response['events'][0]['start_time'] = 0
        self.response['events'][0]['end_time'] = 0

        embed = create_events_embed(parse_events(self.response))

        self.assertEqual(len(embed.fields), 0)
        self.assertIn('ありません', embed.description)

    def test_empty_event_list(self) -> None:
        embed = create_events_embed(parse_events({'events': []}))

        self.assertIn('ありません', embed.description)

    def test_multiple_events_share_one_embed(self) -> None:
        second = dict(self.response['events'][0])
        second['name'] = '次のイベント'
        self.response['events'].append(second)

        embed = create_events_embed(parse_events(self.response))

        self.assertEqual(len(embed.fields), 2)

    def test_invalid_response_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_events({'banners': []})


if __name__ == '__main__':
    unittest.main()
