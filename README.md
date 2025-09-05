# ResoBotGW

実験的な Resonite 向け Bot オーケストレーション・プロジェクトです。ResoBotMCP によって抽象化された Resonite 内の Bot を操作し、GW 的な同時並行 AI Agent の連携により、以下の両立を目標とします。

- 自律性
- 娯楽性（観て・触って楽しい振る舞い）
- 環境認識能力（ワールド/周囲の状態への反応）
- 多人数環境への適応
- 低レイテンシな反応

メインアーキテクチャは OpenAI の Agents SDK を想定し（API 確認後に導入）、実装は Python 3.13、ビルド/運用は Hatch を採用します。アプリケーションループは asyncio を徹底し、`runner.run()` を中心に据えます。

## ステータス

- 状態: 初期化中（最小スケルトン）
- 破壊的変更: 許容（`AGENTS.md` の変更容易性ゲートに従う）

## クイックスタート

前提:

- Python 3.13 が利用可能
- Hatch がインストール済み（`pipx install hatch` など）
- OpenAI API キー（`OPENAI_API_KEY`）

セットアップと基本コマンド:

```bash
hatch env create
hatch run format     # フォーマット
hatch run lint       # Lint
hatch run typecheck  # 型チェック（basedpyright）
hatch run test       # テスト
hatch run mdfmt-check  # Markdown フォーマット確認

# 実行（最小スケルトン: Noop ランナー）
hatch run run -- --dry-run

# OpenAI Agents SDK ランナー（import は起動時に実施）
# ネットワークと API キーが必要（API 仕様の確認後に有効化予定）
OPENAI_API_KEY=... hatch run resobot-gw-openai run -- --bootstrap-hello
```

現状の `run` はスケルトン（非同期ランナー/コリレーションID付ログ）です。Agents SDK の統合は API 確認後に実装します。

## 目標と設計の要旨

- 目的: ResoBotMCP を経由して Resonite 内 Bot を制御し、GW 的に複数の AI Agent を並列連携させることで、人が集まる場でのインタラクション品質と反応速度を両立する。
- 範囲/境界: MCP は Agents SDK の機能を利用して接続。Resonite 側は ResoBotMCP を MCP サーバとして提供し、GW は Agents SDK 経由で利用。GW は AI 推論と意思決定・調停の責務に集中。
- 採用: OpenAI Agents SDK（メイン）、Python 3.13、Hatch。
- テスト戦略: ユニット（純粋ロジック）、結合（エージェント間プロトコル）、外部境界はフェイク/モックで代替。

詳細な運用規約や変更方針は `AGENTS.md` を参照してください。特に本プロジェクトでは以下を厳守します:

- dynamic import・`try` で囲った import の禁止
- Protocol の使用禁止（ABC による抽象）
- 存在未確認 API の推測的利用を禁止（ドキュメント/コードで確認後に実装）
- `openai` パッケージを直接利用しない（Agents SDK アダプタ経由）

## 設定（Config）

- すべての設定は Pydantic Settings により型安全にロード/検証されます。
- `.env`（ルート）を自動読込。環境変数が優先。
- 必須: `OPENAI_API_KEY`（空文字不可）。

MCP（StdioMcpd）:

- 任意: `MCP_STDIO_COMMAND`（設定時に Agents SDK の `MCPServerStdio` で接続）
- 任意: `MCP_STDIO_ARGS`（空白区切りで引数を指定）

例: `.env`

```
OPENAI_API_KEY=sk-...
# StdioMcpd への接続
# MCP_STDIO_COMMAND=stdbin-or-wrapper
# MCP_STDIO_ARGS=--flag1 value1 --flag2
```

## ライセンス

MIT © esnya
