#!/usr/bin/env python3
"""Initialize all data files for content-autopilot. Idempotent — safe to run multiple times.

Usage:
    python3 init_data.py
    python3 init_data.py --force   # Reset all data files (destructive)
"""

import sys
from pathlib import Path

# Allow importing data_manager from same directory
sys.path.insert(0, str(Path(__file__).parent))

from data_manager import (
    DATA_DIR, OUTPUT_DIR, PROFILE_PATH, HISTORY_PATH, SERIES_PATH,
    ensure_data_dir, ensure_output_dir, load_json, save_json, now_iso,
)

SAMPLE_HISTORY = {
    "version": "1.0",
    "entries": [
        {
            "id": "2026-03-19-001", "date": "2026-03-19",
            "topic": "リモートワーク効率化の5つの秘訣",
            "category": "trending", "funnel_stage": "TOFU",
            "platforms": {"note": {"title": "", "file": "", "type": "free", "char_count": 2200},
                          "x": {"title": "", "file": "", "format": "thread", "tweet_count": 6}},
            "title_logics_used": ["Numbers", "Simplicity"],
            "content_pillar": "Productivity", "source": "original", "series_id": None,
            "ab_titles": {"chosen": "", "alternative": "", "winner": None}
        },
        {
            "id": "2026-03-20-001", "date": "2026-03-20",
            "topic": "ChatGPT vs Claude — プロが教える使い分け",
            "category": "evergreen", "funnel_stage": "MOFU",
            "platforms": {"note": {"title": "", "file": "", "type": "free", "char_count": 3100},
                          "x": {"title": "", "file": "", "format": "thread", "tweet_count": 5},
                          "instagram": {"title": "", "file": "", "hashtag_count": 28}},
            "title_logics_used": ["Enemy", "Numbers"],
            "content_pillar": "AI Tools", "source": "original", "series_id": None,
            "ab_titles": {"chosen": "", "alternative": "", "winner": None}
        },
    ]
}
EMPTY_HISTORY = {"version": "1.0", "entries": []}

EMPTY_SERIES = {"version": "1.0", "series": []}

SAMPLE_PROFILE = {
    "version": "1.0",
    "created_at": None,
    "updated_at": None,
    "theme": {
        "main": "AI x ビジネス",
        "keywords": ["AI", "自動化", "生産性", "ビジネス", "効率化"],
    },
    "audience": {
        "age_range": "25-45",
        "occupation": "ビジネスパーソン・個人事業主",
        "pain_points": ["時間が足りない", "AIの活用方法がわからない", "業務効率を上げたい"],
        "knowledge_level": "intermediate",
    },
    "platforms": ["note", "x", "instagram"],
    "style": {
        "method": "preset",
        "preset": "professional",
        "tone": "authoritative yet approachable",
        "sentence_length": "medium",
        "vocabulary": "accessible technical terms",
        "paragraph_style": "short paragraphs with line breaks",
        "emoji_usage": "minimal",
        "first_person": True,
        "sample_urls": [],
    },
    "brand": {
        "primary_color": "#FF6B35",
        "secondary_color": "#1A1A2E",
        "logo_path": None,
        "font_preference": None,
    },
    "funnel": {
        "enabled": False,
        "note_url": "",
        "x_handle": "",
        "instagram_handle": "",
        "monetization": {
            "type": "paid_articles",
            "lead_magnet": "",
            "membership_url": None,
            "lead_magnet_url": None,
        },
    },
    "competitors": [],
}



SAMPLE_NOTE = """# 3つのAI活用法で業務時間を半分にした話

「AIを使ってるのに、なぜ効率が上がらないのか？」

**この記事でわかること**
- チャットボットとAIエージェントの決定的な違い
- 実際に業務時間を50%削減した3つの方法
- 明日から始められる導入ステップ

そう感じたことはありませんか。ChatGPTに質問して、回答を読んで、また質問する。このサイクルを繰り返していると、ある疑問が浮かんできます。

「これ、本当に効率化できているのか？」

答えはNoです。断言できます。チャットボットに質問するだけでは、作業の主導権は人間のまま。本当の効率化は、AIが自律的に動く「エージェント」を活用することで初めて実現します。

---

## なぜチャットボットでは不十分なのか？

チャットボットは「聞かれたら答える」ツールです。人間が質問を考え、プロンプトを書き、回答を読む。すべてのステップに人間の判断が必要です。AIを使っているようでいて、作業量はほとんど減っていないのです。

一方、AIエージェントは「ゴールを与えると自分で考えて実行する」存在です。プロセスの途中の判断はすべてエージェントが自律的に行います。

この違いは小さく見えて、1タスクあたり30分から2時間の差を生みます。1日に5つのタスクがあれば、月間で50時間以上の差になります。

年間に換算すると約600時間。フルタイム勤務の約3.5ヶ月分に相当します。この差を放置すると、競合との生産性格差は開く一方です。

---

## 実際に効果があった3つの活用法

### 1. 日次レポートの完全自動化

毎朝30分かけていた売上レポートの作成をAIエージェントに任せました。データの収集、グラフの生成、Slackへの投稿まで自動。人間がやるのは異常値のチェックだけです。

導入前: 毎朝30分 × 20営業日 = 月10時間
導入後: 異常値チェック5分 × 20営業日 = 月1.7時間
削減効果: 月8.3時間

### 2. カスタマーサポートの一次対応

問い合わせの70%は定型的な質問です。AIエージェントが感情分析を行い、定型質問は自動回答、複雑な案件だけ人間にエスカレーション。

導入前: サポート担当2名がフル対応
導入後: 1名が複雑案件のみ対応、もう1名はプロダクト改善に注力
顧客満足度: 85% → 92%に向上

### 3. コンテンツ制作のパイプライン化

トレンド調査、記事執筆、SNS投稿の書き分けを一つのパイプラインで自動化。1日3時間かかっていた作業が15分のレビューだけになりました。

noteの記事品質も安定しました。以前は疲れた日に質が落ちていましたが、6軸の品質採点で常に一定水準を維持できるようになっています。フック、読みやすさ、構造、プラットフォーム適合、CTA、AI臭検出の6つの観点で自動チェックされるため、人間が見落としがちなポイントも漏れません。

---

## 導入で失敗しないための3ステップ

### ステップ1: 繰り返しタスクを3つ選ぶ

月曜朝に30分だけ時間を取り、先週の業務を振り返ります。「毎回同じ手順でやっていること」がAIエージェント化の最有力候補です。具体的には、日次の売上集計、定型メールの返信、会議議事録の作成、SNS投稿のスケジューリングなどが典型的な候補になります。

### ステップ2: 1つだけ2週間試す

いきなり全業務を自動化しようとすると失敗します。まず1つのタスクに絞り、効果を数値で測定しましょう。時間短縮30%以上なら本格導入の価値があります。測定すべき指標は、作業時間の変化、エラー率の変化、アウトプットの品質の3つです。この3つさえ追えば、投資対効果の判断ができます。

### ステップ3: 段階的に自律性を上げる

最初は「人間が確認してから実行」のモード。信頼が蓄積されたら「自動実行 + 異常時のみ通知」に移行。この段階的アプローチが失敗リスクを最小化します。成功企業は例外なく、このステップを踏んでいます。いきなり全社展開して失敗するケースの大半は、この段階的アプローチを飛ばしたことが原因です。

---

## まとめ

AIの活用は「質問する」から「任せる」へ進化しています。まずは1つの繰り返しタスクから始めてみてください。小さく始めて、効果を実感してから拡大する。これが成功への鉄則です。

AIエージェントは「便利なツール」ではなく「自律的なチームメンバー」です。最初の1歩を踏み出すかどうかが、1年後の業務効率を大きく左右します。

フォローしていただけると、AI活用の最新事例をお届けします。次回は「AIエージェント導入で失敗する3つのパターン」を公開予定です。
"""

SAMPLE_X = """1/6
AIを使ってるのに効率が上がらない人へ。
原因は「チャットボット止まり」だから。
エージェントAIに切り替えたら世界が変わった。具体的に3つ共有する🧵

---

2/6
①日次レポートの完全自動化
データ収集→グラフ生成→Slack投稿まで全自動。
人間がやるのは異常値チェックだけ。
月10時間の削減。

---

3/6
②カスタマーサポートの一次対応
問い合わせの70%は定型質問。
AIが感情分析→定型は自動回答→複雑案件だけ人間へ。
対応速度3倍、満足度92%。

---

4/6
③コンテンツ制作のパイプライン化
トレンド調査→記事執筆→SNS書き分けを全自動化。
1日3時間→15分のレビューだけ。
週15時間の創出。

---

5/6
共通するポイントは「小さく始める」こと。
いきなり全社導入は失敗する。
1つのタスクで2週間試して、効果を数字で確認。

---

6/6
あなたはAIに「質問する」派？「任せる」派？
リプで教えてください。

導入ステップはnoteで詳しく解説しています。
プロフィールのリンクからどうぞ。
"""

SAMPLE_IG = """AIを使っても効率が上がらない本当の理由、知っていますか？

チャットボットに質問するだけでは、作業の主導権は人間のまま。
本当の効率化は「AIエージェント」で実現する。

実際に効果があった3つの方法:

📊 日次レポート自動化 → 月10時間削減
🤝 サポート一次対応 → 対応速度3倍
📝 コンテンツ制作 → 1日3時間→15分

まずは1つの繰り返しタスクから始めてみてください。
詳しくはプロフィールのリンクからnote記事をチェックしてください👆

#AI #AIエージェント #業務効率化 #自動化 #DX #生産性向上 #働き方改革 #ChatGPT #Claude #AIビジネス #リモートワーク #テクノロジー #スタートアップ #フリーランス #副業 #マーケティング #コンテンツマーケティング #デジタルマーケティング #ビジネス成長 #AI活用 #プログラミング #データ分析 #クラウド #SaaS #イノベーション #未来の働き方 #ビジネスハック #経営者 #個人事業主 #note
"""


def init_file(path: Path, default_data: dict, force: bool = False) -> str:
    """Initialize a data file if it doesn't exist. Returns status message."""
    if path.exists() and not force:
        return f"  EXISTS  {path.name}"
    save_json(path, default_data)
    action = "RESET" if force else "CREATED"
    return f"  {action}  {path.name}"


def main():
    force = "--force" in sys.argv

    print("=" * 50)
    print("  Content Autopilot — Data Initialization")
    print("=" * 50)
    print()

    # Create directories
    ensure_data_dir()
    ensure_output_dir()
    print(f"  Data dir:   {DATA_DIR}")
    print(f"  Output dir: {OUTPUT_DIR}")
    print()

    # Initialize data files
    print("Data files:")

    if not PROFILE_PATH.exists():
        ts = now_iso()
        sample = {**SAMPLE_PROFILE, "created_at": ts, "updated_at": ts}
        print(init_file(PROFILE_PATH, sample, force))
        print("    NOTE: Run /setup-profile to configure your profile")
    elif force:
        ts = now_iso()
        sample = {**SAMPLE_PROFILE, "created_at": ts, "updated_at": ts}
        print(init_file(PROFILE_PATH, sample, force))
    else:
        print(f"  EXISTS  {PROFILE_PATH.name}")

    print(init_file(HISTORY_PATH, SAMPLE_HISTORY, force))
    print(init_file(SERIES_PATH, EMPTY_SERIES, force))

    # Create sample content files if they don't exist
    if True:
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        note_path = OUTPUT_DIR / f"note_{today}.md"
        x_path = OUTPUT_DIR / f"x_{today}.md"
        ig_path = OUTPUT_DIR / f"instagram_{today}.md"
        
        if not note_path.exists() or force:
            note_path.write_text(SAMPLE_NOTE, encoding="utf-8")
            print(f"  CREATED  note_{today}.md (sample content)")
        if not x_path.exists() or force:
            x_path.write_text(SAMPLE_X, encoding="utf-8")
            print(f"  CREATED  x_{today}.md (sample content)")
        if not ig_path.exists() or force:
            ig_path.write_text(SAMPLE_IG, encoding="utf-8")
            print(f"  CREATED  instagram_{today}.md (sample content)")

    print()
    print("Initialization complete.")
    if force:
        print("WARNING: --force was used. All data files have been reset.")
    print()
    print("Next steps:")
    print("  Run /daily-autopilot to generate content")
    if not PROFILE_PATH.exists() or force:
        print("  (Optional: Run /setup-profile to customize your profile)")
    print("=" * 50)


if __name__ == "__main__":
    main()
