<h1 align="center">Content Autopilot</h1>

<p align="center">
<strong>1コマンドで、note・X・Instagramのコンテンツを自律生成する</strong>
</p>

<p align="center">
Claude Code プラグイン | 12 Python scripts | 6軸品質採点 | HTMLダッシュボード
</p>

---

## デモ

![Demo](docs/demo.gif)

---

## 仕組み

`/daily-autopilot` を1回実行すると、8ステップが全自動で走ります:

```
━━━━ Content Autopilot ━━━━━━━━━━━━━━━━━━
[1/8] Profile loaded (auto-created)
[2/8] Funnel analysis → MOFU不足 → MOFU選択
[3/8] WebSearch → トピック自動選択
[4/8] note(2,500字) + X(6tweets) + IG 同時生成
[5/8] 6軸品質採点:
      note: 94/100 ✓
      X: 86/100 ✓   IG: 90/100 ✓
[6/8] 公開前チェック: 8/8 通過 ✓
[7/8] HTMLダッシュボード → ブラウザ表示
[8/8] 完了 ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

スコア75未満の場合、**原因を特定して自動改善**します:
```
note: 68/100 → 密度不足 + フック弱を検出
  → コンテンツ追加 + AI臭パターン除去
note: 82/100 ✓ (自動改善 +14点)
```

人間の操作は最初の1コマンドだけ。所要時間は約2-3分です。

---

## 生成例

### note記事

```markdown
# 3つのAI活用法で業務時間を半分にした話

「AIを使ってるのに、なぜ効率が上がらないのか？」

**この記事でわかること**
- チャットボットとAIエージェントの決定的な違い
- 実際に業務時間を50%削減した3つの方法
- 明日から始められる導入ステップ
```

2000文字以上の記事が自動生成されます。漢字率、文体一貫性、AI臭検出まで自動チェック。

### Xスレッド

```
1/6
AIを使ってるのに効率が上がらない人へ。
原因は「チャットボット止まり」だから。
エージェントAIに切り替えたら世界が変わった。具体的に3つ共有する🧵
```

6ツイートのスレッドが自動生成。各ツイートは280文字以内、最終ツイートにnote誘導CTA付き。

### ダッシュボード

![Dashboard](docs/dashboard-screenshot.png)

品質スコア、ファネルバランス、実行履歴を一覧表示。パイプライン完了時にブラウザで自動表示されます。

---

## インストール

```bash
# Claude Code内で実行
/plugin marketplace add FP-sudo/content-autopilot
/plugin install content-autopilot@content-autopilot

# これだけで動きます
/daily-autopilot
```

セットアップ不要。プロフィールは初回実行時に自動生成されます。

### ターミナルから直接確認する場合

```bash
git clone https://github.com/FP-sudo/content-autopilot.git
cd content-autopilot/plugins/content-autopilot/scripts
python3 run_pipeline.py    # パイプライン全体を実行
python3 test_scripts.py    # 23テスト全通過を確認
```

---

## 品質採点（6軸）

| 軸 | チェック内容 | 例 |
|---|---|---|
| フック | 冒頭で読者を掴めるか | 40文字以内の疑問・数字・意外性 |
| 可読性 | 段落長、文体一貫性 | 漢字率20-40%、です/ます体統一 |
| 構造 | 見出し・まとめセクション | 3-7個の##見出し |
| 適合性 | プラットフォーム別の要件 | note: 2000字以上、X: 280字/ツイート |
| CTA | 行動喚起の有無と強度 | フォロー誘導、次回予告 |
| AI臭 | AI特有のパターン検出 | 「本記事では」「さまざまな」等10パターン |

スコア75未満のコンテンツは**問題箇所を特定して自動修正**。人間に修正を求めません。

---

## コマンド

| コマンド | 機能 |
|---------|------|
| `/daily-autopilot` | 全自律パイプライン |
| `/setup-profile` | テーマ・文体カスタマイズ |
| `/trend-scout` | トレンドリサーチ |
| `/content-analytics` | コンテンツ分析 |
| `/deep-audit` | システム監査 |
| `/skills` | 全129スキル一覧 |

---

## 技術構成

```
plugins/content-autopilot/
├── skills/      129 SKILL.md
│   └── daily-autopilot: 380行の状態機械（8ステップ、エラー回復、進捗表示）
├── scripts/     12 Python scripts (3,800+ LOC)
│   ├── grader.py:        6軸採点 + 10パターンAI臭検出 + note.com推奨事項
│   ├── run_pipeline.py:  ANSIカラー付きデモ実行 + 自動改善ループ
│   ├── dashboard.py:     ダークテーマHTMLダッシュボード（CSSアニメーション）
│   └── ...               9 more scripts
├── commands/    7 slash commands
└── test_scripts.py: 23テスト
```

---

## License

MIT
