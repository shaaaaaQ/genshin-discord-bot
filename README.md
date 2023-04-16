Debian(wsl1), python 3.11.1で動作確認
```bash
cd genshin-discord-bot
# tesseract-ocrをインストール
# 使いたい言語のあれ(tesseract-ocr-jpnとか)もインストールする
sudo apt install tesseract-ocr tesseract-ocr-jpn
# venv(やらなくてもいい)
python -m venv venv
source venv/bin/activate.fish
# パッケージのインストール
pip install -r requirements.txt
# 設定ファイル
vim config.py
```
config.pyの中身
```python
token = 'ここにtoken'
prefix = '-'
```

TODO
- 熟知とか防御のスコア計算
- `・`が読み取られなかった時の対策