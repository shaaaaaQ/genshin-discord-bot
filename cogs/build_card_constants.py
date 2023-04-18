calc_types = [
    {
        'rates': [
            {'type': 'FIGHT_PROP_CRITICAL', 'rate': 2},
            {'type': 'FIGHT_PROP_CRITICAL_HURT', 'rate': 1}
        ],
        'label': '会心のみ',
        # TODO 理論値が違うからここの数値を変えるか、ほかのサイトとかBotと合わせたい
        'point_refer': {
            'Total': {
                'SS': 220,
                'S': 200,
                'A': 180
            },
            'EQUIP_BRACER': {
                'SS': 50,
                'S': 45,
                'A': 40
            },
            'EQUIP_NECKLACE': {
                'SS': 50,
                'S': 45,
                'A': 40
            },
            'EQUIP_SHOES': {
                'SS': 45,
                'S': 40,
                'A': 35
            },
            'EQUIP_RING': {
                'SS': 45,
                'S': 40,
                'A': 37
            },
            'EQUIP_DRESS': {
                'SS': 40,
                'S': 35,
                'A': 30
            }
        }
    },
    {
        'rates': [
            {'type': 'FIGHT_PROP_CRITICAL', 'rate': 2},
            {'type': 'FIGHT_PROP_CRITICAL_HURT', 'rate': 1},
            {'type': 'FIGHT_PROP_ATTACK_PERCENT', 'rate': 1}
        ],
        'label': '攻撃換算',
        'point_refer': {
            'Total': {
                'SS': 220,
                'S': 200,
                'A': 180
            },
            'EQUIP_BRACER': {
                'SS': 50,
                'S': 45,
                'A': 40
            },
            'EQUIP_NECKLACE': {
                'SS': 50,
                'S': 45,
                'A': 40
            },
            'EQUIP_SHOES': {
                'SS': 45,
                'S': 40,
                'A': 35
            },
            'EQUIP_RING': {
                'SS': 45,
                'S': 40,
                'A': 37
            },
            'EQUIP_DRESS': {
                'SS': 40,
                'S': 35,
                'A': 30
            }
        }
    },
    {
        'rates': [
            {'type': 'FIGHT_PROP_CRITICAL', 'rate': 2},
            {'type': 'FIGHT_PROP_CRITICAL_HURT', 'rate': 1},
            {'type': 'FIGHT_PROP_HP_PERCENT', 'rate': 1}
        ],
        'label': 'HP換算',
        'point_refer': {
            'Total': {
                'SS': 220,
                'S': 200,
                'A': 180
            },
            'EQUIP_BRACER': {
                'SS': 50,
                'S': 45,
                'A': 40
            },
            'EQUIP_NECKLACE': {
                'SS': 50,
                'S': 45,
                'A': 40
            },
            'EQUIP_SHOES': {
                'SS': 45,
                'S': 40,
                'A': 35
            },
            'EQUIP_RING': {
                'SS': 45,
                'S': 40,
                'A': 37
            },
            'EQUIP_DRESS': {
                'SS': 40,
                'S': 35,
                'A': 30
            }
        }
    },
    {
        'rates': [
            {'type': 'FIGHT_PROP_CRITICAL', 'rate': 2},
            {'type': 'FIGHT_PROP_CRITICAL_HURT', 'rate': 1},
            {'type': 'FIGHT_PROP_DEFENSE_PERCENT', 'rate': 1}
        ],
        'label': '防御換算',
        # TODO
        'point_refer': {
            'Total': {
                'SS': 220,
                'S': 200,
                'A': 180
            },
            'EQUIP_BRACER': {
                'SS': 50,
                'S': 45,
                'A': 40
            },
            'EQUIP_NECKLACE': {
                'SS': 50,
                'S': 45,
                'A': 40
            },
            'EQUIP_SHOES': {
                'SS': 45,
                'S': 40,
                'A': 35
            },
            'EQUIP_RING': {
                'SS': 45,
                'S': 40,
                'A': 37
            },
            'EQUIP_DRESS': {
                'SS': 40,
                'S': 35,
                'A': 30
            }
        }
    },
    {
        'rates': [
            {'type': 'FIGHT_PROP_CRITICAL', 'rate': 2},
            {'type': 'FIGHT_PROP_CRITICAL_HURT', 'rate': 1},
            {'type': 'FIGHT_PROP_ELEMENT_MASTERY', 'rate': 0.25}
        ],
        'label': '会心+熟知換算',
        # TODO
        'point_refer': {
            'Total': {
                'SS': 220,
                'S': 200,
                'A': 180
            },
            'EQUIP_BRACER': {
                'SS': 50,
                'S': 45,
                'A': 40
            },
            'EQUIP_NECKLACE': {
                'SS': 50,
                'S': 45,
                'A': 40
            },
            'EQUIP_SHOES': {
                'SS': 45,
                'S': 40,
                'A': 35
            },
            'EQUIP_RING': {
                'SS': 45,
                'S': 40,
                'A': 37
            },
            'EQUIP_DRESS': {
                'SS': 40,
                'S': 35,
                'A': 30
            }
        }
    },
    {
        'rates': [
            {'type': 'FIGHT_PROP_CRITICAL', 'rate': 2},
            {'type': 'FIGHT_PROP_CRITICAL_HURT', 'rate': 1},
            {'type': 'FIGHT_PROP_CHARGE_EFFICIENCY', 'rate': 1}
        ],
        'label': '元チャ換算',
        # TODO
        'point_refer': {
            'Total': {
                'SS': 220,
                'S': 200,
                'A': 180
            },
            'EQUIP_BRACER': {
                'SS': 50,
                'S': 45,
                'A': 40
            },
            'EQUIP_NECKLACE': {
                'SS': 50,
                'S': 45,
                'A': 40
            },
            'EQUIP_SHOES': {
                'SS': 45,
                'S': 40,
                'A': 35
            },
            'EQUIP_RING': {
                'SS': 45,
                'S': 40,
                'A': 37
            },
            'EQUIP_DRESS': {
                'SS': 40,
                'S': 35,
                'A': 30
            }
        }
    }
]

prop_id_ja = {
    'FIGHT_PROP_HP': 'HP',
    'FIGHT_PROP_ATTACK': '攻撃実数',
    'FIGHT_PROP_DEFENSE': '防御実数',
    'FIGHT_PROP_HP_PERCENT': 'HP%',
    'FIGHT_PROP_ATTACK_PERCENT': '攻撃%',
    'FIGHT_PROP_DEFENSE_PERCENT': '防御%',
    'FIGHT_PROP_CRITICAL': '会心率',
    'FIGHT_PROP_CRITICAL_HURT': '会心ダメージ',
    'FIGHT_PROP_CHARGE_EFFICIENCY': '元素チャージ効率',
    'FIGHT_PROP_ELEMENT_MASTERY': '元素熟知'
}
