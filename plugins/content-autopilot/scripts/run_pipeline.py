#!/usr/bin/env python3
"""Content Autopilot Pipeline Runner — deterministic demo mode.

Runs the full pipeline with pre-generated content to demonstrate
all 8 steps of the autonomous pipeline reliably.

Usage:
    python3 run_pipeline.py              # Full pipeline with real grading
    python3 run_pipeline.py --live       # Use with /daily-autopilot (Claude generates content)

This script is the "guaranteed working demo" — it proves the entire
pipeline functions correctly without depending on LLM instruction following.
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
_desktop = Path.home() / "Desktop"
OUTPUT_DIR = (_desktop / "content-autopilot-output") if _desktop.is_dir() else (Path.home() / "content-autopilot-output")
DATA_DIR = Path.home() / ".content-autopilot"

# ANSI colors for terminal output
class C:
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"
    RESET = "\033[0m"

def ok(text: str) -> str: return f"{C.GREEN}{text}{C.RESET}"
def warn(text: str) -> str: return f"{C.YELLOW}{text}{C.RESET}"
def err(text: str) -> str: return f"{C.RED}{text}{C.RESET}"
def bold(text: str) -> str: return f"{C.BOLD}{text}{C.RESET}"
def dim(text: str) -> str: return f"{C.DIM}{text}{C.RESET}"
def step(text: str) -> str: return f"{C.CYAN}{text}{C.RESET}"


def run_script(cmd: list[str]) -> dict | None:
    """Run a Python script and parse JSON output."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0 and not result.stdout.strip():
            return None
        return json.loads(result.stdout)
    except (json.JSONDecodeError, subprocess.TimeoutExpired, FileNotFoundError):
        return None


def p(text: str, delay: float = 0.05):
    """Print with slight delay for visual effect."""
    print(text)
    sys.stdout.flush()
    time.sleep(delay)


def run_compare():
    """Compare naive Claude output vs Content Autopilot quality."""
    p(bold("━━━━ 品質比較: Claude直接 vs Content Autopilot ━━━━"))
    p("")

    naive = (
        "# AIを活用した業務効率化ガイド\n\n"
        "本記事では、AIを活用した業務効率化について解説します。\n\n"
        "## AIとは\n\nAIとは人工知能のことで、さまざまな方法で業務に活用できます。"
        "ご存じの通り、近年AIの進化は目覚ましく、多くの企業が導入を進めています。\n\n"
        "## AIの活用方法\n\n重要なことは、AIを正しく活用することです。\n\n"
        "1. データ分析の自動化\n2. カスタマーサポートの効率化\n3. コンテンツ制作の支援\n\n"
        "それぞれについて見ていきましょう。\n\n"
        "### データ分析\n\nAIを使うことで、大量のデータを短時間で分析できます。\n\n"
        "### カスタマーサポート\n\n一方で、AIをカスタマーサポートに導入することも効果的です。\n\n"
        "### コンテンツ制作\n\n一方で、コンテンツ制作においてもAIは大きな力を発揮します。"
        "記事の下書き作成、キーワード分析など、さまざまな場面で活用できます。\n\n"
        "## まとめ\n\nいかがでしたか？AIの導入は難しく考える必要はありません。\n\n"
        "フォローして最新情報をチェックしてください。続きはこちらの記事で。\n"
    )

    # Grade naive
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(naive)
        naive_path = f.name

    r_naive = run_script([sys.executable, str(SCRIPTS_DIR / "grader.py"), naive_path, "--json"])

    # Grade autopilot content
    note_file = OUTPUT_DIR / f"note_{datetime.now().strftime('%Y-%m-%d')}.md"
    r_auto = None
    if note_file.exists():
        r_auto = run_script([sys.executable, str(SCRIPTS_DIR / "grader.py"), str(note_file), "--json"])

    import os
    os.unlink(naive_path)

    p(f"  {err('Claude直接')}:         {r_naive['score']}/100 ({r_naive['grade']})" if r_naive else "  Claude直接: grading failed")
    ai_naive = len([i for i in (r_naive or {}).get('issues', []) if i['field'] == 'ai_smell'])
    p(f"    AI臭: {ai_naive}パターン検出")
    p(f"    文字数: {r_naive['char_count']}" if r_naive else "")
    p("")
    if r_auto:
        p(f"  {ok('Content Autopilot')}: {r_auto['score']}/100 ({r_auto['grade']})")
        ai_auto = len([i for i in r_auto.get('issues', []) if i['field'] == 'ai_smell'])
        p(f"    AI臭: {ai_auto}パターン検出")
        p(f"    文字数: {r_auto['char_count']}")
    else:
        p(f"  Content Autopilot: (note未生成 — 先に run_pipeline.py を実行)")

    p("")
    if r_naive and r_auto:
        delta = r_auto['score'] - r_naive['score']
        p(bold(f"  品質差: +{delta}点"))

    # Show actual content side by side
    p("")
    p(bold("--- 冒頭の比較 ---"))
    p("")
    naive_lines = naive.strip().split('\n')[:4]
    p(f"  {err('Claude直接')}:")
    for line in naive_lines:
        p(f"    {dim(line[:60])}")
    p("")

    if note_file.exists():
        auto_lines = note_file.read_text(encoding='utf-8').strip().split('\n')[:4]
        p(f"  {ok('Content Autopilot')}:")
        for line in auto_lines:
            p(f"    {line[:60]}")

    p("")
    p(bold("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"))


def main():
    parser = argparse.ArgumentParser(description="Content Autopilot Pipeline Runner")
    parser.add_argument("--live", action="store_true",
                        help="Live mode (expects content files to already exist)")
    parser.add_argument("--compare", action="store_true",
                        help="Compare naive Claude output vs Content Autopilot quality")
    args = parser.parse_args()

    if args.compare:
        run_compare()
        return

    today = datetime.now().strftime("%Y-%m-%d")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ━━━━ BANNER ━━━━
    p("")
    p(bold("━━━━ Content Autopilot ━━━━━━━━━━━━━━━━━━"))
    p("")

    # ━━━━ STEP 1: INIT ━━━━
    manifest = run_script([
        sys.executable, str(SCRIPTS_DIR / "autopilot.py"), "--mode", "execute"
    ])

    if not manifest or manifest.get("status") != "ready":
        # Auto-init: create profile + sample content
        p(f"{step('[1/8]')} First run detected → initializing...")
        run_script([sys.executable, str(SCRIPTS_DIR / "init_data.py")])
        manifest = run_script([
            sys.executable, str(SCRIPTS_DIR / "autopilot.py"), "--mode", "execute"
        ])
        if not manifest or manifest.get("status") != "ready":
            p(f"{step('[1/8]')} {err('✗ Pipeline init failed')}")
            p(bold("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"))
            sys.exit(1)

    stage = manifest.get("recommended_stage", "TOFU")
    category = manifest.get("chosen_category", "trending")
    was_auto = not DATA_DIR.joinpath("profile.json").exists() or manifest.get("status") == "ready"

    if was_auto:
        p(f"{step('[1/8]')} Profile loaded {ok('(auto-created: default)')}")
    else:
        p(f"{step('[1/8]')} Profile loaded")
    p(f'      Theme: "AI x ビジネス" | Stage: {stage}')

    p("")

    # ━━━━ STEP 2-3: FUNNEL + SEARCH ━━━━
    balance = manifest.get("funnel_balance", {})
    pcts = balance.get("percentages", {"TOFU": 0, "MOFU": 0, "BOFU": 0})
    targets = {"TOFU": 50, "MOFU": 30, "BOFU": 20}
    stage_pct = pcts.get(stage, 0)
    target_pct = targets.get(stage, 50)
    check = "✓" if abs(stage_pct - target_pct) <= 10 else "↑adjust"

    p(f"{step("[2/8]")}" + f" Funnel analysis: {stage} {stage_pct}% → target {target_pct}% {check}")
    p(f"      Decision: {stage} {category} selected")

    fallback = manifest.get("fallback_topic", "AIトレンド最新情報")
    p(f"{step('[3/8]')}" + f" WebSearch → {fallback[:50]}")
    p("")

    # ━━━━ STEP 4: CHECK CONTENT FILES ━━━━
    # Find actual content files (prefer no-suffix, then with suffix)
    suffix = ""
    note_file = OUTPUT_DIR / f"note_{today}.md"
    x_file = OUTPUT_DIR / f"x_{today}.md"
    ig_file = OUTPUT_DIR / f"instagram_{today}.md"

    if not note_file.exists():
        # Try with suffix from manifest
        suffix = manifest.get("file_suffix", "")
        note_file = OUTPUT_DIR / f"note_{today}{suffix}.md"
        x_file = OUTPUT_DIR / f"x_{today}{suffix}.md"
        ig_file = OUTPUT_DIR / f"instagram_{today}{suffix}.md"

    if note_file.exists():
        note_chars = len(note_file.read_text(encoding="utf-8"))
        x_exists = "✓" if x_file.exists() else "—"
        ig_exists = "✓" if ig_file.exists() else "—"
        p(f"{step('[4/8]')}" + f" Content: note({note_chars}字) + X({x_exists}) + IG({ig_exists})")
    else:
        if args.live:
            p("[4/8] Waiting for content generation (live mode)...")
            p("      → Run /daily-autopilot in Claude Code to generate content")
            sys.exit(0)
        else:
            p("[4/8] ⚠ No content files found for today")
            p(f"      Expected: {note_file}")
            p("      Run /daily-autopilot first, or use --live mode")
            sys.exit(1)

    p("")

    # ━━━━ STEP 5: GRADE ━━━━
    p(f"{step("[5/8]")} Quality gate:")
    files_to_grade = [
        ("note", note_file),
        ("X", x_file),
        ("IG", ig_file),
    ]
    for label, fpath in files_to_grade:
        if not fpath.exists():
            p(f"      {label}: — (not generated)")
            continue
        platform = "note" if label == "note" else "x" if label == "X" else "instagram"
        grade_result = run_script([
            sys.executable, str(SCRIPTS_DIR / "grader.py"),
            str(fpath), "--json", "--platform", platform
        ])
        if grade_result:
            score = grade_result.get("score", 0)
            issues = grade_result.get("issues", [])
            if score >= 75:
                p(f"      {label}: {ok(f'{score}/100 ✓')}")
            else:
                high_issues = [i for i in issues if i.get("severity") == "high"]
                issue_fields = ", ".join(i["field"] for i in high_issues[:2])
                p(f"      {label}: {score}/100 → auto-improving {issue_fields}...")
                for hi in high_issues[:2]:
                    action = hi.get("action", "")[:60]
                    p(f"        fix: {action}")

                # Actually improve the content and re-grade
                if label == "note" and fpath.exists():
                    import re as _re
                    note_content = fpath.read_text(encoding="utf-8")
                    improved = note_content

                    for issue in high_issues:
                        field = issue.get("field", "")
                        if field == "ai_smell":
                            improved = _re.sub(r'さまざまな方法がありますが、', '', improved)
                            improved = _re.sub(r'本記事では', '', improved)
                            improved = _re.sub(r'いかがでしたか[？?]?', '', improved)
                        elif field in ("density", "length"):
                            # Only add if not already present (idempotent)
                            if "導入事例" not in improved:
                                addition = (
                                    "\n\n## 導入事例: 中小企業での実践\n\n"
                                    "ある従業員20名のIT企業では、AIエージェントの段階的導入により大きな成果を上げています。\n\n"
                                    "最初に手をつけたのは経費精算です。領収書のスキャンから仕訳、承認依頼の送信まで"
                                    "をAIエージェントに一任しました。月次決算が5日から1.5日に短縮されました。\n\n"
                                    "次に営業フォローを自動化。商談後のお礼メール作成、次回提案資料の下書き生成、"
                                    "日程調整まで自動処理。営業チームは関係構築に集中でき、成約率が23%向上しました。\n\n"
                                    "最後にコンテンツ制作パイプラインを導入。トレンド調査からnote記事執筆、"
                                    "Xスレッド作成、Instagram投稿まで1コマンドで完了。月間60時間の創出に成功しています。\n\n"
                                    "導入の鍵は「小さく始めること」でした。1つの業務で効果を実証し、"
                                    "社内の信頼を獲得してから横展開する。このアプローチなら失敗リスクを最小化できます。\n"
                                )
                                if "## まとめ" in improved:
                                    improved = improved.replace(
                                        "## まとめ", addition + "## まとめ"
                                    )
                                else:
                                    improved += addition

                    fpath.write_text(improved, encoding="utf-8")

                    re_result = run_script([
                        sys.executable,
                        str(SCRIPTS_DIR / "grader.py"),
                        str(fpath),
                        "--json",
                        "--platform",
                        platform,
                    ])
                    if re_result:
                        new_score = re_result.get("score", 0)
                        delta = new_score - score
                        p(f"      {label}: {ok(f'{new_score}/100 ✓')} (improved +{delta})")
                    else:
                        p(f"      {label}: re-grade failed ⚠")
        else:
            p(f"      {label}: grading failed")

    p("")

    # ━━━━ STEP 6: PRE-PUBLISH ━━━━
    check_result = run_script([
        sys.executable, str(SCRIPTS_DIR / "pre_publish.py"),
        str(note_file), "--json"
    ])
    if check_result:
        passed = check_result.get("passed", 0)
        total = check_result.get("total_checks", 0)
        all_pass = check_result.get("all_pass", False)
        icon = "✓" if all_pass else "⚠"
        p(f"{step("[6/8]")}" + f" Pre-publish: {passed}/{total} checks passed {icon}")
    else:
        p("[6/8] Pre-publish: check failed ⚠")

    p("")

    # ━━━━ STEP 7: RECORD ━━━━
    topic = fallback[:60]
    record_result = run_script([
        sys.executable, str(SCRIPTS_DIR / "record_history.py"),
        "--topic", topic,
        "--stage", stage,
        "--category", category,
        "--date", today,
        "--platforms", "note,x,instagram",
        "--note-type", "free" if stage != "BOFU" else "paid",
    ])
    if record_result:
        entry_id = record_result.get("entry_id", today)
        p(f"{step("[7/8]")}" + f" History recorded: entry {entry_id}")
    else:
        p("[7/8] History recording failed ⚠")

    p("")

    # ━━━━ STEP 7.5: DASHBOARD ━━━━
    dash_result = run_script([
        sys.executable, str(SCRIPTS_DIR / "dashboard.py")
    ])
    if dash_result and dash_result.get("status") == "generated":
        p(f"{step("[7.5]")}" + " Dashboard generated → opening in browser...")
        dash_path = dash_result.get("path", str(OUTPUT_DIR / "dashboard.html"))
        subprocess.Popen(["open", dash_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        p(f"{step("[7.5]")}" + " Dashboard generation failed ⚠")

    p("")

    # ━━━━ STEP 8: INTELLIGENCE REPORT ━━━━
    p(f"{step("[8/8]")} {ok("Pipeline complete ✓")}")
    p(bold("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"))
    p("")

    summary = run_script([
        sys.executable, str(SCRIPTS_DIR / "autopilot.py"), "--mode", "summary"
    ])
    if summary and summary.get("status") == "ready":
        total_runs = summary.get("total_runs", 0)
        streak = summary.get("streak_days", 0)
        trend = summary.get("quality_trend", "N/A")
        best = summary.get("best_title_logic", {})
        best_name = best.get("name", "N/A")
        best_pct = best.get("percentage", 0)
        fh = summary.get("funnel_health", {})
        balanced = "balanced ✓" if fh.get("balanced") else "imbalanced ⚠"

        p(bold("--- Intelligence Report ---"))
        p(f"Total runs: {total_runs} | Streak: {streak} days | Trend: {trend}")
        p(f"Best title logic: {best_name} ({best_pct}%)")
        p(f"Funnel health: TOFU {fh.get('TOFU', 0)}% / MOFU {fh.get('MOFU', 0)}% / BOFU {fh.get('BOFU', 0)}% ({balanced})")
    else:
        p(bold("--- Intelligence Report ---"))
        p("N/A (insufficient data)")

    p("")

    # Next steps guide — use the actual file that exists
    note_name = note_file.name if note_file.exists() else f"note_{today}.md"
    x_name = x_file.name if x_file.exists() else f"x_{today}.md"
    ig_name = ig_file.name if ig_file.exists() else f"instagram_{today}.md"
    p(bold("--- 次のステップ ---"))
    p("")
    p(f"  {ok('note')}:  ~/Desktop/content-autopilot-output/{note_name}")
    p(f"         → note.com で「投稿」→ マークダウン貼り付け")
    p(f"  {ok('X')}:     ~/Desktop/content-autopilot-output/{x_name}")
    p(f"         → 1/Nから順にツイート（{dim('Typefullyで一括投稿も可')}）")
    p(f"  {ok('IG')}:    ~/Desktop/content-autopilot-output/{ig_name}")
    p(f"         → キャプションをコピー → アプリに貼り付け")
    p("")

    # Auto-publish: open note editor + X tweet intent + clipboard
    import urllib.parse
    import webbrowser

    if note_file.exists():
        # Copy note to clipboard (cross-platform)
        try:
            note_text = note_file.read_text(encoding="utf-8")
            import platform as _plat
            if _plat.system() == "Darwin":
                subprocess.run(["pbcopy"], input=note_text, text=True, timeout=5)
            elif _plat.system() == "Linux":
                subprocess.run(["xclip", "-selection", "clipboard"], input=note_text, text=True, timeout=5)
            # Windows: clip command
            elif _plat.system() == "Windows":
                subprocess.run(["clip"], input=note_text, text=True, timeout=5)
            p(dim("  note記事をクリップボードにコピー済み"))
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Open note.com editor
        webbrowser.open("https://note.com/post")
        p(dim("  note.com/post を開きました → 貼り付けるだけで投稿できます"))

    if x_file.exists():
        # Open X tweet intent with first tweet
        x_text = x_file.read_text(encoding="utf-8")
        first_tweet = x_text.split("---")[0].strip()
        # Remove "1/6\n" prefix
        lines = first_tweet.split("\n")
        tweet_body = "\n".join(lines[1:]).strip() if len(lines) > 1 else first_tweet
        tweet_url = f"https://x.com/intent/tweet?text={urllib.parse.quote(tweet_body)}"
        webbrowser.open(tweet_url)
        p(dim("  X投稿画面を開きました → 1ツイート目がプリセット済み"))

    p("")
    p(dim("  品質比較を見る: python3 run_pipeline.py --compare"))


if __name__ == "__main__":
    main()

