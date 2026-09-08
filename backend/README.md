# sightings パイプライン

ちいかわグッズの **目撃・入荷・発売・くじ・催事** 情報を集めて、アプリ用の
`backend/out/sightings.json` を生成します。

- **サーバー不要**：GitHub Actions の定期実行（2時間おき）
- **APIキー不要で動く**：公式RSS ＋ Nominatim ジオコーディング
- **任意のシークレットで強化**：
  - `BSKY_IDENTIFIER` / `BSKY_APP_PASSWORD` … Bluesky 検索（＝目撃・入荷情報の本体）
  - `YAHOO_APP_ID` … ジオコーディングを Yahoo に（日本特化で速い）
  - `ANTHROPIC_API_KEY` … 種別・店名抽出を LLM で補強

## 取得元

| ソース | 内容 | 必要なもの |
|---|---|---|
| ちいかわマーケット `collections/all.atom` | 新作グッズ（＝発売） | なし |
| PR TIMES 全体フィード（ちいかわ で絞り込み） | プレスリリース | なし |
| Bluesky 検索 | 「◯◯で買えた/入荷してた」等 | 下記のセットアップ |

`sources.json` を編集すればフィードURL・検索語を足せます。`chains.json` は店名・エリアの辞書です。

## セットアップ

### 1. リポジトリを用意して push

このプロジェクト（`ChiikawaRadar/`）ごと GitHub の**公開リポジトリ**に push します（公開なら Actions・raw配信が無料）。

```bash
cd ~/claude/ChiikawaRadar
git init && git add . && git commit -m "init"
gh repo create chiikawa-radar --public --source=. --push   # gh CLI がある場合
```

### 2. Actions に書き込み権限を与える

リポジトリ → Settings → Actions → General → **Workflow permissions** → 「Read and write permissions」にチェック。

### 3.（推奨）Bluesky のシークレットを登録

1. Bluesky アカウントを作る（無料）
2. Settings → App Passwords → **新しい App Password を発行**（ログインパスワードそのものは使わない）
3. リポジトリ → Settings → Secrets and variables → Actions → New repository secret
   - `BSKY_IDENTIFIER` = 自分のハンドル（例 `you.bsky.social`）
   - `BSKY_APP_PASSWORD` = 発行した App Password

未登録でも動きますが、その場合は公式の発売情報のみになります。

### 4. 動かす

Actions タブ → 「sightings」→ **Run workflow** で手動実行。以後は2時間おきに自動更新。
生成物は `backend/out/sightings.json` にコミットされます。

### 5. アプリに URL を登録

`sightings.json` の raw URL：

```
https://raw.githubusercontent.com/<ユーザー名>/<リポジトリ名>/main/backend/out/sightings.json
```

これをアプリの **設定 → 情報フィード** の欄に貼り付け。

## ローカル実行

```bash
cd backend
pip install -r requirements.txt
BSKY_IDENTIFIER=you.bsky.social BSKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx python fetch_sightings.py
cat out/sightings.json
```

## 注意

- 目撃情報の位置は本文からの推定で「エリア〜店名」止まり・ノイズあり。アプリ側でも「未確認」扱いで表示します。
- 元投稿が削除されると、次回以降のクロールで自然に落ちます（21日で期限切れ）。
- Bluesky はちいかわ界隈の投稿量が X より少なめです。
