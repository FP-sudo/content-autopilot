#!/usr/bin/env python3
"""Content Grader — score content quality with Japanese-aware checks.

Usage:
    python3 grader.py <file_path>          # human-readable output
    python3 grader.py <file_path> --json   # structured JSON output
    python3 grader.py <file_path> --json --platform note  # platform-specific
"""

import argparse
import json
import re
import sys
from pathlib import Path


def count_japanese_chars(text: str) -> int:
    """Count characters in a Japanese-aware way (full-width = 1 char)."""
    return len(text)


def detect_platform(file_path: str) -> str:
    """Detect platform from filename pattern."""
    name = Path(file_path).stem.lower()
    if name.startswith("note"):
        return "note"
    if name.startswith("x_") or name.startswith("x-"):
        return "x"
    if name.startswith("instagram") or name.startswith("ig"):
        return "instagram"
    return "note"  # default


def kanji_ratio(text: str) -> float:
    """Calculate the ratio of kanji characters in text."""
    if not text:
        return 0.0
    kanji_count = sum(
        1 for ch in text
        if "\u4e00" <= ch <= "\u9fff" or "\u3400" <= ch <= "\u4dbf"
    )
    total = sum(1 for ch in text if not ch.isspace())
    return kanji_count / total if total > 0 else 0.0


def check_desu_masu_consistency(text: str) -> dict:
    """Check consistency of desu/masu vs da/dearu style."""
    desu_masu = len(re.findall(r"(?:です|ます|ました|でした|ません|ましょう)[。\n]", text))
    da_dearu = len(re.findall(r"(?:である|だ|だった|ではない)[。\n]", text))

    total = desu_masu + da_dearu
    if total == 0:
        return {"style": "unknown", "consistent": True, "ratio": 0}

    dominant = "desu_masu" if desu_masu >= da_dearu else "da_dearu"
    dominant_count = max(desu_masu, da_dearu)
    ratio = dominant_count / total

    return {
        "style": dominant,
        "consistent": ratio >= 0.85,
        "ratio": round(ratio, 2),
        "desu_masu_count": desu_masu,
        "da_dearu_count": da_dearu,
    }


def split_sentences_ja(text: str) -> list[str]:
    """Split Japanese text into sentences by common delimiters."""
    sentences = re.split(r"[。！？\n]+", text)
    return [s.strip() for s in sentences if s.strip()]


def split_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs by double newlines or section headers."""
    paragraphs = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paragraphs if p.strip()]


# ---------------------------------------------------------------------------
# Grading functions — each returns (score: int, issues: list[dict])
# ---------------------------------------------------------------------------

def grade_hook(content: str, platform: str) -> tuple[int, list[dict]]:
    """Grade the opening hook (first line/sentence)."""
    lines = content.strip().split("\n")
    # Skip markdown headers for the hook check
    first_content_line = ""
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("---"):
            first_content_line = stripped
            break

    if not first_content_line:
        return 0, [{"field": "hook", "action": "最初の1行にフック（読者の興味を引く文）を追加する", "severity": "high"}]

    score = 10
    issues = []

    # Japanese hook quality checks
    hook_len = count_japanese_chars(first_content_line)

    # Check hook length (Japanese: 40 chars ideal for hooks)
    if hook_len > 40:
        score -= 2
        issues.append({
            "field": "hook",
            "action": f"フック文を40文字以内に短縮する（現在{hook_len}文字）",
            "severity": "high",
        })

    # Check for hook patterns: quotes, questions, numbers, inversion
    hook_patterns = [
        (r"[「」『』]", "引用"),
        (r"[？?]", "疑問"),
        (r"\d+", "数字"),
        (r"^(?:実は|意外と|驚くべき|まさか|なぜ)", "意外性"),
    ]
    pattern_matches = sum(1 for pat, _ in hook_patterns if re.search(pat, first_content_line))

    if pattern_matches == 0:
        score -= 4
        issues.append({
            "field": "hook",
            "action": "フックに引用（「」）、疑問（？）、数字、意外性の要素を1つ以上追加する",
            "severity": "high",
        })

    return score, issues


def grade_readability(content: str) -> tuple[int, list[dict]]:
    """Grade readability with Japanese-specific checks."""
    score = 10
    issues = []

    # 1. Paragraph length check (max 3 sentences per paragraph)
    paragraphs = split_paragraphs(content)
    long_paras = []
    for i, para in enumerate(paragraphs):
        sentences = split_sentences_ja(para)
        if len(sentences) > 4:
            long_paras.append(i + 1)

    if long_paras:
        score -= 2
        issues.append({
            "field": "paragraphs",
            "action": f"段落{long_paras}を3文以内に分割する（1段落が長すぎて読みにくい）",
            "severity": "medium",
        })

    # 2. desu/masu consistency
    style_check = check_desu_masu_consistency(content)
    if not style_check["consistent"] and style_check["style"] != "unknown":
        score -= 3
        mixed_style = "です/ます体" if style_check["style"] == "desu_masu" else "だ/である体"
        issues.append({
            "field": "tone",
            "action": f"文体を{mixed_style}に統一する（現在{style_check['ratio']*100:.0f}%の一貫性）",
            "severity": "high",
        })

    # 3. Kanji ratio (ideal: 20-40%)
    ratio = kanji_ratio(content)
    if ratio > 0.45:
        score -= 2
        issues.append({
            "field": "readability",
            "action": f"漢字率を下げる（現在{ratio*100:.0f}%、理想は20-40%）。ひらがなに開ける漢字を検討する",
            "severity": "medium",
        })
    elif ratio < 0.15 and len(content) > 200:
        score -= 1
        issues.append({
            "field": "readability",
            "action": f"漢字率が低すぎる（現在{ratio*100:.0f}%）。幼稚な印象を避けるため適度に漢字を使う",
            "severity": "low",
        })

    # 4. Line break frequency (Japanese readers prefer frequent breaks)
    lines = content.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    if non_empty_lines:
        avg_line_len = sum(count_japanese_chars(line) for line in non_empty_lines) / len(non_empty_lines)
        if avg_line_len > 120:
            score -= 2
            issues.append({
                "field": "line_breaks",
                "action": "1行あたりの文字数を減らす（80-100文字で改行推奨）",
                "severity": "medium",
            })

    # 5. Paragraph density check (note platform needs sufficient content)
    total_content_len = count_japanese_chars(content)
    if total_content_len < 1500:
        score -= 3
        issues.append({
            "field": "density",
            "action": "コンテンツ量が不足しています",
            "severity": "high",
        })

    return score, issues


def grade_structure(content: str) -> tuple[int, list[dict]]:
    """Grade content structure (headers, sections, flow)."""
    score = 10
    issues = []

    headers = re.findall(r"^#{1,3}\s+.+", content, re.MULTILINE)

    if len(headers) < 2:
        score -= 3
        issues.append({
            "field": "structure",
            "action": "見出し（##）を3-7個追加してセクション構造を作る",
            "severity": "high",
        })
    elif len(headers) > 10:
        score -= 1
        issues.append({
            "field": "structure",
            "action": f"見出しが多すぎる（{len(headers)}個）。7個以内にまとめる",
            "severity": "low",
        })

    # Check for conclusion/summary section
    has_conclusion = bool(re.search(
        r"(?:まとめ|おわりに|最後に|結論|まとめると)", content
    ))
    if not has_conclusion and count_japanese_chars(content) > 1500:
        score -= 2
        issues.append({
            "field": "structure",
            "action": "「まとめ」セクションを追加する",
            "severity": "medium",
        })

    return score, issues


def grade_platform_fit(content: str, platform: str) -> tuple[int, list[dict]]:
    """Grade platform-specific fitness with Japanese char counts."""
    score = 10
    issues = []
    char_count = count_japanese_chars(content)

    if platform == "note":
        if char_count < 1000:
            score = 0
            issues.append({
                "field": "length",
                "action": f"文字数が大幅に不足（現在{char_count}文字、最低1000文字必要。note推奨: 2000-5000文字）",
                "severity": "high",
            })
        elif char_count < 2000:
            score = max(0, 2)
            issues.append({
                "field": "length",
                "action": f"文字数を増やす（現在{char_count}文字、note推奨: 2000-5000文字）",
                "severity": "high",
            })
        elif char_count > 6000:
            score -= 2
            issues.append({
                "field": "length",
                "action": f"文字数を減らす（現在{char_count}文字、note推奨: 2000-5000文字）",
                "severity": "medium",
            })

    elif platform == "x":
        # For threads, check individual tweets
        tweets = re.split(r"\n---\n|\n\d+[./]\s", content)
        for i, tweet in enumerate(tweets):
            tweet_text = tweet.strip()
            if not tweet_text:
                continue
            # Japanese: 140 chars (full-width counted as 1)
            tweet_len = count_japanese_chars(tweet_text)
            if tweet_len > 280:
                score -= 2
                issues.append({
                    "field": f"tweet_{i+1}",
                    "action": f"ツイート{i+1}を280文字以内にする（現在{tweet_len}文字）",
                    "severity": "high",
                })

    elif platform == "instagram":
        # Check hook line (first 125 chars visible before "more")
        first_line = content.strip().split("\n")[0] if content.strip() else ""
        if count_japanese_chars(first_line) > 125:
            score -= 3
            issues.append({
                "field": "hook",
                "action": f"最初の行を125文字以内にする（「続きを読む」前に表示される部分）",
                "severity": "high",
            })

        # Hashtag count
        hashtags = re.findall(r"#\S+", content)
        if len(hashtags) < 20:
            score -= 2
            issues.append({
                "field": "hashtags",
                "action": f"ハッシュタグを増やす（現在{len(hashtags)}個、推奨: 25-30個）",
                "severity": "medium",
            })
        elif len(hashtags) > 30:
            score -= 1
            issues.append({
                "field": "hashtags",
                "action": f"ハッシュタグを減らす（現在{len(hashtags)}個、上限: 30個）",
                "severity": "low",
            })

    return score, issues


def grade_cta(content: str, platform: str) -> tuple[int, list[dict]]:
    """Grade CTA presence and quality (Japanese patterns)."""
    score = 10
    issues = []

    # Japanese CTA patterns
    cta_patterns = [
        r"フォロー",
        r"いいね",
        r"シェア",
        r"コメント",
        r"リンク",
        r"プロフ",
        r"詳しくは",
        r"続きは",
        r"チェック",
        r"登録",
        r"購読",
        r"読んでみて",
        r"見てみて",
        r"試してみて",
        r"ダウンロード",
        r"無料",
        r"限定",
        r"今すぐ",
        r"こちら",
        r"リプ",
        r"保存",
        r"ブックマーク",
        r"noteで",
        r"記事で",
    ]

    found_ctas = [pat for pat in cta_patterns if re.search(pat, content)]

    if not found_ctas:
        score -= 5
        issues.append({
            "field": "cta",
            "action": "CTA（行動喚起）を追加する。例: 「フォローで最新情報をチェック」「続きはnoteで」",
            "severity": "high",
        })
    elif len(found_ctas) < 2:
        score -= 2
        issues.append({
            "field": "cta",
            "action": "CTAを強化する。メインCTAに加えてサブCTA（いいね・保存の促し等）を追加",
            "severity": "medium",
        })

    return score, issues


def grade_ai_smell(content: str) -> tuple[int, list[dict]]:
    """Detect AI-generated content patterns (Japanese)."""
    score = 10
    issues = []

    ai_patterns_ja = [
        (r"(?:ご存じ|ご存知)の(?:通り|ように)", "「ご存じの通り」を削除し、具体的な事実から始める"),
        (r"(?:さまざま|様々)な(?:方法|アプローチ|手段)(?:が|を)", "「さまざまな方法」を具体的な方法名に置き換える"),
        (r"(?:重要|大切|大事)(?:な|です)(?:こと|点|ポイント)(?:は|が)", "「重要なことは」を削除し、直接本題に入る"),
        (r"(?:まず|最初に)(?:は|、)?(?:～|ー)?(?:について|に関して)", "冗長な前置きを削除して本題から書く"),
        (r"いかがでしたか", "「いかがでしたか」を削除し、具体的なまとめや次のアクションを書く"),
        (r"(?:本(?:記事|稿)|この(?:記事|投稿))(?:では|で)(?!わかること)", "「本記事では」を削除。読者は記事を読んでいることを知っている"),
        (r"(?:つまり|要するに)(?:、)?(?:～|ー)?", "「つまり」を削除して直接結論を述べる"),
        (r"(?:それでは|では)(?:早速|さっそく)", "「では早速」を削除してすぐ本題に入る"),
        (r"(?:～について|に関して)(?:見ていきましょう|解説します|紹介します)", "「～について解説します」を削除。すでに読んでいる読者には不要"),
    ]

    # Check for repeated "一方で" (multiple occurrences = AI pattern)
    ippou_count = len(re.findall(r"一方で", content))
    if ippou_count >= 2:
        score -= 2
        issues.append({
            "field": "ai_smell",
            "action": f"「一方で」の繰り返しを減らす（{ippou_count}回使用）。別の接続詞を使う",
            "severity": "medium",
        })

    for pattern, fix in ai_patterns_ja:
        if re.search(pattern, content):
            score -= 2
            issues.append({
                "field": "ai_smell",
                "action": fix,
                "severity": "medium",
            })

    return max(score, 0), issues


def grade_content(content: str, platform: str) -> dict:
    """Run all grading checks and return structured result."""
    # Short-circuit for empty/near-empty content
    if len(content.strip()) < 50:
        return {
            "score": 0,
            "grade": "D",
            "platform": platform,
            "char_count": count_japanese_chars(content),
            "kanji_ratio": 0,
            "writing_style": "unknown",
            "style_consistent": True,
            "category_scores": {k: 0 for k in ["hook", "readability", "structure", "platform_fit", "cta", "ai_smell"]},
            "issues": [{"field": "content", "action": "コンテンツがほぼ空です。最低2000文字のコンテンツを作成してください", "severity": "high"}],
            "issue_count": {"high": 1, "medium": 0, "low": 0},
            "pass": False,
            "recommendations": [],
        }

    checks = {
        "hook": grade_hook(content, platform),
        "readability": grade_readability(content),
        "structure": grade_structure(content),
        "platform_fit": grade_platform_fit(content, platform),
        "cta": grade_cta(content, platform),
        "ai_smell": grade_ai_smell(content),
    }

    all_issues = []
    category_scores = {}
    for category, (score, issues) in checks.items():
        category_scores[category] = score
        all_issues.extend(issues)

    # Weight: hook=20%, readability=20%, structure=15%, platform_fit=20%, cta=15%, ai_smell=10%
    weights = {
        "hook": 0.20,
        "readability": 0.20,
        "structure": 0.15,
        "platform_fit": 0.20,
        "cta": 0.15,
        "ai_smell": 0.10,
    }

    total_score = sum(
        category_scores[cat] * weights[cat] * 10
        for cat in weights
    )
    total_score = min(100, max(0, round(total_score)))

    # Sort issues by severity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    all_issues.sort(key=lambda x: severity_order.get(x.get("severity", "low"), 3))

    # Platform-specific recommendations (advisory only, do not affect score)
    recommendations = []
    if platform == "note":
        if not re.search(r'(?:わかること|学べること|ポイント)', content[:500]):
            recommendations.append("冒頭に「この記事でわかること」リストを追加するとnote読者の離脱率が下がります")
        question_headers = len(re.findall(r'^##\s.*[？?]', content, re.MULTILINE))
        if question_headers == 0:
            recommendations.append("見出しを疑問形にすると読者の興味を引きやすくなります（例: 「なぜAIが必要なのか」）")
        if not re.search(r'---', content[len(content)//2:]):
            recommendations.append("記事の中盤以降に「---」区切り線を入れると、noteでの読みやすさが向上します")
        if not re.search(r'(?:他の(?:note|記事)|こちらも(?:おすすめ|読んで))', content):
            recommendations.append("末尾に「他のnote記事」への誘導を追加すると回遊率が上がります")

    style_info = check_desu_masu_consistency(content)

    return {
        "score": total_score,
        "grade": "A" if total_score >= 90 else "B" if total_score >= 75 else "C" if total_score >= 60 else "D",
        "platform": platform,
        "char_count": count_japanese_chars(content),
        "kanji_ratio": round(kanji_ratio(content) * 100, 1),
        "writing_style": style_info["style"],
        "style_consistent": style_info["consistent"],
        "category_scores": category_scores,
        "issues": all_issues,
        "recommendations": recommendations,
        "issue_count": {"high": sum(1 for i in all_issues if i["severity"] == "high"),
                        "medium": sum(1 for i in all_issues if i["severity"] == "medium"),
                        "low": sum(1 for i in all_issues if i["severity"] == "low")},
        "pass": total_score >= 75,
    }


def format_human_readable(result: dict) -> str:
    """Format grading result for human reading."""
    lines = [
        "=" * 44,
        "  Content Grader — 採点結果",
        "=" * 44,
        "",
        f"スコア: {result['score']}/100 ({result['grade']})",
        f"プラットフォーム: {result['platform']}",
        f"文字数: {result['char_count']}",
        f"漢字率: {result['kanji_ratio']}%",
        f"文体: {'です/ます体' if result['writing_style'] == 'desu_masu' else 'だ/である体' if result['writing_style'] == 'da_dearu' else '不明'}",
        f"文体一貫性: {'OK' if result['style_consistent'] else 'NG — 統一が必要'}",
        "",
    ]

    if result["issues"]:
        lines.append("--- 改善点 ---")
        lines.append("")
        for i, issue in enumerate(result["issues"], 1):
            severity_icon = {"high": "[!]", "medium": "[*]", "low": "[-]"}
            icon = severity_icon.get(issue["severity"], "[ ]")
            lines.append(f"  {icon} [{issue['field']}] {issue['action']}")
        lines.append("")

    if result.get("recommendations"):
        lines.append("--- note.com向け推奨事項 ---")
        lines.append("")
        for rec in result["recommendations"]:
            lines.append(f"  [+] {rec}")
        lines.append("")

    lines.append(f"判定: {'PASS' if result['pass'] else 'FAIL — スコア75以上で合格'}")
    lines.append("=" * 44)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Content Grader")
    parser.add_argument("file", help="Content file to grade")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--platform", help="Override platform detection")
    args = parser.parse_args()

    file_path = Path(args.file).expanduser()
    if not file_path.exists():
        error = {"error": f"ファイルが見つかりません: {file_path}"}
        if args.json:
            print(json.dumps(error, ensure_ascii=False))
        else:
            print(f"Error: {error['error']}")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    platform = args.platform or detect_platform(str(file_path))
    result = grade_content(content, platform)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_human_readable(result))


if __name__ == "__main__":
    main()
