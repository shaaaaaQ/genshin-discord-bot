from decimal import ROUND_HALF_UP, Decimal
import logging

from .artifact_constants import ArtifactConstants

logger = logging.getLogger(__name__)


class ArtifactScore:
    INCREASE_TABLE = ArtifactConstants.INCREASE_TABLE
    ROUND_RANK = ArtifactConstants.ROUND_RANK
    DISPLAY_TO_INTERNAL = ArtifactConstants.calc_display_to_internal()

    def __init__(
        self,
        fixed_hp: int = 0,
        fixed_atk: int = 0,
        fixed_def: int = 0,
        rated_hp: float = 0.0,
        rated_atk: float = 0.0,
        rated_def: float = 0.0,
        crit_dmg: float = 0.0,
        crit_rate: float = 0.0,
        charge_rate: float = 0.0,
        elemental_mastery: int = 0,
    ):
        self.fixed_hp = fixed_hp
        self.fixed_atk = fixed_atk
        self.fixed_def = fixed_def
        self.rated_hp = rated_hp
        self.rated_atk = rated_atk
        self.rated_def = rated_def
        self.crit_dmg = crit_dmg
        self.crit_rate = crit_rate
        self.charge_rate = charge_rate
        self.elemental_mastery = elemental_mastery

    def _quantize(
        self,
        value: float,
        rank: str = '0.1',
        method: str = ROUND_HALF_UP,
    ) -> Decimal:
        return ArtifactConstants.quantize(value, rank, method)

    def _get_inner_option_value(self, attr: str, value: float) -> float:
        """表示値から内部の値を算出する"""
        result = value
        try:
            result = self.DISPLAY_TO_INTERNAL[attr][value]
        except KeyError:
            # スコアが算出できなくなると悲しいのでメッセージを記録して握り潰す
            logger.error(
                'Error occured by mapping DISPLAY_TO_INTERNAL at %s %s',
                attr,
                value,
            )

        logger.debug(
            '%s\'s internal value of %s: %s',
            attr,
            value,
            result,
        )

        return result

    def _calc_by_general_score_logic(self, calc_type: str) -> float:
        if calc_type == 'rated_hp':
            return self.crit_rate * 2 + self.crit_dmg + self.rated_hp
        if calc_type == 'rated_atk':
            return self.crit_rate * 2 + self.crit_dmg + self.rated_atk
        if calc_type == 'crit_only':
            return self.crit_rate * 2 + self.crit_dmg
        return 0

    def calc_general_rate(self, calc_type: str) -> Decimal:
        return self._quantize(
            self._calc_by_general_score_logic(calc_type),
            method=ROUND_HALF_UP,
        )

    def _calc_theoretical_rate(
        self, attr: str, initial: int = 1, raises: int = 5
    ) -> float:
        """
        オプション上昇理論値から見た割合を算出する

        現在値 / 1回の上昇量の理論値 * (オプション初期値として扱う値 + オプション上昇回数)

        誤差を小さくするため、ゲーム表示上の値ではなく、内部の値で算出する
        """
        denominator = self.INCREASE_TABLE[attr][3] * (initial + raises)
        inner_value = self._get_inner_option_value(
            attr,
            float(getattr(self, attr)),
        )

        result = inner_value / denominator

        logger.debug(f'{attr}: {inner_value} / {denominator} = {result}')
        return result

    def calc_theoretical_rate(
        self, attrs: 'list[str] | None' = None, raises: int = 5
    ) -> Decimal:
        """
        選択したオプションと、上昇回数から想定される理論値から見た割合を算出する
        """
        if attrs is None:
            attrs = [
                attr for attr in self.INCREASE_TABLE.keys() if getattr(self, attr)
            ]
        rates: list[float] = [
            self._calc_theoretical_rate(
                attr,
                initial=len(attrs),
                raises=raises,
            )
            for attr in attrs
        ]
        return self._quantize(
            min(sum(rates), 1) * 100,
            rank='0.1',
            method=ROUND_HALF_UP,
        )


if __name__ == '__main__':
    # 理論上最弱聖遺物
    tas = ArtifactScore(
        fixed_hp=1046,
        rated_hp=4.1,
        crit_rate=2.7,
        crit_dmg=5.4,
    )
    # 会心率オプションとしての理論値から見た割合: 11.7
    print(tas.calc_theoretical_rate(['crit_rate']))
    # hp固定値が5回伸びた際の理論値から見た割合: 58.3
    print(tas.calc_theoretical_rate(['fixed_hp'], 5))
    # hp固定値を除いた聖遺物としての理論値から見た割合: 26.2
    print(tas.calc_theoretical_rate(['crit_rate', 'crit_dmg', 'rated_hp']))
    # 聖遺物としての理論値スコア: 62.2
    print(tas.calc_theoretical_rate())

    # 理論上最強聖遺物
    tas = ArtifactScore(
        rated_atk=5.8,
        crit_dmg=38.9,
        crit_rate=7.8,
        fixed_def=23
    )
    # 率ダメ理論値スコア: 100.0
    print(tas.calc_theoretical_rate(['crit_rate', 'crit_dmg', 'rated_atk']))
    # トータルスコア: 100.0
    print(tas.calc_theoretical_rate())

    # 一般的な聖遺物スコアが理論値の 60.3であることの確認
    assert tas.calc_general_rate('rated_atk') == Decimal('60.3')

    # 切り捨てが多い下振れ算出される理論上最強聖遺物
    tas = ArtifactScore(
        charge_rate=19.4,  # 6.48 * 3 = 19.44
        crit_dmg=15.5,  # 7.77 * 2 = 15.54
        fixed_atk=19,  # 19.45
        fixed_def=69,  # 23.15 * 3 = 69.45
    )
    # トータルスコア: 100.0
    print(tas.calc_theoretical_rate())

    # 理論値で100.0になることを確認する
    theoretical_values = dict(
        fixed_atk=117,
        rated_atk=35.0,
        fixed_def=139,
        rated_def=43.7,
        fixed_hp=1793,
        rated_hp=35.0,
        elemental_mastery=140,
        charge_rate=38.9,
        crit_rate=23.3,
        crit_dmg=46.6,
    )
    tas = ArtifactScore(
        **theoretical_values
    )
    # 各値ごとに確認
    for k in tas.INCREASE_TABLE.keys():
        actual = tas.calc_theoretical_rate([k])
        print(f'{k}: {actual}')
        assert actual == Decimal('100')
