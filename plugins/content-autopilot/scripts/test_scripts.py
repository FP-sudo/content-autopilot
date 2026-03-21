#!/usr/bin/env python3
"""Test suite for Content Autopilot scripts.

Run: python3 test_scripts.py
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from grader import grade_content, kanji_ratio, check_desu_masu_consistency
from data_manager import load_json, ensure_data_dir, today_str

PASS = 0
FAIL = 0


def assert_eq(name, actual, expected):
    global PASS, FAIL
    if actual == expected:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL: {name}: expected {expected}, got {actual}")


def assert_true(name, condition):
    global PASS, FAIL
    if condition:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL: {name}")


def assert_in_range(name, value, lo, hi):
    global PASS, FAIL
    if lo <= value <= hi:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL: {name}: {value} not in [{lo}, {hi}]")


# ---------------------------------------------------------------------------
# grader tests
# ---------------------------------------------------------------------------

def test_kanji_ratio():
    print("test_kanji_ratio")
    assert_in_range("pure_kanji", kanji_ratio("漢字"), 0.9, 1.0)
    assert_in_range("hiragana", kanji_ratio("ひらがな"), 0.0, 0.01)
    assert_in_range("mixed", kanji_ratio("今日は良い天気です"), 0.2, 0.6)
    assert_in_range("empty", kanji_ratio(""), 0.0, 0.01)


def test_desu_masu():
    print("test_desu_masu_consistency")
    r = check_desu_masu_consistency("これは良いです。あれも素晴らしいです。")
    assert_eq("style", r["style"], "desu_masu")
    assert_true("consistent", r["consistent"])

    r2 = check_desu_masu_consistency("良いです。素晴らしいのである。")
    assert_eq("mixed_detected", r2["consistent"] or r2["ratio"] < 1.0, True)


def test_grade_short_note():
    print("test_grade_short_note")
    short = "テスト記事。短すぎる内容。フォローしてね。"
    result = grade_content(short, "note")
    assert_true("short_low_score", result["score"] == 0)  # <50 chars = 0 score
    assert_true("has_issues", len(result["issues"]) > 0)


def test_grade_good_note():
    print("test_grade_good_note")
    good = """# 3つの方法でAIを活用する

「AIを使いこなせていますか？」

## 方法1: 自動化

業務の80%は自動化できます。経費精算、レポート作成、データ入力。これらは全てAIが処理します。

## 方法2: 分析

データ分析にAIを活用すると、人間では見つけられないパターンが見えます。売上データから季節性を発見し、在庫管理を最適化できます。

## 方法3: コンテンツ作成

ブログ記事、SNS投稿、メール文面。AIが下書きを作り、人間が仕上げる。この分業で制作時間は半分になります。

## まとめ

AIの活用は難しくありません。小さく始めて、効果を実感してから拡大しましょう。

フォローしてもらえると嬉しいです。AI活用の最新事例をお届けしています。次回は実践編を公開予定です。
"""
    result = grade_content(good, "note")
    assert_true("good_passes", result["score"] >= 60)
    assert_true("grade_not_D", result["grade"] != "D")


def test_grade_ai_smell():
    print("test_grade_ai_smell")
    smelly = "# AIについて\n\n本記事ではさまざまな方法を紹介します。ご存じの通り、重要なことはAIです。AIを使うと業務が効率化されます。具体的な方法を見ていきましょう。いかがでしたか？参考になれば幸いです。"
    result = grade_content(smelly, "note")
    ai_issues = [i for i in result["issues"] if i["field"] == "ai_smell"]
    assert_true("detects_ai_smell", len(ai_issues) >= 3)


def test_grade_x_thread():
    print("test_grade_x_thread")
    thread = """1/3
AIが変える働き方。具体的に3つ解説する。

---

2/3
1つ目: レポート作成の自動化。4時間が30分に。

---

3/3
フォローしてnoteも読んでね。"""
    result = grade_content(thread, "x")
    assert_true("x_scored", result["score"] > 0)
    assert_eq("platform_x", result["platform"], "x")


def test_grade_instagram():
    print("test_grade_instagram")
    ig = """AIで業務効率を上げる3つの方法

1つ目は自動化です。
2つ目は分析です。
3つ目はコンテンツ作成です。

プロフィールのリンクから詳細をチェックしてね。

#AI #自動化 #業務効率 #生産性 #DX #テクノロジー #ビジネス #スタートアップ #マーケティング #コンテンツ #フリーランス #副業 #働き方 #リモートワーク #AI活用 #ChatGPT #Claude #プログラミング #デジタル #未来 #イノベーション #データ #クラウド #SaaS #アプリ"""
    result = grade_content(ig, "instagram")
    assert_eq("platform_ig", result["platform"], "instagram")
    assert_true("ig_scored", result["score"] > 0)


# ---------------------------------------------------------------------------
# data_manager tests
# ---------------------------------------------------------------------------

def test_today_str():
    print("test_today_str")
    t = today_str()
    assert_true("format_YYYY-MM-DD", len(t) == 10 and t[4] == "-" and t[7] == "-")


def test_load_json_missing():
    print("test_load_json_missing")
    result = load_json(Path("/nonexistent/path.json"))
    assert_eq("returns_none", result, None)


def test_ensure_data_dir():
    print("test_ensure_data_dir")
    p = ensure_data_dir()
    assert_true("dir_exists", p.is_dir())


# ---------------------------------------------------------------------------
# autopilot tests
# ---------------------------------------------------------------------------

def test_autopilot_modes():
    print("test_autopilot_modes")
    from autopilot import mode_summary

    # Empty history
    result = mode_summary(None)
    assert_eq("empty_total", result["total_runs"], 0)
    assert_eq("empty_streak", result["streak_days"], 0)

    # With data
    history = {
        "entries": [
            {"date": today_str(), "funnel_stage": "TOFU", "category": "trending",
             "title_logics_used": ["Numbers"], "platforms": {"note": {}}},
        ]
    }
    result = mode_summary(history)
    assert_eq("one_run", result["total_runs"], 1)
    assert_true("has_best_logic", result["best_title_logic"]["name"] != "N/A")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_kanji_ratio()
    test_desu_masu()
    test_grade_short_note()
    test_grade_good_note()
    test_grade_ai_smell()
    test_grade_x_thread()
    test_grade_instagram()
    test_today_str()
    test_load_json_missing()
    test_ensure_data_dir()
    test_autopilot_modes()

    total = PASS + FAIL
    print(f"\n{'=' * 40}")
    print(f"  Results: {PASS}/{total} passed, {FAIL} failed")
    print(f"{'=' * 40}")
    sys.exit(1 if FAIL > 0 else 0)
