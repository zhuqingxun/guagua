#!/bin/bash
# 驱动 verify_pygame_hotplug.py 时序: 不依赖用户操作手柄, 用 bluetoothctl 控制断/连
# 总时长 40s: T=0 启动 python verify; T=10 disconnect; T=25 connect; T=40 退出
set -u
LOG=/tmp/hotplug-v3.log
: > "$LOG"
MAC=A0:5A:5F:0A:0F:2C

~/venv_duck/bin/python /tmp/verify_pygame_hotplug.py >> "$LOG" 2>&1 &
PY=$!

sleep 5
echo "--- T=5 DISCONNECT ---" >> "$LOG"
bluetoothctl disconnect "$MAC" >> "$LOG" 2>&1

sleep 20  # 给蓝牙 socket 充足时间释放, v3 用 15 秒 connect 失败
echo "--- T=25 CONNECT ---" >> "$LOG"
bluetoothctl connect "$MAC" >> "$LOG" 2>&1

wait "$PY"
echo "--- driver done ---" >> "$LOG"
cat "$LOG"
