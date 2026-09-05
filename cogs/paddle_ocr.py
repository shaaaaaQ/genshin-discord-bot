from threading import Lock

import numpy as np
from paddleocr import PaddleOCR
from PIL import Image


class PaddleOCRReader:
    """PaddleOCRの認識結果を文字列の配列に変換する。"""

    def __init__(self, lang: str) -> None:
        self.lang = lang
        self._ocr: PaddleOCR | None = None
        self._lock = Lock()

    def _get_ocr(self) -> PaddleOCR:
        if self._ocr is None:
            # PP-OCRv6非対応の文字系はPP-OCRv5を使用する。
            ocr_version = (
                'PP-OCRv5'
                if self.lang in {'korean', 'ru', 'th'}
                else 'PP-OCRv6'
            )
            self._ocr = PaddleOCR(
                lang=self.lang,
                ocr_version=ocr_version,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                engine='paddle',
            )
        return self._ocr

    def read_lines(self, image: Image.Image) -> list[str]:
        # 同じ推論器をDiscordコマンドから並列利用しない。
        with self._lock:
            results = self._get_ocr().predict(
                np.asarray(image.convert('RGB')),
            )

        lines: list[str] = []
        for result in results:
            data = result.json
            payload = data.get('res', data)
            lines.extend(str(text) for text in payload.get('rec_texts', []))
        return lines
