import re


REWARD_NAMES_JA = {
    "Adventurer's Experience": '冒険家の経験',
    'Agnidus Agate Sliver': '炎願のアゲート·砕屑',
    'Barbeque Ribs': 'スペアリブのロースト',
    'Beryl Conch': '蒼晶螺',
    'Blazed Meat Stew': 'ブレイズ·ミートシチュー',
    'Brilliant Chrysanthemum': 'シャクギク',
    'Broken Drive Shaft': '破損した駆動軸',
    'Bulle Sauce Duck Breast': '鴨胸肉のオレンジソースソテー',
    'Chenyu Adeptea': '沈玉仙茶',
    'Chenyu Brew': '沈玉茶',
    'Chocolate': 'チョコレート',
    'Cold Cut Platter': '冷製肉盛り合わせ',
    'Crepes Suzette': 'クレームクレープシュゼット',
    "Cup O' Grainfruit": 'グレインカップ',
    'Delicious Puff Pops': '美味しそうなドキドキポンポン',
    'Dreams of Healing': '「夢一夜の癒し」',
    'Fine Enhancement Ore': '仕上げ用良鉱',
    'Fish and Chips': 'フィッシュアンドチップス',
    'Fragile Resin': '脆弱樹脂',
    'Frostlamp Flower': 'フロストランプ',
    'Fruit Tandem Turnovers': 'ツインベリーロール',
    'Fruit-Flavored Milk Candies': 'フルーツミルクキャンディ',
    'Fruity Trio': '花と果実のトリオ',
    'Geode of Replication': '再現群晶',
    'Glowing Hornshroom': '蛍光ツノキノコ',
    'Goulash': 'お肉と野菜のシチュー',
    'Grainfruit Chips': 'グレインチップス',
    'Guide to Contention': '「角逐」の導き',
    'Guide to Kindling': '「焚燼」の導き',
    'Guide to Transience': '「浮世」の導き',
    "Hero's Wit": '大英雄の経験',
    'Honey-Glazed Ceviche': 'ハニーセビチェ',
    'Hymn of Gathered Flame': '「集いし炎の賛歌」',
    'Ideal Circumstance': '「理想的状況」',
    'Ile flottante': 'イル·フロッタント',
    'Impeccably Organized': 'きっちりチップス',
    'Jueyun Chili Chicken': '椒椒鶏',
    'Kageuchi Handguard': '影打の鍔',
    'Kalpalata Lotus': 'カルパラタ蓮',
    'Lasagna': 'ミートソースラザニア',
    'Long Night Alight': '長き夜に燃ゆる炎',
    'Masked Ball Invitation Letter': '仮面舞踏会の招待状',
    'Matsutake Meat Rolls': '松茸の肉巻き',
    'Meshing Gear': '整合の歯車',
    'Midsommar Torte': 'ソマルケーキ',
    'Moonfall Silver': '月落銀',
    'Mora': 'モラ',
    'Mystic Enhancement Ore': '仕上げ用魔鉱',
    'Nagadus Emerald Sliver': '成長のエメラルド·砕屑',
    'Nod-Krai Hot Dog': 'ナド・クライ・ホットドッグ',
    'Primogem': '原石',
    'Quenepa Berry': 'ケネパベリー',
    'Recipe: Bubblemilk Pie': 'レシピ：つぶつぶミルクパイ',
    "Recipe: Meat-Lover's Feast": 'レシピ：ミートラバーフェスタ',
    'Recipe: Nine-Fruit Nectar': 'レシピ：フルーツネクター',
    'Saurus Crackers': 'ちび竜ビスケット',
    'Sea Ganoderma': 'ウミレイシ',
    'Seasoned Fang': '熟練の牙',
    'Secret Art': '「唯一無二の秘法」',
    'Shivada Jade Fragment': '哀切なアイスクリスタル·欠片',
    'Shivada Jade Sliver': '哀切なアイスクリスタル·砕屑',
    'Sparkling Berry Juice': 'スパークリングベリージュース',
    'Stir-Fried Fish Noodles': '魚肉の焼き麺',
    "Stuffed N' Mashed Potatoes": 'カウサ',
    'Sweet Madame': '鳥肉のスイートフラワー漬け焼き',
    'Tatacos': 'タタコス',
    'Tattered Warrant': '破損した徽章',
    'Tea Break Pancake': '午後のパンケーキ',
    'Teachings of Ballad': '「詩文」の教え',
    'Teachings of Conflict': '「紛争」の教え',
    'Teachings of Contention': '「角逐」の教え',
    'Teachings of Elysium': '「楽園」の教え',
    'Teachings of Freedom': '「自由」の教え',
    'Teachings of Moonlight': '「月光」の教え',
    'Teyvat Fried Egg': 'テイワット風目玉焼き',
    'The Endeavor': '丹精込めた一作',
    'Thunderclap Slash!': '「ゴロピシャ電光斬！」',
    'Tomates Narbonnaises': 'ナルボンヌのトマトファルシ',
    'Vajrada Amethyst Sliver': '最勝のアメシスト·砕屑',
    'Varunada Lazurite Sliver': '澄明なラピスラズリ·砕屑',
    'Vayuda Turquoise Sliver': '自由のターコイズ·砕屑',
    "Warrior's Metal Whistle": '戦士の鉄笛',
    'Withering Purpurbloom': '枯れ紫菖',
    '"Abyssal Bounty"': '「暗き淵の獲物」',
}

REWARD_NAME_ALIASES = {
    'Primogems': 'Primogem',
}

_QUANTITY_FIRST_RE = re.compile(r'^(?P<quantity>\d[\d,]*)\s+(?P<name>.+)$')


def _localize_reward_name(name: str) -> str | None:
    canonical_name = REWARD_NAME_ALIASES.get(name, name)
    return REWARD_NAMES_JA.get(canonical_name)


def localize_reward(reward: str) -> str:
    quantity_first = _QUANTITY_FIRST_RE.fullmatch(reward)
    if quantity_first:
        japanese = _localize_reward_name(quantity_first.group('name'))
        if japanese is not None:
            return f"{japanese} ×{quantity_first.group('quantity')}"
        return reward

    for english in (*REWARD_NAMES_JA, *REWARD_NAME_ALIASES):
        japanese = _localize_reward_name(english)
        if japanese is None:
            continue
        if reward == english:
            return japanese
        if reward.startswith(f'{english} '):
            return japanese + reward[len(english):]
    return reward
