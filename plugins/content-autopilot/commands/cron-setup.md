---
description: "毎日の自動実行をcronで設定する（Mac/Linux対応）"
disable-model-invocation: true
---

以下の手順でContent Autopilotを毎日自動実行するcronジョブを設定します:

1. ユーザーの希望する実行時間を確認（デフォルト: 毎朝7:00）
2. 以下のcrontabエントリを追加:

```bash
# Content Autopilot - 毎日7:00に自動実行
0 7 * * * cd ~/content-autopilot/plugins/content-autopilot/scripts && python3 run_pipeline.py >> ~/.content-autopilot/cron.log 2>&1
```

3. `crontab -e` でエディタを開き、上記を追加
4. 確認: `crontab -l`

macOSの場合はlaunchctlも使用可能:
```bash
# ~/Library/LaunchAgents/com.content-autopilot.daily.plist を作成
```

これにより「一度設定したら、あとは毎日自動で走る」完全自律運用が実現します。
