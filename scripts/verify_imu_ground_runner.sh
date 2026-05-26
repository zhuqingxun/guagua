#!/bin/bash
# IMU ground baseline runner (2026-05-26)
# 用户跑: ssh -t duck "bash /tmp/verify_imu_ground_runner.sh"

set -e

echo "=== Stop services (释放 I2C 给 IMU 独占) ==="
sudo systemctl stop duck-mcp-runtime mcp-openduck
sleep 1

echo ""
echo "=== Run IMU ground baseline (5 sec, 50Hz) ==="
~/venv_duck/bin/python -u /tmp/verify_imu_ground.py
PY_EXIT=$?

echo ""
echo "=== Restart services ==="
sudo systemctl reset-failed duck-mcp-runtime 2>/dev/null || true
sudo systemctl start duck-mcp-runtime mcp-openduck
sleep 2
systemctl is-active duck-mcp-runtime mcp-openduck

echo ""
if [ "$PY_EXIT" = "0" ]; then
    echo "=== ALL DONE ==="
else
    echo "=== FAILED (exit $PY_EXIT), 服务已 restart ==="
fi
