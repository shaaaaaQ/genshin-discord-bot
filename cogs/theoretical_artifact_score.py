from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP


class TheoreticalArtifactScore:
    theoretical_value = {
        'fixed_hp': 298.75,
        'fixed_atk': 19.45,
        'fixed_def': 23.15,
        'rated_hp': 5.83,
        'rated_atk': 5.83,
        'rated_def': 7.29,
        'crit_dmg': 7.77,
        'crit_rate': 3.89,
        'charge_rate': 6.48,
        'elemental_mastery': 23.31,
    }

    round_rank = {
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

    def _quantize(self, value: float, rank: str='0.1', method:str = ROUND_DOWN) -> Decimal:
        return Decimal(value).quantize(Decimal(rank), method)

    def _calc_theoretical_rate(
        self, attr: str, initial: int = 1, raises: int = 5
    ) -> float:
        """
        オプション上昇理論値から見た割合を算出する

        現在値 / 1回の上昇量の理論値 * (オプション初期値として扱う値 + オプション上昇回数)
        """
        # 誤差を小さくするため、ゲーム表示上の値を算出する
        denominator = float(self._quantize(
            self.theoretical_value[attr] * (initial + raises),
            self.round_rank[attr],
            ROUND_HALF_UP,
        ))
        result = getattr(self, attr) / denominator
        # print(f'{attr}: {getattr(self, attr)} / {denominator} = {result}')
        return result

    def calc_theoretical_rate(
        self, attrs: 'list[str] | None' = None, raises: int = 5
    ) -> Decimal:
        """
        選択したオプションと、上昇回数から想定される理論値から見た割合を算出する
        """
        if attrs is None:
            attrs = [
                attr for attr in self.theoretical_value.keys() if getattr(self, attr)
            ]
        rates: list[float] = [
            self._calc_theoretical_rate(attr, initial=len(attrs), raises=raises)
            for attr in attrs
        ]
        return self._quantize(sum(rates) * 100)


if __name__ == '__main__':
    # 理論上最弱聖遺物
    tas = TheoreticalArtifactScore(
        fixed_hp=1046,
        rated_hp=4.1,
        crit_rate=2.7,
        crit_dmg=5.4,
    )
    # 会心率オプションとしての理論値から見た割合: 11.5
    print(tas.calc_theoretical_rate(['crit_rate']))
    # hp固定値が5回伸びた際の理論値から見た割合: 58.3
    print(tas.calc_theoretical_rate(['fixed_hp'], 5))
    # hp固定値を除いた聖遺物としての理論値から見た割合: 26.1
    print(tas.calc_theoretical_rate(['crit_rate', 'crit_dmg', 'rated_hp']))
    # 聖遺物としての理論値スコア: 62.1
    print(tas.calc_theoretical_rate())

    # 理論上最強聖遺物
    tas = TheoreticalArtifactScore(
        rated_atk=5.8,
        crit_dmg=38.9,
        crit_rate=7.8,
        fixed_def=23,
    )
    # 率ダメ理論値スコア: 100.0
    print(tas.calc_theoretical_rate(['crit_rate', 'crit_dmg', 'rated_atk']))
    # トータルスコア: 100.0
    print(tas.calc_theoretical_rate())
    # 一般的な聖遺物スコアが理論値の 60.3であることの確認
    assert tas.calc_general_rate('rated_atk') == Decimal('60.3')
    
    # 理論値で100.0になることを確認する
    theoretical_values=dict(
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
    tas = TheoreticalArtifactScore(
        **theoretical_values
    )
    # 各値ごとに確認
    for k in tas.theoretical_value.keys():
        assert tas.calc_theoretical_rate([k])== Decimal('100.0')
