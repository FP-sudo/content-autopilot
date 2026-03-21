<h1 align="center">Content Autopilot</h1>

<p align="center">
<strong>1コマンドで、note・X・Instagramのコンテンツを自律生成する</strong>
</p>

<p align="center">
Claude Code プラグイン | 12 Python scripts | 品質自動採点 | HTMLダッシュボード
</p>

---

## やること

`/daily-autopilot` を1回実行するだけ。あとはシステムが全て自律的に処理します:

```
━━━━ Content Autopilot ━━━━━━━━━━━━━━━━━━
[1/8] Profile loaded (auto-created: default)
[2/8] Funnel: MOFU 0% → target 30% ↑adjust
[3/8] WebSearch → AIエージェントで業務を自律化
[4/8] Content: note(2,500字) + X(6tweets) + IG
[5/8] Quality gate:
      note: 72/100 → auto-improving density...
      note: 82/100 ✓ (improved +10)
[6/8] Pre-publish: 8/8 checks passed ✓
[7/8] Dashboard → browser auto-open
[8/8] Pipeline complete ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

> ハッカソンテーマ「一度命じたら、あとは任せろ」— 7つの判断（トピック選択、品質改善、フォールバック、ファネルバランス、重複回避、シリーズ継続、プロフィール自動生成）をシステムが自律的に行います。

---

## 実際に生成されるコンテンツ

### note記事（冒頭）

```
# 3つのAI活用法で業務時間を半分にした話

「AIを使ってるのに、なぜ効率が上がらないのか？」

**この記事でわかること**
- チャットボットとAIエージェントの決定的な違い
- 実際に業務時間を50%削減した3つの方法
- 明日から始められる導入ステップ
```

### Xスレッド（1ツイート目）

```
1/6
AIを使ってるのに効率が上がらない人へ。
原因は「チャットボット止まり」だから。
エージェントAIに切り替えたら世界が変わった。具体的に3つ共有する🧵
```

### 品質ダッシュボード

![Dashboard](docs/dashboard-screenshot.png)

---

## インストール

```bash
/plugin marketplace add FP-sudo/content-autopilot
/plugin install content-autopilot@content-autopilot
/daily-autopilot
```

セットアップ不要。プロフィールは自動生成されます。

ターミナルから直接確認する場合:
```bash
git clone https://github.com/FP-sudo/content-autopilot.git
cd content-autopilot/plugins/content-autopilot/scripts
python3 run_pipeline.py    # パイプライン全体を実行
python3 test_scripts.py    # 23テスト全通過を確認
```

---

## 品質ゲート

生成コンテンツは6軸で自動採点されます:

| 軸 | チェック内容 |
|---|---|
| Hook | 冒頭で読者を掴めるか |
| Readability | 段落長、文体一貫性、漢字率 |
| Structure | 見出し構成、まとめセクション |
| Platform Fit | プラットフォーム別の文字数・形式 |
| CTA | 行動喚起の有無 |
| AI Smell | AI生成テキスト特有のパターン検出 |

スコア75未満 → 問題箇所を特定し自動改善（最大2ラウンド）。

---

## 使えるコマンド

| コマンド | 機能 |
|---------|------|
| `/daily-autopilot` | 全自律パイプライン実行 |
| `/setup-profile` | テーマ・文体カスタマイズ |
| `/trend-scout` | トレンドリサーチ |
| `/content-analytics` | 分析ダッシュボード |
| `/deep-audit` | システム整合性チェック |
| `/skills` | 全スキル一覧表示 |

---

## アーキテクチャ

```
plugins/content-autopilot/
├── skills/      129 SKILL.md（パイプライン制御、コンテンツ生成、分析等）
├── scripts/     12 Python scripts（品質採点、ダッシュボード、履歴管理等）
└── commands/    7 slash commands
```

---

## 生成コンテンツの使い方

1. **note**: ファイルを開き、note.comの投稿画面にマークダウンを貼り付け
2. **X**: 各ツイートを1/Nから順に投稿（`---`で区切り済み）
3. **Instagram**: キャプションをコピー → アプリに貼り付け（ハッシュタグ30個配置済み）

パイプライン完了時にnote記事は自動でクリップボードにコピーされます。

---

## Demo Video

> [撮影ガイド](./DEMO_SCRIPT.md) — ナレーション台本・操作手順

---

## License

MIT
