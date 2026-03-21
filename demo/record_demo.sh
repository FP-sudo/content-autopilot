#!/bin/bash
set -e

cp -r ~/.content-autopilot ~/.content-autopilot.demo-bak 2>/dev/null || true
rm -rf ~/.content-autopilot
rm -rf ~/Desktop/content-autopilot-output

SCRIPTS=~/content-autopilot/plugins/content-autopilot/scripts

echo ""
echo "  Content Autopilot"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  1コマンドで、note・X・Instagramを自律生成"
echo ""
sleep 2

echo "  $ python3 run_pipeline.py"
echo ""
sleep 1

cd "$SCRIPTS"
python3 run_pipeline.py

sleep 2

echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  github.com/FP-sudo/content-autopilot"
echo ""
sleep 2

rm -rf ~/.content-autopilot
mv ~/.content-autopilot.demo-bak ~/.content-autopilot 2>/dev/null || true
mkdir -p ~/Desktop/content-autopilot-output
cd "$SCRIPTS" && python3 init_data.py > /dev/null 2>&1
