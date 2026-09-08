import itertools
import statistics
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal
from typing import Literal

AttrKeys = Literal[
    'fixed_hp',
    'fixed_atk',
    'fixed_def',
    'rated_hp',
    'rated_atk',
    'rated_def',
    'crit_dmg',
    'crit_rate',
    'charge_rate',
    'elemental_mastery',
]

class ArtifactConstants:
    INCREASE_TABLE: dict[AttrKeys, list[float]] = {
        'fixed_hp': [209.13, 239.00, 268.88, 298.75],
        'fixed_atk': [13.62, 15.56, 17.51, 19.45],
        'fixed_def': [16.20, 18.52, 20.83, 23.15],
        'rated_hp': [4.08, 4.66, 5.25, 5.83],
        'rated_atk': [4.08, 4.66, 5.25, 5.83],
        'rated_def': [5.10, 5.83, 6.56, 7.29],
        'crit_dmg': [5.44, 6.22, 6.99, 7.77],
        'crit_rate': [2.72, 3.11, 3.50, 3.89],
        'charge_rate': [4.53, 5.18, 5.83, 6.48],
        'elemental_mastery': [16.32, 18.65, 20.98, 23.31],
    }

    ROUND_RANK: dict[AttrKeys, str] = {
        'fixed_hp': '1',
        'fixed_atk': '1',
        'fixed_def': '1',
        'rated_hp': '0.1',
        'rated_atk': '0.1',
        'rated_def': '0.1',
        'crit_dmg': '0.1',
        'crit_rate': '0.1',
        'charge_rate': '0.1',
        'elemental_mastery': '1',
    }

    def __init__(self):
        pass

    @staticmethod
    def quantize(value: float, rank: str = '0.1', method: str = ROUND_DOWN) -> Decimal:
        return Decimal(value).quantize(Decimal(rank), method)

    @staticmethod
    def _calc_display_to_internal(attr: AttrKeys):
        """キー毎に、表示値から、内部値を算出する"""
        indexes: list[tuple[int]] = []
        # 上昇値のインデックスである 0 - 3 の配列から、 重複を含みかつ並べ替えて一致しない i 個のペアを生成する
        increase_index = range(4)
        for i in range(7):
            indexes.extend(
                itertools.combinations_with_replacement(increase_index, i)
            )

        # 内部値の配列に持ち替える
        display_to_internal_values: dict[float, list[float]] = {}
        for x in indexes:
            disp = float(ArtifactConstants.quantize(
                sum([ArtifactConstants.INCREASE_TABLE[attr][i] for i in x]),
                ArtifactConstants.ROUND_RANK[attr],
                ROUND_HALF_UP,
            ))
            internal = sum(
                [ArtifactConstants.INCREASE_TABLE[attr][i] for i in x]
            )

            if disp in display_to_internal_values:
                display_to_internal_values[disp].append(internal)
            else:
                display_to_internal_values[disp] = [internal]

        # 内部値の配列も、INCREASE_TABLEの誤差で多少揺れているので中央値で算出し直し、四捨五入する
        result = {
            k: float(ArtifactConstants.quantize(
                statistics.median(v) if v else 0,
                '0.01',
                ROUND_HALF_UP,
            ))
            for k, v in display_to_internal_values.items()
        }
        return result

    @staticmethod
    def calc_display_to_internal():
        """表示値から、内部値を算出し、辞書に整形する

        :example:
        ```
        >>> ArtifactConstants.calc_display_to_internal()
        {
            'fixed_hp': {0.0: 0.0, 209.0: 209.13, 239.0: 239.0, 269.0: 268.88, 299.0: 298.75, ...},
            'fixed_atk':  {0.0: 0.0, 14.0: 13.62, 16.0: 15.56, 18.0: 17.51, 19.0: 19.45, ...},
            ...
        }
        ```
        """
        result: dict[AttrKeys, dict[float, float]] = {}
        for k in ArtifactConstants.ROUND_RANK.keys():
            result[k] = ArtifactConstants._calc_display_to_internal(k)
        return result
