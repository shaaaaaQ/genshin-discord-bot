## 動かし方
```bash
cd genshin-discord-bot

# venv(やらなくてもいい)
python -m venv venv
source venv/bin/activate.fish

# パッケージのインストール
pip install -r requirements.txt

# 設定ファイル
cp .env.example .env
vim .env

# 実行
python main.py
```

もしくはDocker

## TODO
bot
- レート制限
- forgetuid コマンドでuidを削除できるように

## 機能
### 交換コード一覧

[hoyoverse-api](https://github.com/torikushiii/hoyoverse-api) から、現在利用できる原神の交換コードと報酬を取得して表示します。

|コマンド|例（prefix が `-` の場合）|
|-|-|
|codes|`-codes`|

### 幻境のステージ情報
![](images/command_stage.png)

[Octavia API](https://github.com/kj415j45/octavia) から、幻境の情報を取得して表示します。

|コマンド|例（prefix が `-` の場合）|
|-|-|
|stage \<GUID> [サーバー]|`-stage 29191333005`|
|サーバーを指定|`-stage 29191333005 os_asia`|

指定可能なサーバー: `os_asia`, `os_usa`, `os_euro`, `os_cht`, `cn_gf01`, `cn_qd01`

### 画像からスコアを計算する
![](images/command_atk.png)
|コマンド||
|-|-|
|crit|会心率\*2 + 会心ダメージ|
|atk|会心率\*2 + 会心ダメージ + 攻撃力%|
|hp|会心率\*2 + 会心ダメージ + HP%|
|def|会心率\*2 + 会心ダメージ + 防御力%|
|em|会心率\*2 + 会心ダメージ + 元素熟知\*0.25|
|er|会心率\*2 + 会心ダメージ + 元素チャージ効率|

### ビルドカード作成
[enka.py](https://github.com/seriaati/enka-py) でショーケースを取得し、
[ArtifacterImageGen](https://github.com/shaaaaaQ/ArtifacterImageGen) で画像を生成
![](images/command_build.png)
|コマンド|
|-|
|build [UID]|

### プロフィール表示

|コマンド|
|-|
|profile [UID]|

`build` と `profile` で指定したUIDはDiscordユーザーごとに保存され、次回から省略できます。

## 免責事項

本プロジェクトは非公式のファンプロジェクトです。

HoYoverseおよびCOGNOSPHEREとの提携・承認・後援関係はありません。原神および関連する名称、画像、その他の素材に関する権利は、それぞれの権利者に帰属します。
