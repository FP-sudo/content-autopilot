#!/usr/bin/env python3
"""Remove the old duplicate 線形フロー section from SKILL.md"""

import shutil

SOURCE = '/Users/sudotakao/content-autopilot/plugins/content-autopilot/skills/daily-autopilot/SKILL.md'
AGI_LAB_DEST = '/Users/sudotakao/agi-lab-skills-marketplace/plugins/content-autopilot/skills/daily-autopilot/SKILL.md'

with open(SOURCE, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the old 線形フロー section (the longer bash-commented version)
old_section = """
## 線形フロー（クイックリファレンス）

状態機械の全体をシンプルに要約すると以下の通り:

```bash
# 0. 出力ディレクトリ確保
mkdir -p ~/Desktop/content-autopilot-output

# 1. パイプライン初期化
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/autopilot.py --mode execute
# → JSON出力をパースし、execution_plan, content_spec, recommended_stage 等を取得

# 2. WebSearch → トピック自動選択
# → 検索失敗時はJSONのfallback_topicを使用

# 3. コンテンツ生成（note + X + Instagram）→ ファイル保存

# 4. 品質ゲート（score < 75 なら自動修正、最大2回）
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/grader.py ~/Desktop/content-autopilot-output/note_{date}.md --json

# 5. プレパブリッシュ検証（失敗項目を自動修正、最大2回）
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pre_publish.py ~/Desktop/content-autopilot-output/note_{date}.md --json

# 6. 履歴記録
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/record_history.py --topic "{topic}" --stage {stage} --category {category} --date {date}

# 7. ダッシュボード生成 + ブラウザ表示
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dashboard.py
open ~/Desktop/content-autopilot-output/dashboard.html

# 8. Intelligence Report
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/autopilot.py --mode summary
```

NOTE: `${CLAUDE_PLUGIN_ROOT}` はClaude Codeが自動解決する環境変数。
手動テスト時は `~/content-autopilot/plugins/content-autopilot` で代替可能。
"""

if old_section in content:
    content = content.replace(old_section, '\n')
    print("Removed old duplicate 線形フロー section")
else:
    print("WARNING: Old section not found exactly - checking...")
    # Try to find it
    if '状態機械の全体をシンプルに要約すると以下の通り' in content:
        print("Found the old section text but exact match failed")
    else:
        print("Old section already removed or not present")

with open(SOURCE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Updated: {SOURCE}")

# Copy to agi-lab repo
shutil.copy2(SOURCE, AGI_LAB_DEST)
print(f"Copied to: {AGI_LAB_DEST}")
