---
name: daily-autopilot
description: 完全自律型コンテンツパイプライン — トレンド調査からコンテンツ生成・品質チェック・履歴記録まで、ユーザー介入ゼロで完走する。状態機械ベースで全判断を自動化。リアルタイム進捗表示付き。
---

# Daily Autopilot — 完全自律コンテンツ生成

## 実行の最優先事項

このスキルが起動したら、以下を**この順番通りに**実行する。
状態機械の分岐ロジックに従うが、**各ステップの "Output to user:" は必ずそのまま出力すること。**
省略・要約・言い換えは厳禁。

重要: 各python3コマンドは必ずBashツールで実行する。出力をJSONとしてパースし、次のステップに使う。


ワンコマンドでコンテンツパイプラインを完走する。**ユーザーへの質問は一切しない。**
各ステップの進捗をリアルタイムで表示し、判断根拠を可視化する。

## 起動条件

- `/daily-autopilot` または `/autopilot`
- 「今日のコンテンツ」「投稿を作って」「コンテンツパイプライン実行」


NOTE: `${CLAUDE_PLUGIN_ROOT}` はClaude Codeが自動的に解決する環境変数。
手動テスト時は以下で代替可能:
```
PLUGIN_DIR=~/content-autopilot/plugins/content-autopilot
```

## 状態機械（全判断を自動化）

CRITICAL: 各ステップの "Output to user:" セクションの内容は**必ずそのまま出力すること**。
これはリアルタイム進捗表示であり、省略や要約は禁止。

```
STATE: SETUP (Step 0)
  → mkdir -p ~/Desktop/content-autopilot-output
  → (出力先ディレクトリを確保)
  → STATE: BANNER

STATE: BANNER (Step 0/8)
  → パイプライン開始のビジュアルヘッダーを表示
  → STATE: INIT

  Output to user:
    ━━━━ Content Autopilot ━━━━━━━━━━━━━━━━━━

STATE: INIT (Step 1/8)
  → python3 ${CLAUDE_PLUGIN_ROOT}/scripts/autopilot.py --mode execute
  → status == "ready" → STATE: SEARCH
  → status == "error" && error == "profile_missing"
    → ユーザーに1つだけ質問する: 「どんなテーマのコンテンツを作りますか？（例: AI×ビジネス、英語学習、料理レシピ）」
    → 回答を受け取ったら、python3 ${CLAUDE_PLUGIN_ROOT}/scripts/init_data.py 実行
    → profile.jsonのtheme.mainをユーザーの回答で上書き
    → 再度 autopilot.py --mode execute
    → status == "ready" → STATE: SEARCH
    → 2回目もerror → エラー報告して終了

  Output to user (status == "ready"):
    [1/8] Profile loaded ({profile_name})
          Theme: "{theme}" | Stage: {recommended_stage}

  Output to user (profile auto-created):
    [1/8] Profile loaded (auto-created: default)
          Theme: "{theme}" | Stage: {recommended_stage}

  Output to user (fatal error):
    [1/8] ✗ Profile load failed: {error_message}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    (pipeline aborted)

STATE: SEARCH (Step 2/8)
  → autopilot.pyの結果からファネルバランスを表示
  → WebSearch(execution_plan[0].query)
  → 検索結果あり:
    → 結果からトピックを1つ自動選択（最もエンゲージメントが期待できるもの）
    → STATE: GENERATE
  → 検索結果なし / WebSearch失敗:
    → execution_planのfallback_topicを使用
    → STATE: GENERATE

  Output to user (検索成功):
    [2/8] Funnel analysis: {stage} {current}% → target {target}% {✓ or ↑adjust}
          Decision: {stage} {trending/balanced/catch-up} selected
    [3/8] WebSearch: {N} candidates found
          → "{selected_topic}" (score: {score}) ← selected
          → "{candidate_2}" (score: {score})
          → "{candidate_3}" (score: {score})

  Output to user (検索失敗 → fallback):
    [2/8] Funnel analysis: {stage} {current}% → target {target}% {✓ or ↑adjust}
          Decision: {stage} {trending/balanced/catch-up} selected
    [3/8] WebSearch: failed → fallback topic used
          → "{fallback_topic}" ← auto-selected from library

STATE: GENERATE (Step 4/8)
  → content-writerスキルの仕様に従いコンテンツ一括生成
  → 参照: plugins/content-autopilot/skills/content-writer/SKILL.md（タイトルロジック9種、プラットフォーム別仕様）
  → 各プラットフォーム用ファイルを保存:
    - ~/Desktop/content-autopilot-output/note_{date}{suffix}.md
    - ~/Desktop/content-autopilot-output/x_{date}{suffix}.md
    - ~/Desktop/content-autopilot-output/instagram_{date}{suffix}.md
  → 
STATE: IMAGE (Step 4.5 — OGP画像生成)
  → MCPツール mcp__gemini-image__generate_image が利用可能か確認
  → 利用可能:
    → 記事のトピックに基づいたOGP画像を自動生成
    → プロンプト: "Modern minimalist blog header for {topic}. Dark gradient, geometric shapes, professional."
    → aspect_ratio: "16:9"
    → 保存先: ~/Desktop/content-autopilot-output/note_ogp_{date}.png
  → 利用不可: スキップ

  Output to user (成功):
    [4.5] OGP image → generated ✓
  Output to user (スキップ):
    [4.5] OGP image → Gemini MCP未設定（スキップ）

STATE: GRADE

  生成時の品質ルール（厳守）:
  - 最初の1文は「？」「数字」「意外な事実」のいずれかを含む
  - 「本記事では」「さまざまな」「重要なことは」は使用禁止
  - 段落は3文以内、各段落の間に空行
  - noteは必ず2500文字以上（短いと品質ゲートで不合格になる）。1500文字未満は確実にFAIL。文字数が不足しそうな場合は具体例やデータを追加する

  Output to user:
    [4/8] Generating: note({N}字) + X({N}tweets) + IG


STATE: IMAGE (Step 4.5 — OGP画像生成)
  → MCPツール mcp__gemini-image__generate_image が利用可能か確認
  → 利用可能:
    → 記事のトピックに基づいたOGP画像を自動生成
    → プロンプト: "Modern minimalist blog header for {topic}. Dark gradient, geometric shapes, professional."
    → aspect_ratio: "16:9"
    → 保存先: ~/Desktop/content-autopilot-output/note_ogp_{date}.png
  → 利用不可: スキップ

  Output to user (成功):
    [4.5] OGP image → generated ✓
  Output to user (スキップ):
    [4.5] OGP image → Gemini MCP未設定（スキップ）

STATE: GRADE (Step 5/8)
  → python3 ${CLAUDE_PLUGIN_ROOT}/scripts/grader.py {note_file} --json
  → score >= 75 → STATE: CHECK
  → score < 75:
    → issuesのfield/actionを読み取り、自動修正
    → 再grading（最大2回）
    → 2回修正してもscore < 75 → 警告付きでSTATE: CHECK

  Output to user (全合格):
    [5/8] Quality gate:
          note: {score}/100 ✓
          X: {score}/100 ✓
          IG: {score}/100 ✓

  Output to user (自動修正あり):
    [5/8] Quality gate:
          note: {initial_score}/100 → auto-improving {issue_field}...
          note: {improved_score}/100 ✓ (improved +{delta})
          X: {score}/100 ✓
          IG: {score}/100 ✓

  Output to user (2回修正しても不合格):
    [5/8] Quality gate:
          note: {initial_score}/100 → auto-improving...
          note: {final_score}/100 ⚠ (below 75 after 2 retries)
          X: {score}/100 ✓
          IG: {score}/100 ✓

STATE: CHECK (Step 6/8)
  → python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pre_publish.py {note_file} --json
  → all_pass == true → STATE: RECORD
  → all_pass == false:
    → 失敗チェック項目を読み取り、自動修正
    → 再check（最大2回）
    → 2回修正しても失敗 → 警告付きでSTATE: RECORD

  Output to user (全合格):
    [6/8] Pre-publish: {N}/{N} checks passed ✓

  Output to user (修正後合格):
    [6/8] Pre-publish: {passed}/{total} checks → auto-fixing {failed_items}...
          Pre-publish: {N}/{N} checks passed ✓ (fixed {M} issues)

  Output to user (修正しても不合格):
    [6/8] Pre-publish: {passed}/{total} checks ⚠
          Failed: {failed_check_names} (continuing with warning)

STATE: RECORD (Step 7/8)
  → python3 ${CLAUDE_PLUGIN_ROOT}/scripts/record_history.py \
      --topic "{topic}" --stage {stage} --category {category} \
      --date {date} --platforms {platforms} \
      [--suffix {suffix}] [--series-id {series_id}]
  → STATE: DASHBOARD

  Output to user:
    [7/8] History recorded: entry {date}-{suffix}

STATE: DASHBOARD (Step 7.5/8 — Dashboard Generation)
  → python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dashboard.py
  → open ~/Desktop/content-autopilot-output/dashboard.html
  → STATE: REPORT

  Output to user:
    [7.5] Dashboard generated → opening in browser...


STATE: PUBLISH (Step 7.75 — 外部連携)
  → MCPツール mcp__claude_ai_Notion__notion-create-pages が利用可能か確認
  → 利用可能:
    → 生成したnote記事をNotionページとして作成
    → ページタイトル: "[Content Autopilot] {topic}"
    → 内容: note記事のマークダウン本文
    → フッター: "Generated by Content Autopilot | {date} | Stage: {stage} | Quality: {score}/100"
  → 利用不可: スキップ（パイプラインに影響しない）

  Output to user (成功):
    [7.75] Notion → 記事を自動保存 ✓
  Output to user (スキップ):
    [7.75] Notion → MCP未設定（スキップ）

STATE: REPORT (Step 8/8)
  → python3 ${CLAUDE_PLUGIN_ROOT}/scripts/autopilot.py --mode summary
  → summaryデータからIntelligence Reportを構築
  → パイプライン完了フッターを表示 → 終了

  → 自動公開アシスト:
    1. note記事をクリップボードにコピー（pbcopy）
    2. note.com にログインし「投稿」ボタンからテキスト投稿画面を開く
    3. Xの投稿画面を開く: https://x.com/intent/tweet?text={1ツイート目のURLエンコード}

  Output to user:
    [8/8] Pipeline complete ✓
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    --- Intelligence Report ---
    Total runs: {total} | Avg quality: {avg} → Today: {today_score} ({↑N or ↓N})
    Best title logic: {pattern_1} ({pct}%) > {pattern_2} ({pct}%)
    Quality trend: {↑ or ↓}{delta} pts/week over {N} weeks
    Funnel health: TOFU {pct}% / MOFU {pct}% / BOFU {pct}% ({balanced ✓ or imbalanced ⚠})
```

## 線形フロー（クイックリファレンス）

1. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/autopilot.py --mode execute` → JSONパース
2. WebSearch(query) → トピック自動選択
3. コンテンツ生成（note + X + Instagram）→ ファイル保存
4. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/grader.py {note_file} --json` → score < 75 なら自動修正
5. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pre_publish.py {note_file} --json` → 失敗項目を自動修正
6. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/record_history.py --topic ... --stage ... --category ... --date ...`
7. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dashboard.py` → `open ~/Desktop/content-autopilot-output/dashboard.html`
8. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/autopilot.py --mode summary` → Intelligence Report表示

## 進捗表示ルール

1. **各Stateの "Output to user:" に記載された内容をそのまま出力すること。**省略・変更不可。
2. プレースホルダ `{...}` はスクリプト出力やコンテキストの実値で置換する。
3. スコアの `✓` / `⚠` / `✗` は以下の基準:
   - `✓` : 合格（score >= 75, all checks passed）
   - `⚠` : 警告付き続行（score < 75 after retries, some checks failed after retries）
   - `✗` : 致命的エラー（pipeline中断）
4. ステップ番号は `[N/8]` 形式で固定。Dashboard生成は `[7.5]` とする。
5. Intelligence Reportの各項目が取得不能な場合は `N/A` と表示（項目自体は省略しない）。
6. ヘッダー・フッターの罫線幅は固定（ヘッダー: `━━━━ Content Autopilot ━━━━━━━━━━━━━━━━━━`、フッター: `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`）。

## 自動判断ルール（ユーザーに聞かない）

### トピック選択
1. アクティブシリーズがある → シリーズの次パートを自動使用
2. シリーズなし → WebSearchトップ結果から自動選択
3. WebSearch失敗 → フォールバックトピック自動使用

### ファネルステージ選択
- autopilot.py --mode execute の recommended_stage を使用
- 直近7日のバランスから自動計算（TOFU 50% / MOFU 30% / BOFU 20%）

### note種別（free/paid）
- TOFU/MOFU → free
- BOFU → paid

### タイトル選択
- 生成した候補の1番目を自動採用

### 既に今日生成済みの場合
- **ユーザーに聞かずに**サフィックス付きで追加生成
- 例: note_2026-03-21-002.md

### 品質不合格時
- grader/pre_publishの具体的なissueを読み取り自動修正
- 最大2回リトライ、それでも不合格なら警告付きで続行

## コンテンツ生成仕様

### note記事
- 文字数: 2000-5000文字（日本語）
- セクション: 3-7個（##見出し付き）
- 文体: です/ます体で統一
- 漢字率: 20-40%
- 1段落: 3文以内
- フック: 最初の1文は40文字以内
- CTA: noteフォロー + 次回記事の予告（TOFU/MOFU）/ 有料記事購入（BOFU）
  - 注意（厳守）: 存在しないURL、ダウンロードリンク、リードマグネットへの誘導は絶対に書かない。「毎日更新」等の守れない約束も禁止。CTAは「フォロー」「次回予告」「note記事への誘導」のみ許可
- まとめセクション必須
- **note.com固有ルール:**
  - **noteアルゴリズム対応（2026年版）:**
    - 投稿後24時間以内に10スキ以上 → 「おすすめ」に乗る
    - 読了率が重要 → 最後まで読ませる構成（まとめセクション必須）
    - 適切なタグ（5個）→ カテゴリアルゴリズムに乗る
    - note砲狙い: 特定タグの「注目記事」に選ばれるとPV急増
  - 冒頭に「この記事でわかること」を3行箇条書き（目次代わり）
  - 見出しは読者の疑問形で書く（例: 「## なぜAIエージェントが必要なのか」）
  - 段落間に適度な空行を入れる（note表示で読みやすい）
  - 画像の代わりに「---」の区切り線を使いリズムを作る
  - 最後に「他のnote記事」への誘導を入れる
- **BOFU（有料記事）の場合:**
  - 冒頭200-300文字は無料プレビュー
  - 「--- ここから有料 ---」の境界線を挿入
  - 有料部分にはテンプレート、チェックリスト等の実用的な付加価値を入れる
  - 記事概要（note SEO用）を本文冒頭から自動生成
  - タグ候補を5個提示

### Xスレッド
- ツイート数: 5-7
- 各ツイート: 280文字以内（短い方がエンゲージメント高。返信を誘う質問形式が最も効果的 — 返信はいいねの27倍の重み）
- 最終ツイートにnote誘導CTA
- スレッド番号付き（1/5, 2/5...）
- **X最新アルゴリズム対応（2026年版）:**
  - 返信 = いいねの27倍の重み。質問形式で返信を誘う
  - 会話（返信+著者返信）= いいねの150倍
  - リツイート = いいねの20倍、ブックマーク = 10倍
  - 最初の30分のエンゲージメント速度が最重要
  - 6時間で露出が半減するため、投稿時間が重要
  - 1ツイート目に最も強い主張を置く（スクロール停止させる）

### Instagramキャプション
- フック（最初の行）: 125文字以内
- ハッシュタグ: 25-30個
- CTA: プロフィールリンク誘導


## 品質リファレンス（Claudeへの参考例）

生成品質を高めるため、良い例・悪い例を以下に示す。これらを参考にコンテンツを生成すること。

### noteのフック（最初の1文）

```
✓ 「ChatGPTに月5万円払っている人へ。無料で同じことができる方法がある。」
✓ 「3ヶ月で売上2倍。やったことはAIに"この3つ"を任せただけ。」
✗ 「本記事ではAIの活用方法について解説します。」（AI臭い・フックが弱い）
```

### Xスレッドの冒頭ツイート

```
✓ 「AIで月10時間の作業を削減した。具体的な方法を共有する 🧵」
✗ 「AIについてのスレッドです。ぜひ最後まで読んでください。」
```

## 完了レポート形式

完了レポートは、リアルタイム進捗表示の累積として自動構成される。
パイプライン全体の出力は以下の形式となる:

```
━━━━ Content Autopilot ━━━━━━━━━━━━━━━━━━
[1/8] Profile loaded (auto-created: default)
      Theme: "AI x ビジネス" | Stage: TOFU
[2/8] Funnel analysis: TOFU 52% → target 50% ✓
      Decision: TOFU trending selected
[3/8] WebSearch: 3 candidates found
      → "AIで月10時間の作業削減" (score: 0.92) ← selected
      → "ChatGPT新機能まとめ" (score: 0.71)
      → "AI導入の失敗例" (score: 0.65)
[4/8] Generating: note(3,200字) + X(6tweets) + IG
[5/8] Quality gate:
      note: 64/100 → auto-improving hook...
      note: 82/100 ✓ (improved +18)
      X: 78/100 ✓
      IG: 75/100 ✓
[6/8] Pre-publish: 5/5 checks passed ✓
[7/8] History recorded: entry 2026-03-21-001
[7.5] Dashboard generated → opening in browser...
[8/8] Pipeline complete ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

--- Intelligence Report ---
Total runs: 12 | Avg quality: 79 → Today: 84 (↑5)
Best title logic: Numbers (42%) > Paradox (28%)
Quality trend: ↑3.2 pts/week over 4 weeks
Funnel health: TOFU 48% / MOFU 32% / BOFU 20% (balanced ✓)
```

## Dashboard Generation

Step 7.5 で呼び出されるダッシュボード生成:

1. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dashboard.py` を実行
   - content-history.json を読み込み、HTMLダッシュボードを生成
   - 出力先: `~/Desktop/content-autopilot-output/dashboard.html`
2. `open ~/Desktop/content-autopilot-output/dashboard.html` でブラウザ表示
3. ダッシュボードには以下を含む:
   - ファネルバランスの円グラフ
   - 品質スコアの推移グラフ
   - 直近7日のコンテンツカレンダー
   - タイトルパターン分析

## Intelligence Report

Step 8/8 の最終レポートで表示。データは以下のコマンドで取得:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/autopilot.py --mode summary
```

レポート項目:
- **Total runs**: 累計実行回数と平均品質スコア、本日との差分
- **Best title logic**: タイトルパターンの成功率ランキング
- **Quality trend**: 週次の品質スコア変動率
- **Funnel health**: TOFU/MOFU/BOFUの割合とバランス判定

データが不足している場合（初回〜3回目の実行）は取得可能な項目のみ表示し、不足項目は `N/A (need {N} more runs)` と表示する。



## 公開手順ガイド（パイプライン完了後に自動表示）

パイプライン完了後、以下の「次のステップ」を必ず表示する:

```
--- 次のステップ ---

📝 note:
  1. ファイルを開く: open ~/Desktop/content-autopilot-output/note_{date}.md
  2. note.com にログイン → 「投稿」→ マークダウン貼り付け
  3. 有料/無料は自動判定済み（ファネルステージに基づく）
  4. OGP画像は別途設定（Level 2ならgemini-imageで自動生成可能）

🐦 X (Twitter):
  1. ファイルを開く: open ~/Desktop/content-autopilot-output/x_{date}.md
  2. 1/Nから順にツイート。各ツイート間に「---」で区切り済み
  3. 最終ツイートのnote誘導CTAを確認

📸 Instagram:
  1. ファイルを開く: open ~/Desktop/content-autopilot-output/instagram_{date}.md
  2. キャプションをコピー → Instagramアプリに貼り付け
  3. ハッシュタグは本文末尾に25-30個配置済み

📊 ダッシュボード:
  → ~/Desktop/content-autopilot-output/dashboard.html（ブラウザで開き済み）
```


## 外部連携（MCP経由 — 自動実行）

パイプライン完了後、以下のMCPツールが利用可能な場合は自動的に連携する。
利用不可の場合はスキップし、ファイル出力のみで完了する。

### Notion連携
MCPツール `mcp__notion__API-post-page` が利用可能な場合:
1. 生成したnote記事をNotionページとして自動作成
2. ページタイトル = 記事タイトル
3. ページ内容 = マークダウン本文
4. タグ: funnel_stage, category, date を付与


### Gmail連携
MCPツール mcp__claude_ai_Gmail__gmail_create_draft が利用可能な場合:
1. 生成したnote記事をHTML形式のGmail下書きとして作成
2. 宛先: ユーザー自身（レビュー用）
3. 件名: "[Content Autopilot] {topic} | {date} | {stage} | {score}/100"
4. 本文: note記事のHTML変換版

  Output to user (成功):
    [7.76] Gmail → 下書き保存 ✓


### Google Calendar連携
MCPツール mcp__claude_ai_Google_Calendar__gcal_create_event が利用可能な場合:
1. 翌日の投稿リマインダーをカレンダーに自動登録
2. イベント名: "[Content Autopilot] コンテンツ投稿 — note / X / Instagram"
3. 説明: ファイルパス + 品質スコア + ファネルステージ
4. 30分前にポップアップ通知

  Output to user (成功):
    [7.77] Calendar → 投稿リマインダー登録 ✓

### Gmail連携
MCPツール `mcp__claude_ai_Gmail__gmail_create_draft` が利用可能な場合:
1. note記事をGmail下書きとして保存（レビュー用）
2. 件名: 「[Content Autopilot] {date} {topic}」

連携の有無はパイプラインの成功に影響しない。MCP未設定でもパイプラインは正常に完了する。

## エラーリカバリ

| エラー | 自動対応 | 進捗表示 |
|--------|---------|----------|
| profile.json未作成 | init_data.py実行 → 1回リトライ | `[1/8] Profile loaded (auto-created: default)` |
| WebSearch失敗 | フォールバックトピックライブラリから自動選択 | `[3/8] WebSearch: failed → fallback topic used` |
| grader不合格 | issues読み取り → 自動修正 → 最大2回リトライ | `note: {score}/100 → auto-improving {field}...` |
| pre_publish不合格 | 失敗項目を自動修正 → 最大2回リトライ | `Pre-publish: {N}/{M} checks → auto-fixing...` |
| 画像MCP未接続 | テキストプロンプトのみ出力（画像スキップ） | `(image generation skipped: MCP not connected)` |
| 出力ディレクトリなし | mkdir -p で自動作成 | `(output directory created)` |
| 今日既に生成済み | -002サフィックスで自動追加生成 | suffix がステップ内で自動反映 |
| dashboard.py失敗 | 警告を表示しSTATE: REPORTへ続行 | `[7.5] Dashboard generation failed ⚠ (skipped)` |
| autopilot.py --mode summary失敗 | Intelligence Reportを `N/A` で埋めて表示 | `--- Intelligence Report ---` の各項目が `N/A` |

## クイックモード

`/autopilot quick` — 通常モードと同じ（全て自動のため差分なし）。

## 出力先

- テキスト: `~/Desktop/content-autopilot-output/`
- 画像: `~/Desktop/content-autopilot-output/`
- ダッシュボード: `~/Desktop/content-autopilot-output/dashboard.html`
- 履歴: `~/.content-autopilot/content-history.json`
