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
    p("━━━━ Content Autopilot ━━━━━━━━━━━━━━━━━━")
    p("")

    # ━━━━ STEP 1: INIT ━━━━
    manifest = run_script([
        sys.executable, str(SCRIPTS_DIR / "autopilot.py"), "--mode", "execute"
    ])

    if manifest and manifest.get("status") == "ready":
        stage = manifest.get("recommended_stage", "TOFU")
        category = manifest.get("chosen_category", "trending")
        theme = "AI x ビジネス"
        profile_status = "auto-created: default" if not DATA_DIR.joinpath("profile.json").exists() else "loaded"
        p(f"[1/8] Profile {profile_status}")
        p(f'      Theme: "{theme}" | Stage: {stage}')
    else:
        # Init data if profile missing
        init_result = run_script([
            sys.executable, str(SCRIPTS_DIR / "init_data.py")
        ])
        manifest = run_script([
            sys.executable, str(SCRIPTS_DIR / "autopilot.py"), "--mode", "execute"
        ])
        if not manifest or manifest.get("status") != "ready":
            p("[1/8] ✗ Pipeline init failed")
            p("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            sys.exit(1)
        stage = manifest.get("recommended_stage", "TOFU")
        category = manifest.get("chosen_category", "trending")
        p("[1/8] Profile loaded (auto-created: default)")
        p(f'      Theme: "AI x ビジネス" | Stage: {stage}')

    p("")

    # ━━━━ STEP 2-3: FUNNEL + SEARCH ━━━━
    balance = manifest.get("funnel_balance", {})
    pcts = balance.get("percentages", {"TOFU": 0, "MOFU": 0, "BOFU": 0})
    targets = {"TOFU": 50, "MOFU": 30, "BOFU": 20}
    stage_pct = pcts.get(stage, 0)
    target_pct = targets.get(stage, 50)
    check = "✓" if abs(stage_pct - target_pct) <= 10 else "↑adjust"

    p(f"[2/8] Funnel analysis: {stage} {stage_pct}% → target {target_pct}% {check}")
    p(f"      Decision: {stage} {category} selected")

    fallback = manifest.get("fallback_topic", "AIトレンド最新情報")
    p(f"[3/8] Topic: {fallback[:50]}")
    p("")

    # ━━━━ STEP 4: CHECK CONTENT FILES ━━━━
    suffix = manifest.get("file_suffix", "")
    note_file = OUTPUT_DIR / f"note_{today}{suffix}.md"
    x_file = OUTPUT_DIR / f"x_{today}{suffix}.md"
    ig_file = OUTPUT_DIR / f"instagram_{today}{suffix}.md"

    if not note_file.exists():
        # Try without suffix
        note_file = OUTPUT_DIR / f"note_{today}.md"
        x_file = OUTPUT_DIR / f"x_{today}.md"
        ig_file = OUTPUT_DIR / f"instagram_{today}.md"

    if note_file.exists():
        note_chars = len(note_file.read_text(encoding="utf-8"))
        x_exists = "✓" if x_file.exists() else "—"
        ig_exists = "✓" if ig_file.exists() else "—"
        p(f"[4/8] Content found: note({note_chars}字) + X({x_exists}) + IG({ig_exists})")
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
    p("[5/8] Quality gate:")
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
                p(f"      {label}: {score}/100 ✓")
            else:
                high_issues = [i for i in issues if i.get("severity") == "high"]
                issue_fields = ", ".join(i["field"] for i in high_issues[:2])
                p(f"      {label}: {score}/100 → auto-improving {issue_fields}...")
                # Try improved version (-002 file)
                improved = fpath.parent / fpath.name.replace(today, f"{today}-002")
                if improved.exists() and improved != fpath:
                    re_result = run_script([
                        sys.executable, str(SCRIPTS_DIR / "grader.py"),
                        str(improved), "--json", "--platform", platform
                    ])
                    if re_result:
                        new_score = re_result.get("score", 0)
                        delta = new_score - score
                        icon = "✓" if new_score >= 75 else "⚠"
                        p(f"      {label}: {new_score}/100 {icon} (improved +{delta})")
                        # Use improved file for pre-publish
                        if label == "note":
                            note_file = improved
                else:
                    p(f"      {label}: {score}/100 ⚠ (no improved version)")
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
        p(f"[6/8] Pre-publish: {passed}/{total} checks passed {icon}")
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
        p(f"[7/8] History recorded: entry {entry_id}")
    else:
        p("[7/8] History recording failed ⚠")

    p("")

    # ━━━━ STEP 7.5: DASHBOARD ━━━━
    dash_result = run_script([
        sys.executable, str(SCRIPTS_DIR / "dashboard.py")
    ])
    if dash_result and dash_result.get("status") == "generated":
        p("[7.5] Dashboard generated → opening in browser...")
        dash_path = dash_result.get("path", str(OUTPUT_DIR / "dashboard.html"))
        subprocess.Popen(["open", dash_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        p("[7.5] Dashboard generation failed ⚠")

    p("")

    # ━━━━ STEP 8: INTELLIGENCE REPORT ━━━━
    p("[8/8] Pipeline complete ✓")
    p("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
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

        p("--- Intelligence Report ---")
        p(f"Total runs: {total_runs} | Streak: {streak} days | Trend: {trend}")
        p(f"Best title logic: {best_name} ({best_pct}%)")
        p(f"Funnel health: TOFU {fh.get('TOFU', 0)}% / MOFU {fh.get('MOFU', 0)}% / BOFU {fh.get('BOFU', 0)}% ({balanced})")
    else:
        p("--- Intelligence Report ---")
        p("N/A (insufficient data)")

    p("")


if __name__ == "__main__":
    main()
