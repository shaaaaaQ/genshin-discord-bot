import asyncio
import logging
from decimal import Decimal
from io import BytesIO
from typing import Any, Literal

import requests
from PIL import Image

from .constants import AttrKeys
from .locales import locales
from .ocr import PaddleOCRReader
from .score import ArtifactScore, G_CalcType


logger = logging.getLogger(__name__)

CalcType = Literal['hp', 'atk', 'def', 'crit', 'em', 'er']

PADDLE_LANGS = {
    'en': 'en',
    'ru': 'ru',
    'vi': 'vi',
    'th': 'th',
    'pt': 'pt',
    'ko': 'korean',
    'ja': 'japan',
    'id': 'id',
    'fr': 'fr',
    'es': 'es',
    'de': 'de',
    'zh-TW': 'chinese_cht',
    'zh-CN': 'ch',
    'it': 'it',
    'tr': 'tr',
}

COMMAND_CALC_MAP: dict[CalcType, tuple[G_CalcType, list[AttrKeys]]] = {
    'crit': ('crit_only', ['crit_dmg', 'crit_rate']),
    'atk': ('rated_atk', ['crit_dmg', 'crit_rate', 'rated_atk']),
    'hp': ('rated_hp', ['crit_dmg', 'crit_rate', 'rated_hp']),
    'def': ('rated_def', ['crit_dmg', 'crit_rate', 'rated_def']),
    'em': ('em', ['crit_dmg', 'crit_rate', 'elemental_mastery']),
    'er': ('er', ['crit_dmg', 'crit_rate', 'charge_rate']),
}


class ArtifactProcessor:
    def __init__(self) -> None:
        self._ocr_readers: dict[str, PaddleOCRReader] = {}

    async def analyze(
        self,
        lang: str,
        image_url: str,
        calc_type: CalcType,
    ) -> tuple[dict[str, str], dict[str, Any], Decimal, Decimal]:
        translations = locales[lang]
        reader = self._ocr_readers.setdefault(
            lang,
            PaddleOCRReader(PADDLE_LANGS[lang]),
        )
        stats = await asyncio.to_thread(
            self._get_stats, translations, image_url, reader
        )
        score, rate = self._calc_score(stats, calc_type)
        return translations, stats, score, rate

    def _get_stats(
        self,
        translations: dict[str, str],
        image_url: str,
        reader: PaddleOCRReader,
    ) -> dict[str, Any]:
        response = requests.get(image_url, timeout=20)
        response.raise_for_status()
        with Image.open(BytesIO(response.content)) as image:
            ocr_lines = reader.read_lines(image)
        logger.debug('PaddleOCR result: %s', ocr_lines)
        return self._parse_stats(translations, ocr_lines)

    @staticmethod
    def _parse_stats(
        translations: dict[str, str],
        ocr_lines: list[str],
    ) -> dict[str, Any]:
        stats: dict[str, Any] = {}
        for text in ocr_lines:
            text = text.strip().lstrip('・·• ')
            text = text.replace('攻擊力', '攻撃力')
            for attr, attr_name in translations.items():
                if not text.startswith(f'{attr_name}+'):
                    continue
                if attr.startswith('fixed') and text.endswith('%'):
                    continue
                if attr.startswith('rated') and not text.endswith('%'):
                    continue
                value = float(text.split('+')[1].replace('%', '').replace(',', ''))
                stats[attr] = int(value) if attr.startswith(
                    ('fixed', 'elemental_mastery')
                ) else value
        logger.debug(stats)
        return stats

    @staticmethod
    def _calc_score(
        stats: dict[str, Any],
        calc_type: CalcType,
    ) -> tuple[Decimal, Decimal]:
        score = ArtifactScore(**stats)
        logic_name, target_attrs = COMMAND_CALC_MAP[calc_type]
        return (
            score.calc_general_rate(logic_name),
            score.calc_theoretical_rate(target_attrs),
        )
