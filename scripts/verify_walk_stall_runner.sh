#!/bin/bash
# walk stall J+K verify runner (2026-05-26)
# 用户在自己终端跑: ssh duck "bash /tmp/verify_walk_stall_runner.sh"

set -e

echo "=== Stop services ==="
sudo systemctl stop duck-mcp-runtime mcp-openduck
sleep 1

echo ""
echo "=== Run verify script (12 sec, 50Hz sampling) ==="
~/venv_duck/bin/python -u /tmp/verify_walk_stall_J_K.py
PY_EXIT=$?

echo ""
echo "=== Restart services ==="
sudo systemctl reset-failed duck-mcp-runtime 2>/dev/null || true
sudo systemctl start duck-mcp-runtime mcp-openduck
sleep 2
systemctl is-active duck-mcp-runtime mcp-openduck

echo ""
if [ "$PY_EXIT" = "0" ]; then
    echo "=== ALL DONE === jsonl 在 /tmp/walk_stall_check.jsonl, 让 AI 分析"
else
    echo "=== verify script FAILED (exit $PY_EXIT), 但服务已 restart ==="
fi
