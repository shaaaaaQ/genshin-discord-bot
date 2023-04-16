"""
(async () => {
    const res = await fetch("https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/loc.json")
    const loc = await res.json()
    const code = {
        en: "eng",
        ru: "rus",
        vi: "vie",
        th: "tha",
        pt: "por",
        ko: "kor",
        ja: "jpn",
        id: "ind",
        fr: "fra",
        es: "spa",
        de: "deu",
        "zh-TW": "chi_tra",
        "zh-CN": "chi_sim",
        it: "ita",
        tr: "tur"
    }
    let str = ""
    Object.keys(loc).forEach(lang => {
        str += `"${lang}": {
    "code": "${code[lang]}",
    "crit_rate": "${loc[lang]["FIGHT_PROP_CRITICAL"]}",
    "crit_dmg": "${loc[lang]["FIGHT_PROP_CRITICAL_HURT"]}",
    "fixed_atk": "${loc[lang]["FIGHT_PROP_ATTACK"]}",
    "fixed_hp": "${loc[lang]["FIGHT_PROP_HP"]}",
    "fixed_def": "${loc[lang]["FIGHT_PROP_DEFENSE"]}",
    "rated_atk": "${loc[lang]["FIGHT_PROP_ATTACK_PERCENT"]}",
    "rated_hp": "${loc[lang]["FIGHT_PROP_HP_PERCENT"]}",
    "rated_def": "${loc[lang]["FIGHT_PROP_DEFENSE_PERCENT"]}",
    "charge_rate": "${loc[lang]["FIGHT_PROP_CHARGE_EFFICIENCY"]}",
    "elemental_mastery": "${loc[lang]["FIGHT_PROP_ELEMENT_MASTERY"]}"
},\n`
    })
    console.log(str)
})()
"""

locales = {
    "en": {
        "code": "eng",
        "crit_rate": "CRIT Rate",
        "crit_dmg": "CRIT DMG",
        "fixed_atk": "ATK",
        "fixed_hp": "HP",
        "fixed_def": "DEF",
        "rated_atk": "ATK",
        "rated_hp": "HP",
        "rated_def": "DEF",
        "charge_rate": "Energy Recharge",
        "elemental_mastery": "Elemental Mastery"
    },
    "ru": {
        "code": "rus",
        "crit_rate": "Шанс крит. попадания",
        "crit_dmg": "Крит. урон",
        "fixed_atk": "Сила атаки",
        "fixed_hp": "HP",
        "fixed_def": "Защита",
        "rated_atk": "Сила атаки",
        "rated_hp": "HP",
        "rated_def": "Защита",
        "charge_rate": "Восст. энергии",
        "elemental_mastery": "Мастерство стихий"
    },
    "vi": {
        "code": "vie",
        "crit_rate": "Tỷ Lệ Bạo Kích",
        "crit_dmg": "ST Bạo Kích",
        "fixed_atk": "Tấn Công",
        "fixed_hp": "HP",
        "fixed_def": "Phòng Ngự",
        "rated_atk": "Tấn Công",
        "rated_hp": "HP",
        "rated_def": "Phòng Ngự",
        "charge_rate": "Hiệu Quả Nạp Nguyên Tố",
        "elemental_mastery": "Tinh Thông Nguyên Tố"
    },
    "th": {
        "code": "tha",
        "crit_rate": "อัตราคริ",
        "crit_dmg": "ความแรงคริ",
        "fixed_atk": "พลังโจมตี",
        "fixed_hp": "พลังชีวิต",
        "fixed_def": "พลังป้องกัน",
        "rated_atk": "พลังโจมตี",
        "rated_hp": "พลังชีวิต",
        "rated_def": "พลังป้องกัน",
        "charge_rate": "การฟื้นฟูพลังงาน",
        "elemental_mastery": "ความชำนาญธาตุ"
    },
    "pt": {
        "code": "por",
        "crit_rate": "Taxa Crítica",
        "crit_dmg": "Dano Crítico",
        "fixed_atk": "ATQ",
        "fixed_hp": "Vida",
        "fixed_def": "DEF",
        "rated_atk": "ATQ",
        "rated_hp": "Vida",
        "rated_def": "DEF",
        "charge_rate": "Recarga de Energia",
        "elemental_mastery": "Proficiência Elemental"
    },
    "ko": {
        "code": "kor",
        "crit_rate": "치명타 확률",
        "crit_dmg": "치명타 피해",
        "fixed_atk": "공격력",
        "fixed_hp": "HP",
        "fixed_def": "방어력",
        "rated_atk": "공격력",
        "rated_hp": "HP",
        "rated_def": "방어력",
        "charge_rate": "원소 충전 효율",
        "elemental_mastery": "원소 마스터리"
    },
    "ja": {
        "code": "jpn",
        "crit_rate": "会心率",
        "crit_dmg": "会心ダメージ",
        "fixed_atk": "攻撃力",
        "fixed_hp": "HP",
        "fixed_def": "防御力",
        "rated_atk": "攻撃力",
        "rated_hp": "HP",
        "rated_def": "防御力",
        "charge_rate": "元素チャージ効率",
        "elemental_mastery": "元素熟知"
    },
    "id": {
        "code": "ind",
        "crit_rate": "CRIT Rate",
        "crit_dmg": "CRIT DMG",
        "fixed_atk": "ATK",
        "fixed_hp": "HP",
        "fixed_def": "DEF",
        "rated_atk": "ATK",
        "rated_hp": "HP",
        "rated_def": "DEF",
        "charge_rate": "Energy Recharge",
        "elemental_mastery": "Elemental Mastery"
    },
    "fr": {
        "code": "fra",
        "crit_rate": "Taux CRIT",
        "crit_dmg": "DGT CRIT",
        "fixed_atk": "ATQ",
        "fixed_hp": "PV",
        "fixed_def": "DÉF",
        "rated_atk": "ATQ",
        "rated_hp": "PV",
        "rated_def": "DÉF",
        "charge_rate": "Recharge d'énergie",
        "elemental_mastery": "Maîtrise élémentaire"
    },
    "es": {
        "code": "spa",
        "crit_rate": "Prob. CRIT",
        "crit_dmg": "Daño CRIT",
        "fixed_atk": "ATQ",
        "fixed_hp": "Vida",
        "fixed_def": "DEF",
        "rated_atk": "ATQ",
        "rated_hp": "Vida",
        "rated_def": "DEF",
        "charge_rate": "Recarga de Energía",
        "elemental_mastery": "Maestría Elemental"
    },
    "de": {
        "code": "deu",
        "crit_rate": "KT",
        "crit_dmg": "KSCH",
        "fixed_atk": "ANG",
        "fixed_hp": "LP",
        "fixed_def": "VTD",
        "rated_atk": "ANG",
        "rated_hp": "LP",
        "rated_def": "VTD",
        "charge_rate": "Aufladerate",
        "elemental_mastery": "Elementarkunde"
    },
    "zh-TW": {
        "code": "chi_tra",
        "crit_rate": "暴擊率",
        "crit_dmg": "暴擊傷害",
        "fixed_atk": "攻擊力",
        "fixed_hp": "生命值",
        "fixed_def": "防禦力",
        "rated_atk": "攻擊力",
        "rated_hp": "生命值",
        "rated_def": "防禦力",
        "charge_rate": "元素充能效率",
        "elemental_mastery": "元素精通"
    },
    "zh-CN": {
        "code": "chi_sim",
        "crit_rate": "暴击率",
        "crit_dmg": "暴击伤害",
        "fixed_atk": "攻击力",
        "fixed_hp": "生命值",
        "fixed_def": "防御力",
        "rated_atk": "攻击力",
        "rated_hp": "生命值",
        "rated_def": "防御力",
        "charge_rate": "元素充能效率",
        "elemental_mastery": "元素精通"
    },
    "it": {
        "code": "ita",
        "crit_rate": "Tasso di CRIT",
        "crit_dmg": "DAN da CRIT",
        "fixed_atk": "ATT",
        "fixed_hp": "PS",
        "fixed_def": "DIF",
        "rated_atk": "ATT",
        "rated_hp": "PS",
        "rated_def": "DIF",
        "charge_rate": "Ricarica di energia",
        "elemental_mastery": "Maestria elementale"
    },
    "tr": {
        "code": "tur",
        "crit_rate": "Kritik Oranı",
        "crit_dmg": "Kritik Hasar",
        "fixed_atk": "Saldırı",
        "fixed_hp": "Can",
        "fixed_def": "Savunma",
        "rated_atk": "Saldırı",
        "rated_hp": "Can",
        "rated_def": "Savunma",
        "charge_rate": "Enerji Yüklemesi",
        "elemental_mastery": "Element Ustalığı"
    },
}
