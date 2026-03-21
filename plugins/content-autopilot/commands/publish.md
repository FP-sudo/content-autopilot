---
description: "生成済みコンテンツをNotion/Gmailに連携する"
disable-model-invocation: true
---

以下の手順で生成済みコンテンツを外部サービスに連携してください:

1. `~/Desktop/content-autopilot-output/` から最新のnote記事を読み込む
2. MCP `mcp__notion__API-post-page` が利用可能なら、Notionページとして作成
3. MCP `mcp__claude_ai_Gmail__gmail_create_draft` が利用可能なら、Gmail下書きを作成
4. 連携結果をユーザーに報告

利用不可のMCPはスキップし、利用可能なもののみ実行する。
