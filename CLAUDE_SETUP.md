# Claude Code セットアップメモ

このプロジェクト専用の設定ではなく、`~/.claude/`(userスコープ)に入れたグローバル設定・MCP・プラグインの記録。どのプロジェクトでも共通して使える。詳細な経緯は `knowledge-base` アプリの「Claude Code」カテゴリのメモにも残してある。

## セキュリティ設定

強制ルールは `~/.claude/settings.json`、行動指針は `~/.claude/CLAUDE.md` に分けて管理。

`~/.claude/settings.json`:

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(./**/*.pem)",
      "Read(./**/*.key)",
      "Read(./**/id_rsa*)"
    ],
    "ask": [
      "Bash(git push:*)",
      "Bash(rm:*)"
    ]
  }
}
```

- `.env`・鍵ファイルの読み取りは常にブロック
- `git push`・`rm`は毎回確認
- curl/wgetはあえて対象外(ローカルAPI動作確認で多用するため)
- `.claudeignore`は公式機能として確認できず当てにならないため使わない方針

`.gitignore`には以下だけを追加(`.claude/`全体を除外すると、共有すべき`settings.json`まで消えるため個別ファイルに絞る):

```gitignore
/.claude/settings.local.json
CLAUDE.local.md
```

## MCPサーバー / プラグイン(userスコープ = 全プロジェクト共通)

```bash
# ナレッジグラフ型メモリ
claude mcp add memory --scope user -- npx -y @modelcontextprotocol/server-memory

# ドキュメント検索(HTTP版)
claude mcp add --transport http context7 --scope user https://mcp.context7.com/mcp

# AWS: CDK / CloudFormationのベストプラクティス・検証
python3 -m pip install --user uv   # uv/uvxが未導入だったので
claude mcp add aws-iac --scope user -- uvx awslabs.aws-iac-mcp-server@latest

# AWS: 構成図生成・pricing・ドキュメント検索がまとめて入っているプラグイン
claude plugin marketplace add awslabs/agent-plugins
claude plugin install deploy-on-aws@agent-plugins-for-aws
```

補足:
- awslabs公式の単体MCP(`aws-diagram-mcp-server`、`cdk-mcp-server`、`terraform-mcp-server`)は軒並み廃止済み。`aws-iac-mcp-server`と`deploy-on-aws`プラグインに統合されている
- Terraform用MCPはDocker/Goが必要なため未導入(CDK/CloudFormationはaws-iacでカバー)
- `aws-architecture-diagram`スキルで実際にCloudFront→ALB→ECS→RDS構成図(draw.io形式、AWS公式アイコン)の生成を確認済み

## 動作確認コマンド

- `/permissions` — denyルールが効いているか
- `/context` — 読み込まれているCLAUDE.mdの確認
- `claude mcp list` — MCPサーバーの接続状態
