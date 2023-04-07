Debian(wsl1), python 3.11.1で動作確認
```bash
cd genshin-discord-bot
# tesseract-ocrをインストール
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

### コマンド
[]はオプション
- `crit [LANG]`
- `atk [LANG]`
- `hp [LANG]`

### 対応言語
- ja
- en
