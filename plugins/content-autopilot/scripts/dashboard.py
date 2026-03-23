#!/usr/bin/env python3
"""Content Autopilot Dashboard — generate an HTML dashboard for content performance.

Generates a single-file HTML dashboard with zero external dependencies.
Dark theme, CSS Grid, responsive layout.  All styling is inlined so the
output file can be opened directly in any browser without a server.

Usage:
    python3 dashboard.py              # dashboard for today
    python3 dashboard.py --date 2026-03-15  # dashboard for specific date
"""

import argparse
import json
import sys
import webbrowser
from datetime import datetime, timedelta
from html import escape
from pathlib import Path

# Allow importing sibling module (grader.py)
sys.path.insert(0, str(Path(__file__).parent))
from grader import detect_platform, grade_content


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_desktop = Path.home() / "Desktop"
OUTPUT_BASE = (_desktop / "content-autopilot-output") if _desktop.is_dir() else (Path.home() / "content-autopilot-output")
CONFIG_DIR = Path.home() / ".content-autopilot"
HISTORY_FILE = CONFIG_DIR / "content-history.json"
PROFILE_FILE = CONFIG_DIR / "profile.json"


def _output_dir_for_date(date_str: str) -> Path:
    """Return date-specific output directory (e.g. .../2026-03-23/)."""
    return OUTPUT_BASE / date_str


# ---------------------------------------------------------------------------
# Data loaders (all return safe defaults on missing/corrupt files)
# ---------------------------------------------------------------------------


def load_json(path: Path) -> dict | list | None:
    """Load a JSON file, returning None on any failure."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def load_profile() -> tuple[dict, bool]:
    """Return (profile_dict, is_default)."""
    data = load_json(PROFILE_FILE)
    if data is None:
        return {}, True
    # Heuristic: a default profile has the generic theme "AI x business"
    # and no sample_urls.  Adjust if the default template changes.
    is_default = (
        data.get("style", {}).get("method") == "preset"
        and not data.get("style", {}).get("sample_urls")
    )
    return data, is_default


def load_history() -> list[dict]:
    """Return the entries list from content-history.json."""
    data = load_json(HISTORY_FILE)
    if isinstance(data, dict):
        return data.get("entries", [])
    if isinstance(data, list):
        return data
    return []


def read_content_file(path: Path) -> str | None:
    """Read a content file, returning None on failure."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


# ---------------------------------------------------------------------------
# Content discovery
# ---------------------------------------------------------------------------

PLATFORM_PREFIXES = [
    ("note", "note_{date}.md"),
    ("x", "x_{date}.md"),
    ("instagram", "instagram_{date}.md"),
]


def discover_content(date_str: str) -> list[dict]:
    """Find generated content files for a given date and grade them.

    Looks in the date subfolder first, then falls back to the flat base directory
    for backward compatibility with older runs.

    Returns a list of dicts:
        {"platform": str, "path": Path|None, "content": str|None, "grade": dict|None}
    """
    date_dir = _output_dir_for_date(date_str)
    results = []
    for platform, pattern in PLATFORM_PREFIXES:
        filename = pattern.format(date=date_str)
        # Try date subfolder first, then flat base dir (backward compat)
        path = date_dir / filename
        content = read_content_file(path)
        if content is None:
            path = OUTPUT_BASE / filename
            content = read_content_file(path)
        grade = None
        if content is not None:
            grade = grade_content(content, platform)
        results.append({
            "platform": platform,
            "path": path if content is not None else None,
            "content": content,
            "grade": grade,
        })
    return results


# ---------------------------------------------------------------------------
# Analytics helpers
# ---------------------------------------------------------------------------


def last_n_entries(history: list[dict], n: int) -> list[dict]:
    """Return the last *n* history entries sorted by date descending."""
    sorted_entries = sorted(history, key=lambda e: e.get("date", ""), reverse=True)
    return sorted_entries[:n]


def funnel_distribution(history: list[dict]) -> dict[str, int]:
    """Count TOFU / MOFU / BOFU occurrences."""
    counts: dict[str, int] = {"TOFU": 0, "MOFU": 0, "BOFU": 0}
    for entry in history:
        stage = entry.get("funnel_stage", "").upper()
        if stage in counts:
            counts[stage] += 1
    return counts


def intelligence_report(history: list[dict], graded: list[dict]) -> dict:
    """Compute aggregate intelligence metrics."""
    total_runs = len(history)

    # Quality scores from graded content (today only)
    scores = [g["grade"]["score"] for g in graded if g.get("grade")]
    avg_quality = round(sum(scores) / len(scores), 1) if scores else 0

    # Trend: compare last 3 entries with previous 3
    recent = last_n_entries(history, 6)
    recent_scores: list[float] = []
    for entry in recent:
        platforms = entry.get("platforms", {})
        for plat_data in platforms.values():
            cc = plat_data.get("char_count")
            if cc and cc > 0:
                recent_scores.append(cc)  # proxy when no stored score

    # Title logic frequency
    logic_counts: dict[str, int] = {}
    for entry in history:
        for logic in entry.get("title_logics_used", []):
            logic_counts[logic] = logic_counts.get(logic, 0) + 1
    most_used_logic = max(logic_counts, key=logic_counts.get) if logic_counts else "N/A"

    # Simple trend indicator based on posting frequency
    from datetime import timedelta
    if len(history) >= 2:
        cutoff_recent = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        cutoff_prior = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
        recent_count = sum(1 for e in history if e.get("date", "") >= cutoff_recent)
        prior_count = sum(1 for e in history if cutoff_prior <= e.get("date", "") < cutoff_recent)
        if recent_count > prior_count:
            trend = "improving"
        elif recent_count == prior_count:
            trend = "stable"
        else:
            trend = "declining"
    else:
        trend = "insufficient data"

    # Streak calculation
    from datetime import date as date_cls
    unique_dates = sorted({e.get("date", "") for e in history if e.get("date")}, reverse=True)
    streak = 0
    check = date_cls.today()
    for d in unique_dates:
        try:
            entry_date = date_cls.fromisoformat(d)
        except ValueError:
            continue
        if entry_date == check:
            streak += 1
            check -= timedelta(days=1)
        elif entry_date < check:
            break
    if streak == 0 and unique_dates:
        check = date_cls.today() - timedelta(days=1)
        for d in unique_dates:
            try:
                entry_date = date_cls.fromisoformat(d)
            except ValueError:
                continue
            if entry_date == check:
                streak += 1
                check -= timedelta(days=1)
            elif entry_date < check:
                break

    return {
        "total_runs": total_runs,
        "avg_quality": avg_quality,
        "trend": trend,
        "most_used_logic": most_used_logic,
        "streak": streak,
    }


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------


def score_color(score: int) -> str:
    """Return CSS colour for a quality score."""
    if score >= 85:
        return "#3fb950"
    if score >= 75:
        return "#d29922"
    return "#f85149"


def truncate(text: str, limit: int = 300) -> str:
    """Truncate text to *limit* characters, adding ellipsis if needed."""
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def build_content_card(item: dict) -> str:
    """Build an HTML card for a single platform's content."""
    platform = escape(item["platform"])
    platform_labels = {"note": "Note", "x": "X (Twitter)", "instagram": "Instagram"}
    label = platform_labels.get(platform, platform)

    if item["content"] is None:
        return f"""
        <div class="card card--empty">
          <h3>{label}</h3>
          <p class="placeholder">未生成</p>
        </div>"""

    preview = escape(truncate(item["content"]))
    grade = item["grade"] or {}
    score = grade.get("score", 0)
    grade_letter = grade.get("grade", "?")
    color = score_color(score)

    return f"""
    <div class="card">
      <div class="card-header">
        <h3>{label}</h3>
        <span class="badge" style="background:{color}">{grade_letter} ({score})</span>
      </div>
      <pre class="preview">{preview}</pre>
    </div>"""


def build_score_bars(graded: list[dict]) -> str:
    """Build CSS-only bar charts for category scores."""
    rows = []
    for item in graded:
        if item["grade"] is None:
            continue
        platform = escape(item["platform"])
        cat_scores = item["grade"].get("category_scores", {})
        for category, raw_score in cat_scores.items():
            pct = min(100, max(0, raw_score * 10))
            color = score_color(int(pct))
            # Custom labels for better readability
            label_map = {
                "hook": "Hook", "readability": "Readability", "structure": "Structure",
                "platform_fit": "Platform Fit", "cta": "CTA", "ai_smell": "AI Smell",
            }
            cat_label = escape(label_map.get(category, category.replace("_", " ").title()))
            rows.append(f"""
            <div class="bar-row">
              <span class="bar-label">{platform} / {cat_label}</span>
              <div class="bar-track">
                <div class="bar-fill" style="width:{pct}%;background:{color}"></div>
              </div>
              <span class="bar-value">{raw_score}/10</span>
            </div>""")
    return "\n".join(rows) if rows else '<p class="placeholder">スコアデータなし</p>'


def build_funnel_chart(distribution: dict[str, int]) -> str:
    """Build a horizontal stacked bar for funnel balance."""
    total = sum(distribution.values()) or 1
    targets = {"TOFU": 50, "MOFU": 30, "BOFU": 20}
    colors = {"TOFU": "#58a6ff", "MOFU": "#d29922", "BOFU": "#f85149"}

    actual_bars = ""
    target_bars = ""
    for stage in ("TOFU", "MOFU", "BOFU"):
        actual_pct = round(distribution.get(stage, 0) / total * 100, 1)
        target_pct = targets[stage]
        color = colors[stage]
        actual_bars += (
            f'<div class="funnel-seg" style="width:{actual_pct}%;background:{color}">'
            f"{stage} {actual_pct}%</div>\n"
        )
        target_bars += (
            f'<div class="funnel-seg funnel-seg--target" style="width:{target_pct}%;background:{color}80">'
            f"{stage} {target_pct}%</div>\n"
        )

    return f"""
    <div class="funnel-group">
      <p class="funnel-label">Actual</p>
      <div class="funnel-bar">{actual_bars}</div>
    </div>
    <div class="funnel-group">
      <p class="funnel-label">Target</p>
      <div class="funnel-bar">{target_bars}</div>
    </div>"""


def build_history_table(entries: list[dict]) -> str:
    """Build an HTML table from history entries."""
    if not entries:
        return '<p class="placeholder">履歴データなし</p>'

    rows = ""
    for entry in entries:
        date = escape(entry.get("date", ""))
        topic = escape(entry.get("topic", ""))
        stage = escape(entry.get("funnel_stage", ""))
        category = escape(entry.get("category", ""))
        rows += f"""
        <tr>
          <td>{date}</td>
          <td>{topic}</td>
          <td>{stage}</td>
          <td>{category}</td>
        </tr>"""

    return f"""
    <table>
      <thead>
        <tr><th>Date</th><th>Topic</th><th>Stage</th><th>Category</th></tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>"""


def build_html(
    date_str: str,
    graded: list[dict],
    history: list[dict],
    profile: dict,
    is_default_profile: bool,
) -> str:
    """Assemble the complete dashboard HTML."""

    content_cards = "\n".join(build_content_card(item) for item in graded)
    score_bars = build_score_bars(graded)
    funnel = build_funnel_chart(funnel_distribution(history))
    history_table = build_history_table(last_n_entries(history, 7))
    intel = intelligence_report(history, graded)

    trend_icon = {
        "improving": "&#9650;",   # up triangle
        "stable": "&#8594;",      # right arrow
        "declining": "&#9660;",   # down triangle
        "insufficient data": "&#8212;",  # em dash
    }.get(intel["trend"], "&#8212;")

    trend_color = {"improving": "#3fb950", "stable": "#c9d1d9", "declining": "#f85149"}.get(intel["trend"], "#c9d1d9")

    streak_color = "#3fb950" if intel["streak"] >= 3 else "#c9d1d9" if intel["streak"] >= 1 else "#f85149"

    profile_banner = ""
    if is_default_profile:
        profile_banner = """
    <div class="banner">
      &#128161; /setup-profile でテーマをカスタマイズできます
    </div>"""

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Content Autopilot Dashboard — {escape(date_str)}</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{font-size:16px}}
body{{
  font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  background:#0d1117;
  color:#c9d1d9;
  line-height:1.6;
  padding:2rem;
  min-width:320px;
}}
a{{color:#58a6ff;text-decoration:none}}
a:hover{{text-decoration:underline}}

/* Layout */
.container{{
  max-width:1200px;
  margin:0 auto;
  display:grid;
  gap:1.5rem;
}}
.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem}}
.grid-3{{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem}}
@media(max-width:900px){{
  .grid-2,.grid-3{{grid-template-columns:1fr}}
}}

/* Header */
.header{{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding:1.5rem 2rem;
  background:#161b22;
  border-radius:12px;
  border:1px solid #30363d;
}}
.header h1{{font-size:1.5rem;color:#e6edf3;font-weight:700}}
.header .date{{color:#8b949e;font-size:0.95rem}}

/* Banner */
.banner{{
  background:#161b2280;
  border:1px solid #30363d;
  border-radius:8px;
  padding:0.75rem 1.25rem;
  font-size:0.9rem;
  color:#8b949e;
  text-align:center;
}}

/* Section */
.section{{
  background:#161b22;
  border:1px solid #30363d;
  border-radius:12px;
  padding:1.5rem;
}}
.section h2{{
  font-size:1.1rem;
  color:#e6edf3;
  margin-bottom:1rem;
  padding-bottom:0.5rem;
  border-bottom:1px solid #21262d;
}}

/* Cards */
.card{{
  background:#0d1117;
  border:1px solid #30363d;
  border-radius:10px;
  padding:1.25rem;
  display:flex;
  flex-direction:column;
  gap:0.75rem;
}}
.card--empty{{opacity:0.5}}
.card-header{{
  display:flex;
  justify-content:space-between;
  align-items:center;
}}
.card h3{{font-size:1rem;color:#e6edf3}}
.badge{{
  display:inline-block;
  padding:0.2rem 0.6rem;
  border-radius:6px;
  font-size:0.8rem;
  font-weight:700;
  color:#0d1117;
}}
.preview{{
  font-size:0.85rem;
  color:#8b949e;
  white-space:pre-wrap;
  word-break:break-word;
  max-height:200px;
  overflow-y:auto;
  background:#161b22;
  border-radius:6px;
  padding:0.75rem;
  font-family:inherit;
  line-height:1.5;
}}
.placeholder{{
  color:#484f58;
  font-style:italic;
  text-align:center;
  padding:2rem 0;
}}

/* Score bars */
.bar-row{{
  display:grid;
  grid-template-columns:180px 1fr 60px;
  gap:0.75rem;
  align-items:center;
  margin-bottom:0.4rem;
}}
.bar-label{{
  font-size:0.8rem;
  color:#8b949e;
  text-align:right;
  white-space:nowrap;
  overflow:hidden;
  text-overflow:ellipsis;
}}
.bar-track{{
  height:18px;
  background:#21262d;
  border-radius:9px;
  overflow:hidden;
}}
.bar-fill{{
  height:100%;
  border-radius:9px;
  transition:width 0.6s ease;
  transform-origin:left;
  animation:barGrow 0.8s ease-out;
}}
@keyframes barGrow{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
.bar-value{{
  font-size:0.8rem;
  color:#c9d1d9;
  font-weight:600;
}}

/* Funnel chart */
.funnel-group{{margin-bottom:0.75rem}}
.funnel-label{{font-size:0.8rem;color:#8b949e;margin-bottom:0.25rem}}
.funnel-bar{{
  display:flex;
  height:32px;
  border-radius:8px;
  overflow:hidden;
}}
.funnel-seg{{
  display:flex;
  align-items:center;
  justify-content:center;
  font-size:0.75rem;
  font-weight:600;
  color:#0d1117;
  min-width:40px;
  white-space:nowrap;
}}
.funnel-seg--target{{opacity:0.6}}

/* Table */
table{{
  width:100%;
  border-collapse:collapse;
  font-size:0.85rem;
}}
th,td{{
  text-align:left;
  padding:0.6rem 0.75rem;
  border-bottom:1px solid #21262d;
}}
th{{
  color:#8b949e;
  font-weight:600;
  font-size:0.8rem;
  text-transform:uppercase;
  letter-spacing:0.05em;
}}
td{{color:#c9d1d9}}
tr:hover td{{background:#161b2280}}

/* Intelligence */
.intel-grid{{
  display:grid;
  grid-template-columns:repeat(5,1fr);
  gap:1rem;
}}
@media(max-width:900px){{
  .intel-grid{{grid-template-columns:repeat(2,1fr)}}
}}
.intel-card{{
  background:#0d1117;
  border:1px solid #30363d;
  border-radius:10px;
  padding:1rem;
  text-align:center;
  animation:fadeIn 0.5s ease-out;
}}
@keyframes fadeIn{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}
.intel-card .value{{
  font-size:1.5rem;
  font-weight:700;
  color:#e6edf3;
  margin-bottom:0.25rem;
}}
.intel-card .label{{
  font-size:0.75rem;
  color:#8b949e;
  text-transform:uppercase;
  letter-spacing:0.05em;
}}
</style>
</head>
<body>
<div class="container">

  <!-- Header -->
  <div class="header">
    <h1>Content Autopilot Dashboard</h1>
    <span class="date">v9.0 | {escape(date_str)}</span>
  </div>

  {profile_banner}

  <!-- Intelligence Report -->
  <div class="section">
    <h2>Intelligence Report</h2>
    <div class="intel-grid">
      <div class="intel-card">
        <div class="value">{intel["total_runs"]}</div>
        <div class="label">Total Runs</div>
      </div>
      <div class="intel-card">
        <div class="value">{intel["avg_quality"]}</div>
        <div class="label">Today's Quality</div>
      </div>
      <div class="intel-card">
        <div class="value" style="color:{trend_color}">{trend_icon}</div>
        <div class="label">Activity Trend</div>
      </div>
      <div class="intel-card">
        <div class="value">{escape(intel["most_used_logic"])}</div>
        <div class="label">Top Title Logic</div>
      </div>
      <div class="intel-card">
        <div class="value" style="color:{streak_color}">{intel["streak"]}d</div>
        <div class="label">Streak</div>
      </div>
    </div>
  </div>

  <!-- Today's Content -->
  <div class="section">
    <h2>Today's Content Preview</h2>
    <div class="grid-3">
      {content_cards}
    </div>
  </div>

  <!-- Scores + Funnel side-by-side -->
  <div class="grid-2">
    <div class="section">
      <h2>Quality Scores</h2>
      {score_bars}
    </div>
    <div class="section">
      <h2>Funnel Balance (TOFU / MOFU / BOFU)</h2>
      {funnel}
    </div>
  </div>

  <!-- 7-Day History -->
  <div class="section">
    <h2>7-Day History</h2>
    {history_table}
  </div>

</div>

  <footer style="text-align:center;padding:2rem;color:#484f58;font-size:0.75rem">
    Content Autopilot v9.0 &mdash; Generated {escape(date_str)}
  </footer>

</body>
</html>"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Content Autopilot Dashboard")
    parser.add_argument(
        "--date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Target date in YYYY-MM-DD format (default: today)",
    )
    args = parser.parse_args()

    date_str: str = args.date
    date_dir = _output_dir_for_date(date_str)
    dashboard_file = date_dir / "dashboard.html"
    root_dashboard = OUTPUT_BASE / "dashboard.html"

    # Load data
    profile, is_default_profile = load_profile()
    history = load_history()
    graded = discover_content(date_str)

    # Build HTML
    html = build_html(date_str, graded, history, profile, is_default_profile)

    # Ensure output directories exist
    date_dir.mkdir(parents=True, exist_ok=True)
    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)

    # Write dashboard to date folder
    with open(dashboard_file, "w", encoding="utf-8") as f:
        f.write(html)

    # Also copy to root for quick access
    import shutil
    shutil.copy2(dashboard_file, root_dashboard)

    # Collect section names that have data
    sections = ["header", "intelligence"]
    if any(g["content"] is not None for g in graded):
        sections.append("content_preview")
        sections.append("quality_scores")
    if history:
        sections.append("funnel_balance")
        sections.append("history_7day")
    if is_default_profile:
        sections.append("profile_banner")

    result = {
        "status": "generated",
        "path": str(dashboard_file),
        "sections": sections,
    }
    print(json.dumps(result, ensure_ascii=False))

    # Open in browser
    webbrowser.open(dashboard_file.as_uri())


if __name__ == "__main__":
    main()
