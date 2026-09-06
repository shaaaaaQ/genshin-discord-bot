# Application Emoji

`cogs/application_emojis.py` の `EMOJI_ASSETS` に、Application Emoji名、ローカルファイル名、取得URLの対応を定義します。

```python
EMOJI_ASSETS = {
    # リポジトリに画像を置く場合
    'custom_local': EmojiAsset(filename='custom_local.png'),

    # 任意のURLから取得する場合
    'custom_remote': EmojiAsset(
        filename='custom_remote.png',
        url='https://example.com/custom_remote.png',
    ),
}
```

起動時は、Discordに同名のApplication Emojiがあればそのまま使用します。未登録の場合はこのディレクトリ直下のローカルファイルを探し、ファイルもなければ設定されたURLから取得して `.cache/` に保存し、登録します。`.cache/` はGitの対象外です。独自画像をリポジトリに含める場合は、画像のライセンスも確認してください。

### 幽境の激戦
Bot起動時にDiscord Application Emojiが未登録の場合のみ、Enka.Networkから取得して `.cache/` へ保存します。

```text
https://enka.network/ui/UI_LeyLineChallenge_Medal_1.png
...
https://enka.network/ui/UI_LeyLineChallenge_Medal_6.png
```

取得した画像はリポジトリのUnlicense対象外です。画像の権利は各権利者に帰属します。
