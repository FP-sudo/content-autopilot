<h1 align="center">Content Autopilot</h1>

<p align="center">
<strong>一度命じたら、コンテンツは自律的に生まれ続ける</strong>
</p>

<p align="center">
<code>129 skills</code>&nbsp;&nbsp;|&nbsp;&nbsp;<code>10 Python scripts</code>&nbsp;&nbsp;|&nbsp;&nbsp;<code>3 platforms</code>&nbsp;&nbsp;|&nbsp;&nbsp;<code>Zero user intervention</code>
</p>

<p align="center">
Claude Code plugin for fully autonomous content creation.<br>
トレンド調査からコンテンツ生成、品質管理、ダッシュボード出力まで——<br>
<strong>人間が介入するのは、最初の1コマンドだけ。</strong>
</p>

---

## 実行するとこうなる

```
━━━━ Content Autopilot ━━━━━━━━━━━━━━━━━━
[1/8] Profile loaded (auto-created: default)
      Theme: "AI x ビジネス" | Stage: TOFU
[2/8] Funnel analysis: TOFU 50% → target 50% ✓
      Decision: TOFU trending selected
[3/8] WebSearch: 3 candidates found
      → "AIエージェントが変える働き方" (score: 0.91) ← selected
[4/8] Generating: note(3,200字) + X(6tweets) + IG
[5/8] Quality gate:
      note: 68/100 → auto-improving hook + structure...
      note: 81/100 ✓ (improved +13)
      X: 79/100 ✓
      IG: 76/100 ✓
[6/8] Pre-publish: 5/5 checks passed ✓
[7/8] History recorded → Dashboard opened in browser
[8/8] Pipeline complete ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**人間の操作: `/daily-autopilot` の1コマンドのみ。残りはすべて自律判断。**

---

## "他のAIツールとの違い"

「AIでコンテンツを作る」ツールは多い。しかし、そのほとんどは**人間がプロンプトを考え、出力を読み、判断する**ことを前提としている。Content Autopilotは違う。

| | ChatGPT / Claude 直接利用 | **Content Autopilot** |
|---|---|---|
| **トピック選択** | ユーザーが考える | トレンド自動検索 + ファネル分析で自動決定 |
| **品質管理** | ユーザーが読んで判断 | 6軸採点 + 自動改善ループ |
| **マルチ展開** | プラットフォームごとに依頼 | note + X + IG を1コマンドで同時生成 |
| **学習** | 毎回ゼロから | 履歴分析 + ファネルバランス + トレンド追跡 |
| **品質可視化** | なし | HTMLダッシュボード自動生成 |

**核心的な違い**: 従来のAIツールは「賢いアシスタント」。Content Autopilotは**自律的に判断・実行・改善するシステム**。

---

## パイプライン全体像

`/daily-autopilot` を実行すると、以下のステップが**完全自律で**動く。

```
/daily-autopilot
    |
    v
[Profile] -----> [Funnel Analysis] -----> [WebSearch]
                                              |
                                        auto-select topic
                                              |
                                              v
                                    [Generate 3 platforms]
                                         note / X / IG
                                              |
                                              v
                                    [Quality Gate 6-axis]
                                         |         |
                                    score>=70   score<70
                                         |         |
                                         |    auto-improve
                                         |    (max 2 rounds)
                                         |         |
                                         v         v
                                    [Pre-publish Check]
                                         8 validations
                                              |
                                              v
                                    [Record + Dashboard]
                                     HTML auto-open
```

**人間の判断が必要なポイント: ゼロ。** トピック選択もスコア改善も、すべてシステムが自律的に判断する。

---

## Quick Demo（審査員向け）

```bash
# インストール（Claude Code内で実行）
/plugin marketplace add FP-sudo/content-autopilot
/plugin install content-autopilot@content-autopilot

# 実行（必要なのはこれだけ）
/daily-autopilot

# あとは見ているだけ:
# 1. プロフィール未作成 → 自動生成（セットアップ不要）
# 2. WebSearchでトレンド調査
# 3. ファネル分析でトピック自動選択
# 4. note / X / Instagram 向けコンテンツ同時生成
# 5. 6軸品質採点（日本語ネイティブチェック含む）
# 6. スコア70未満 → 自動改善（最大2ラウンド）
# 7. HTMLダッシュボードがブラウザで自動表示
```

**所要時間**: 約2-3分。**ユーザー操作**: 1コマンド。**生成物**: 3プラットフォーム分のコンテンツ + 品質レポート。

---

## Demo Video

[3分デモ動画](./DEMO_SCRIPT.md) — 撮影手順とナレーション台本

---

## 自律性の設計（Autonomy — 審査配点40%）

Content Autopilotが自律的に下す判断の一覧:

- **トピック選定**: WebSearchによるトレンド調査 + ファネルバランス分析で、何を書くべきかをシステムが決定
- **品質の自己改善ループ**: 6軸採点でスコア70未満なら、具体的な修正指示を生成して自動改善（最大2ラウンド）
- **フォールバック**: WebSearch失敗時はローカルのトピックライブラリから自動選択。外部依存でパイプラインは止まらない
- **重複回避**: 同日に複数回実行した場合、自動サフィックスでファイル名を分離
- **シリーズ継続追跡**: 進行中の連載がある場合、自動的に次回分を提案
- **ファネル自動バランシング**: TOFU 50% / MOFU 30% / BOFU 20% の比率を履歴から自動計算し、最適なステージを選択
- **プロフィール自動生成**: 初回実行時にプロフィールが存在しなければ、対話なしでデフォルト生成

**「一度命じたら、あとは任せろ」を文字通り実現する。** ユーザーが離席しても、パイプラインは最後まで走り切る。

---

## 品質システム（Quality — 審査配点35%）

### 6軸採点システム

すべてのコンテンツは公開前に6つの軸で自動採点される:

| 軸 | 評価内容 | 配点 |
|---|---|---|
| **Hook** | 冒頭3秒で読者を掴めるか | 20点 |
| **Readability** | 読みやすさ・流れ | 20点 |
| **Structure** | 論理構成・価値密度 | 20点 |
| **Platform Fit** | プラットフォーム最適化 | 15点 |
| **CTA** | 行動喚起の明確さ | 15点 |
| **AI Smell** | AI臭の検出・人間らしさ | 10点 |

### 日本語ネイティブチェック

汎用的な品質チェックではなく、**日本語コンテンツに特化した**検証:

- 漢字比率の適正チェック（多すぎると読みにくい、少なすぎるとカジュアルすぎる）
- です/ます調の一貫性
- 一文の長さ制限
- 接続詞の適切な使用

### プレパブリッシュ検証（8項目）

品質採点とは別に、公開前の最終チェックリストを自動実行:

- フォーマット整合性、リンク有効性、ハッシュタグ数、CTA存在確認、文字数制限、画像サイズ、メタデータ、法的コンプライアンス

### 自動改善ループ

スコアが閾値未満の場合、**何を直すべきかの具体的指示**を生成し、自動で修正を実行する。「スコアが低い」と報告するだけのシステムとは根本的に異なる。

---

## HTMLダッシュボード

パイプライン完了時にブラウザで自動表示（ダークテーマ、CSSアニメーション、外部依存ゼロ）:

```
┌─────────────────────────────────────────────────────────┐
│  Content Autopilot Dashboard              v9.0 | 2026  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐         │
│  │  5   │ │ 90.0 │ │  ▲   │ │ Num  │ │  2d  │         │
│  │Runs  │ │Qual. │ │Trend │ │Logic │ │Streak│         │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘         │
│                                                         │
│  Today's Content     Quality Scores                     │
│  ┌────┐┌────┐┌────┐ Hook     ████████████ 10/10        │
│  │Note││ X  ││ IG │ Read.    ████████░░░░  8/10        │
│  │C 70││B 86││B 86│ Struct.  █████████░░░  9/10        │
│  └────┘└────┘└────┘ CTA      ████████████ 10/10        │
│                                                         │
│  Funnel Balance                                         │
│  Actual: TOFU 40% ████  MOFU 40% ████  BOFU 20% ██    │
│  Target: TOFU 50% █████ MOFU 30% ███   BOFU 20% ██    │
└─────────────────────────────────────────────────────────┘
```

> 実際のダッシュボードはCSSアニメーション付き。スコアバーがスライドイン、カードがフェードインします。

![Dashboard Screenshot](docs/dashboard-screenshot.png)

---

## 129 Skills 一覧

9カテゴリ、129スキル。すべてが連携し、一つのコンテンツOSとして機能する。

| カテゴリ | スキル数 | 主要スキル |
|---|---|---|
| **Core Pipeline** | 6 | `daily-autopilot`, `content-writer`, `trend-scout`, `setup-profile`, `visual-creator`, `funnel-designer` |
| **Analytics & Strategy** | 20 | `content-analytics`, `competitor-scout`, `series-designer`, `batch-generator`, `seo-optimizer`, `monetize-report` |
| **Intelligence** | 20 | `content-dna`, `viral-reverse`, `algorithm-guide`, `smart-cta`, `brand-voice`, `trend-predictor` |
| **Precision & QA** | 20 | `fact-checker`, `content-grader`, `pre-publish`, `readability-tuner`, `consistency-auditor`, `engagement-predictor` |
| **Feedback Loop** | 10 | `performance-log`, `ab-test-runner`, `post-mortem`, `quality-benchmark`, `pipeline-view` |
| **Content OS** | 10 | `skill-advisor`, `workflow-chain`, `mind-map`, `persuasion-framework`, `audience-simulator` |
| **Products & Business** | 13 | `course-builder`, `book-proposal`, `revenue-forecast`, `launch-sequence`, `pricing-strategy` |
| **Strategic Thinking** | 20 | `anti-content`, `compound-content`, `mirror-content`, `identity-architect`, `content-genome` |
| **Adaptation & Learning** | 10 | `energy-adapter`, `smart-suggest`, `meta-learning`, `skill-composer`, `deep-audit` |

---

## アーキテクチャ

AGI Lab Skills Marketplace 準拠のプラグイン構造:

```
content-autopilot/
├── .claude-plugin/
│   └── marketplace.json          # マーケットプレイス登録情報
├── plugins/
│   └── content-autopilot/
│       ├── .claude-plugin/
│       │   └── plugin.json       # プラグイン定義
│       ├── skills/               # 129 skills (各 SKILL.md)
│       │   ├── daily-autopilot/  # パイプラインオーケストレーター
│       │   ├── content-writer/   # マルチプラットフォーム生成
│       │   ├── trend-scout/      # トレンド調査
│       │   ├── content-grader/   # 6軸品質採点
│       │   └── ...               # 125 more skills
│       └── scripts/              # 10 Python scripts
│           ├── autopilot.py      # パイプライン制御 + 実行マニフェスト + 累積サマリー
│           ├── grader.py         # 6軸品質採点エンジン
│           ├── dashboard.py      # HTMLダッシュボード生成
│           ├── pre_publish.py    # 8項目プレパブリッシュ検証
│           ├── record_history.py # 履歴・シリーズ記録
│           ├── init_data.py      # ゼロセットアップ初期化
│           ├── data_manager.py   # 共通データI/O
│           ├── analytics.py      # コンテンツ分析ダッシュボード
│           ├── funnel_balance.py # ファネルバランス計算
│           └── deep_audit.py     # システム整合性監査
├── README.md
└── LICENSE
```

### データフロー

```
profile.json ─────────────────────> autopilot.py
                                        |
WebSearch API ──> trend data ──────────>|
content-history.json ──> funnel data ──>|
                                        |
                                        v
                                  content-writer
                                        |
                                        v
                               grader.py (6-axis)
                                   |         |
                              pass (>=70)  fail (<70)
                                   |         |
                                   |    auto-improve
                                   |         |
                                   v         v
                              pre_publish.py
                                        |
                                        v
                              record_history.py
                                        |
                                        v
                              dashboard.py ──> HTML
```

---

## インパクト（Impact — 審査配点25%）

### クリエイターだけではない、幅広い応用可能性

Content Autopilotは特定の職種に限定されない。コンテンツ発信が必要なあらゆる人に価値を提供する:

- **フリーランス・個人クリエイター** — 本業に集中しながらコンテンツ発信を自動化
- **中小企業のマーケティング担当** — 少人数チームでも毎日の発信を維持
- **副業でコンテンツ発信する会社員** — 限られた時間でも継続的なアウトプットを実現
- **コンテンツマーケティングエージェンシー** — クライアント複数案件の並行運用を効率化

### 解決する課題

日本の個人クリエイター・スモールビジネスが直面する「コンテンツ継続の壁」:

- **毎日のネタ探し**に30-60分 → **自動化で0分**
- **3プラットフォーム別の書き分け**に2-3時間 → **1コマンドで同時生成**
- **品質のばらつき**（疲れた日は質が落ちる）→ **6軸採点で品質を一定に保証**
- **ファネル設計の挫折**（概念は知っていても実行が続かない）→ **自動バランシングで無意識に最適化**

### 対象プラットフォーム

| プラットフォーム | 生成コンテンツ |
|---|---|
| **note** | SEO最適化された長文記事（有料/無料） |
| **X (Twitter)** | トレンドに乗るツイート・スレッド |
| **Instagram** | ハッシュタグ最適化されたキャプション + カルーセルスクリプト |

### ファネル戦略（DRM）

```
X / Instagram (TOFU)       note free (MOFU)        note paid (BOFU)
+------------------+     +------------------+     +------------------+
|  Reach & Attract |---->|  Trust & Educate  |---->|  Convert & Earn  |
|  30% of insight  |     |  80% of insight   |     |  100% + bonus    |
|  Curiosity gap   |     |  Free articles    |     |  Paid articles   |
|  CTA -> note     |     |  Lead magnet      |     |  Membership      |
+------------------+     +------------------+     +------------------+
```

**ファネルバランスもシステムが自律管理。** TOFU/MOFU/BOFUの比率を履歴データから計算し、次に生成すべきステージを自動決定する。

---

## Capability Levels

| Level | 要件 | 機能 |
|---|---|---|
| **Level 1** | Claude Code + WebSearch | テキストコンテンツ生成（全機能利用可能） |
| **Level 2** | + gemini-image or fal.ai MCP | テキスト + 画像自動生成 |
| **Level 3** | + X API credentials | テキスト + 画像 + X自動投稿 |

---

## 出力ファイル

```
~/Desktop/content-autopilot-output/
  note_2026-03-21.md              # note記事
  x_2026-03-21.md                 # Xツイート/スレッド
  instagram_2026-03-21.md         # Instagramキャプション + ハッシュタグ
  dashboard.html                  # 品質ダッシュボード（自動生成）
  note_ogp_2026-03-21.png         # note OGP画像 (Level 2+)

~/.content-autopilot/
  profile.json                    # ユーザープロフィール
  content-history.json            # コンテンツ履歴（自動記録）
  content-dna.json                # コンテンツ成功パターン
  ...                             # 20+ データファイル
```

---

## インストール

Claude Code 内で以下を実行:

```bash
# marketplace として追加
/plugin marketplace add FP-sudo/content-autopilot

# plugin をインストール
/plugin install content-autopilot@content-autopilot
```

インストール後、すぐに使えます:

```bash
# 全自律パイプラインを実行（セットアップ不要）
/daily-autopilot
```

> プロフィール未作成でも自動生成されるため、初回から即実行可能です。
> カスタマイズしたい場合は `/setup-profile` を実行してください。

---

## Demo Video

[3分デモ動画撮影ガイド](./DEMO_SCRIPT.md) — ナレーション台本・操作手順・撮影Tips

---

## License

MIT
