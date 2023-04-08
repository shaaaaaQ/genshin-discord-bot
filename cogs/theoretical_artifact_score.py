from decimal import Decimal, ROUND_HALF_UP


class TheoreticalArtifactScore:
    theoretical_value = {
        'fixed_hp': 299,
        'fixed_atk': 19,
        'fixed_def': 23,
        'rated_hp': 5.8,
        'rated_atk': 5.8,
        'rated_def': 7.3,
        'crit_dmg': 7.8,
        'crit_rate': 3.9,
        'charge_rate': 6.5,
        'elemental_mastery': 23,
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
        return self._quantize(self._calc_by_general_score_logic(calc_type))

    def _quantize(self, value: float) -> Decimal:
        return Decimal(value).quantize(Decimal('0.1'), ROUND_HALF_UP)

    def _calc_theoretical_rate(
        self, attr: str, initial: int = 1, raises: int = 5
    ) -> float:
        """
        オプション上昇理論値から見た割合を算出する

        現在値 / 1回の上昇量の理論値 * (オプション初期値として扱う値 + オプション上昇回数)
        """
        return getattr(self, attr) / (self.theoretical_value[attr] * (initial + raises))

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
    # 手持ちのそこそこ強い羽
    tas = TheoreticalArtifactScore(
        fixed_hp=209,
        rated_hp=9.9,
        crit_rate=10.1,
        crit_dmg=20.2,
    )
    # 会心率オプションとしての理論値から見た割合
    # 43.162393162393165
    print(tas.calc_theoretical_rate(['crit_rate']))

    # 会心率が2回伸びた際の理論値から見た割合
    # 86.32478632478633
    print(tas.calc_theoretical_rate(['crit_rate'], 2))

    # hp固定値を除いた聖遺物の理論値から見た割合
    # 86.07979664014147
    print(tas.calc_theoretical_rate(['crit_rate', 'crit_dmg', 'rated_hp']))

    # 聖遺物としての理論値から見た割合
    # 84.28200429699679
    print(tas.calc_theoretical_rate())

    # 適当に理論上最弱聖遺物
    tas = TheoreticalArtifactScore(
        fixed_hp=209 * 6,
        rated_hp=4.1,
        crit_rate=2.7,
        crit_dmg=5.4,
    )
    # 会心率オプションとしての理論値から見た割合
    # 11.53846153846154
    print(tas.calc_theoretical_rate(['crit_rate']))

    # hp固定値が5回伸びた際の理論値から見た割合
    # 69.89966555183946
    print(tas.calc_theoretical_rate(['fixed_hp'], 5))

    # hp固定値を除いた聖遺物としての理論値から見た割合
    # 26.143899204244036
    print(tas.calc_theoretical_rate(['crit_rate', 'crit_dmg', 'rated_hp']))

    # 聖遺物としての理論値スコア
    # 69.83879854944321
    print(tas.calc_theoretical_rate())

    # 適当に理論上最強聖遺物
    tas = TheoreticalArtifactScore(
        elemental_mastery=23,
        charge_rate=6.5,
        crit_rate=3.9 * 3,
        crit_dmg=7.8 * 4,
    )
    # 率ダメ理論値スコア
    # 100
    print(tas.calc_theoretical_rate(['crit_rate', 'crit_dmg']))
    # 理論値スコア
    # 100
    print(tas.calc_theoretical_rate())
