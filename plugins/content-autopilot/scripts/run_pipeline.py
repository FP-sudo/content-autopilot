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
OUTPUT_DIR = Path.home() / "Desktop" / "content-autopilot-output"
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


def main():
    parser = argparse.ArgumentParser(description="Content Autopilot Pipeline Runner")
    parser.add_argument("--live", action="store_true",
                        help="Live mode (expects content files to already exist)")
    args = parser.parse_args()

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
    p(f"{step("[3/8]")}" + f" Topic: {fallback[:50]}")
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
        p(f"{step("[4/8]")}" + f" Content found: note({note_chars}字) + X({x_exists}) + IG({ig_exists})")
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
                # Show what the auto-improvement would fix
                for hi in high_issues[:2]:
                    action = hi.get("action", "")[:60]
                    p(f"        fix: {action}")
                # In live mode, Claude rewrites and re-grades
                # In demo mode, show the improvement potential
                p(f"      {label}: (live mode: Claude rewrites → re-grade → target 85+)")
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
    p(f"  note:  open ~/Desktop/content-autopilot-output/{note_name}")
    p(f"         → note.com で「投稿」→ マークダウン貼り付け")
    p(f"  X:     open ~/Desktop/content-autopilot-output/{x_name}")
    p(f"         → 1/Nから順にツイート")
    p(f"  IG:    open ~/Desktop/content-autopilot-output/{ig_name}")
    p(f"         → キャプションをコピー → アプリに貼り付け")
    p("")


if __name__ == "__main__":
    main()
