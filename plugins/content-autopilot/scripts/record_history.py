#!/usr/bin/env python3
"""Record History — append content entry to content-history.json and update series.

Usage:
    python3 record_history.py --topic "AI tools" --stage TOFU --category trending --date 2026-03-21
    python3 record_history.py --topic "AI tools" --stage MOFU --category overseas --date 2026-03-21 \\
        --suffix -002 --series-id series-2026-03-21-001
    python3 record_history.py --topic "AI tools" --stage TOFU --category trending --date 2026-03-21 \\
        --platforms note,x,instagram --note-type free --note-chars 3500
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path.home() / ".content-autopilot"
HISTORY_PATH = DATA_DIR / "content-history.json"
SERIES_PATH = DATA_DIR / "active-series.json"


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_entry_id(history: dict, date: str, suffix: str) -> str:
    """Generate a unique entry ID for the given date."""
    existing_ids = {e.get("id", "") for e in history.get("entries", [])}

    if suffix:
        candidate = f"{date}{suffix}"
        # Ensure uniqueness even with explicit suffix
        counter = 2
        while candidate in existing_ids:
            candidate = f"{date}{suffix}-{counter}"
            counter += 1
        return candidate

    existing_for_date = [
        e for e in history.get("entries", [])
        if e.get("date") == date
    ]
    seq = len(existing_for_date) + 1
    candidate = f"{date}-{seq:03d}"
    while candidate in existing_ids:
        seq += 1
        candidate = f"{date}-{seq:03d}"
    return candidate


def build_platforms_dict(platforms_str: str, date: str, suffix: str, note_type: str, note_chars: int) -> dict:
    """Build platforms dictionary from comma-separated platform list."""
    platforms = [p.strip() for p in platforms_str.split(",")]
    result = {}
    file_suffix = suffix if suffix else ""

    for platform in platforms:
        if platform == "note":
            result["note"] = {
                "title": "",
                "file": f"{date}/note_{date}{file_suffix}.md",
                "type": note_type,
                "char_count": note_chars,
            }
        elif platform == "x":
            result["x"] = {
                "title": "",
                "file": f"{date}/x_{date}{file_suffix}.md",
                "format": "thread",
                "tweet_count": 0,
            }
        elif platform == "instagram":
            result["instagram"] = {
                "title": "",
                "file": f"{date}/instagram_{date}{file_suffix}.md",
                "hashtag_count": 0,
            }

    return result


def update_series_status(series_id: str, date: str, output_file: str) -> dict:
    """Update the active series part status to 'published'."""
    series_data = load_json(SERIES_PATH)
    if not series_data or not series_data.get("series"):
        return {"updated": False, "reason": "series_not_found"}

    for series in series_data["series"]:
        if series["id"] != series_id:
            continue

        # Find the first pending part
        for part in series.get("parts", []):
            if part.get("status") == "pending":
                part["status"] = "published"
                part["content_file"] = output_file
                part["published_date"] = date

                # Check if all parts are now published
                all_done = all(
                    p.get("status") == "published"
                    for p in series.get("parts", [])
                )
                if all_done:
                    series["status"] = "completed"

                save_json(SERIES_PATH, series_data)
                return {
                    "updated": True,
                    "part": part["part"],
                    "series_completed": all_done,
                }

    return {"updated": False, "reason": "no_pending_parts"}


def main():
    parser = argparse.ArgumentParser(description="Record content to history")
    parser.add_argument("--topic", required=True, help="Content topic")
    parser.add_argument("--stage", required=True, choices=["TOFU", "MOFU", "BOFU"], help="Funnel stage")
    parser.add_argument("--category", required=True, help="Category (trending/overseas/evergreen)")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="Content date")
    parser.add_argument("--suffix", default="", help="File suffix (e.g., -002)")
    parser.add_argument("--series-id", default=None, help="Active series ID")
    parser.add_argument("--platforms", default="note,x,instagram", help="Comma-separated platforms")
    parser.add_argument("--note-type", default="free", choices=["free", "paid"], help="Note type")
    parser.add_argument("--note-chars", type=int, default=0, help="Note character count")
    parser.add_argument("--source", default="original", help="Content source (original/repurpose)")
    args = parser.parse_args()

    # Load or create history
    history = load_json(HISTORY_PATH)
    if not history:
        history = {"version": "1.0", "entries": []}
    if "entries" not in history:
        history["entries"] = []

    # Build entry
    entry_id = generate_entry_id(history, args.date, args.suffix)
    platforms = build_platforms_dict(
        args.platforms, args.date, args.suffix, args.note_type, args.note_chars
    )

    entry = {
        "id": entry_id,
        "date": args.date,
        "topic": args.topic,
        "category": args.category,
        "funnel_stage": args.stage,
        "platforms": platforms,
        "title_logics_used": [],
        "content_pillar": "",
        "source_url": None,
        "source": args.source,
        "series_id": args.series_id,
        "ab_titles": {
            "chosen": "",
            "alternative": "",
            "winner": None,
        },
    }

    history["entries"].append(entry)
    save_json(HISTORY_PATH, history)

    result = {
        "status": "recorded",
        "entry_id": entry_id,
        "date": args.date,
        "topic": args.topic,
        "stage": args.stage,
        "category": args.category,
    }

    # Update series if specified
    if args.series_id:
        series_result = update_series_status(
            args.series_id,
            args.date,
            f"note_{args.date}{args.suffix}.md",
        )
        result["series_update"] = series_result

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
