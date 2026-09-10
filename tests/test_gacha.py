import unittest
from unittest.mock import patch

from services.gacha import create_gacha_embeds, parse_gacha_banners


class GachaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.response = {
            'events': [],
            'banners': [
                {
                    'id': 1,
                    'name': 'キャラクター祈願',
                    'version': '7.0',
                    'characters': [
                        {
                            'id': 1001,
                            'name': '五星キャラ',
                            'icon': 'https://example.com/character.png',
                            'element': 'Electro',
                            'rarity': 5,
                        },
                        {
                            'id': 1002,
                            'name': '四星キャラ',
                            'icon': 'https://example.com/character-4.png',
                            'element': 'Hydro',
                            'rarity': 4,
                        },
                    ],
                    'weapons': [],
                    'start_time': 1_000,
                    'end_time': 2_000,
                }
            ],
            'challenges': [],
        }

    def test_parse_gacha_banners(self) -> None:
        banners = parse_gacha_banners(self.response)

        self.assertEqual(len(banners), 1)
        self.assertEqual(banners[0].name, 'キャラクター祈願')
        self.assertEqual(banners[0].version, '7.0')
        self.assertEqual(banners[0].characters[0].name, '五星キャラ')
        self.assertEqual(banners[0].characters[0].rarity, 5)
        self.assertEqual(banners[0].start_time, 1_000)

    def test_create_gacha_embed(self) -> None:
        embed = create_gacha_embeds(
            parse_gacha_banners(self.response), now=1_500
        )[0]

        self.assertEqual(embed.title, 'ガチャ情報｜Ver.7.0')
        self.assertIn('**開催中**', embed.description)
        self.assertIn('<t:1000:F>', embed.description)
        self.assertIn('<t:2000:R>', embed.description)
        self.assertEqual(embed.fields[0].name, 'キャラクター祈願 — 五星キャラ')
        self.assertIn('🟨 [雷] 五星キャラ', embed.fields[0].value)
        self.assertIn('🟪 [水] 四星キャラ', embed.fields[0].value)
        self.assertEqual(embed.thumbnail.url, 'https://example.com/character.png')

    @patch(
        'services.gacha.service.get_application_emoji',
        return_value='<:element_electro:2>',
    )
    def test_element_application_emoji_is_displayed(self, _emoji) -> None:
        self.response['banners'][0]['characters'] = [
            self.response['banners'][0]['characters'][0]
        ]

        embed = create_gacha_embeds(parse_gacha_banners(self.response))[0]

        self.assertIn(
            '🟨 <:element_electro:2> 五星キャラ',
            embed.fields[0].value,
        )

    def test_zero_timestamp_is_treated_as_unknown(self) -> None:
        self.response['banners'][0]['start_time'] = 0
        self.response['banners'][0]['end_time'] = 0

        embed = create_gacha_embeds(parse_gacha_banners(self.response))[0]

        self.assertIn('期間情報なし', embed.description)

    def test_weapon_banner_is_displayed(self) -> None:
        banner = self.response['banners'][0]
        banner['characters'] = []
        banner['weapons'] = [
            {
                'id': 2001,
                'name': '五星武器',
                'icon': 'https://example.com/weapon.png',
                'rarity': 5,
            }
        ]

        embed = create_gacha_embeds(parse_gacha_banners(self.response))[0]

        self.assertEqual(embed.fields[0].name, 'キャラクター祈願 — 五星武器')
        self.assertEqual(embed.fields[0].value, '🟨 五星武器')
        self.assertEqual(embed.thumbnail.url, 'https://example.com/weapon.png')

    def test_multiple_banners_share_one_embed(self) -> None:
        second = dict(self.response['banners'][0])
        second['name'] = '武器祈願'
        second['characters'] = []
        second['weapons'] = [
            {'name': '五星武器', 'rarity': 5, 'icon': None}
        ]
        self.response['banners'].append(second)

        embeds = create_gacha_embeds(parse_gacha_banners(self.response))

        self.assertEqual(len(embeds), 1)
        self.assertEqual(len(embeds[0].fields), 2)

    def test_empty_banner_list(self) -> None:
        embed = create_gacha_embeds(parse_gacha_banners({'banners': []}))[0]

        self.assertEqual(embed.title, 'ガチャ情報')
        self.assertIn('ありません', embed.description)

    def test_invalid_response_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_gacha_banners({'events': []})


if __name__ == '__main__':
    unittest.main()
