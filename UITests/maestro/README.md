# Maestro flows

`UITests/ChiikawaRadarUITests.swift`（Xcodeでビルドして回すXCUITest）とは別物。
こちらはアプリに組み込まず外側から操作する、Maestro CLI / Maestro MCP 用のYAMLフロー。

## 実行方法

シミュレータを起動した状態で:

```sh
export JAVA_HOME="$HOME/.local/opt/jdk-21/Contents/Home"
export PATH="$JAVA_HOME/bin:$HOME/.maestro/bin:$PATH"
maestro --device <シミュレータのUDID> test UITests/maestro/
```

1本だけなら `maestro --device <UDID> test UITests/maestro/01_launch_and_tabs.yaml`。

Claude Code のMaestro MCP経由でも、この中のYAMLをそのまま `run` ツールに渡して実行できる。

## フロー一覧

- `01_launch_and_tabs.yaml` — 起動して5タブ（レーダー/地図/一覧/情報/設定）が揃っているか
- `02_settings_feed_section.yaml` — 設定画面をスクロールして情報フィードのセクションに辿り着けるか
- `03_sightings_feed_refresh.yaml` — 情報タブでpull-to-refreshできるか
- `04_map_categories.yaml` — 地図タブのカテゴリチップ（常設店/取扱店/コンビニ）が表示されるか
