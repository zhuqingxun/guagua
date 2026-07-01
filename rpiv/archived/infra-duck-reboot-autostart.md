---
title: "鸭子 reboot 自启 systemd unit 未配置"
type: todo
status: open
priority: medium
created_at: 2026-07-01T23:15:00
updated_at: 2026-07-01T23:15:00
---

# 鸭子 reboot 自启 systemd unit 未配置

## 任务描述

2026-06-06/07 系统整盘重置后，走路控制进程(`v2_rl_walk_mujoco_mcp.py`)的 reboot 自启 systemd unit 从未重新配置。当前每次需要用手柄控制走路，都得手动 SSH 上去用 `systemd-run` 起一个临时 unit（命令见 `docs/duck-workspace-state.md` §7）。2026-07-01 已确认 `guagua-customizations` 分支代码本身没问题（端到端走路验证通过），缺的只是"开机自动跑起来"这一层。

需要把手动命令固化成一个正式的 systemd service 文件（`[Install] WantedBy=multi-user.target` + `systemctl enable`），并处理好之前踩过的坑：必须以 `raspios` 用户运行（不能用 root，否则 `HOME` 解析成 `/root` 读不到 `duck_config.json` 直接崩溃）。

## 涉及文件

- 鸭子端新建 `/etc/systemd/system/duckwalk.service`（或类似命名）
- 参考命令模板：`docs/duck-workspace-state.md` §7
- 可能需要同步一份 unit 文件副本进 `guagua-customizations` 分支（当前该分支不含任何 `.service` 文件，systemd 配置一直是分支外手动维护，重置一次就得重配一次——是否要把 unit 文件也纳入 git 追踪一并解决，可以在做这个 todo 时一并评估）

## 完成标准

- `systemctl is-enabled duckwalk` 返回 `enabled`
- 鸭子重启后，不用任何手动 SSH 操作，手柄按 PS 键回连 + 按 ✕ 解锁即可直接走路
- 验证方式：真实执行一次 `sudo reboot`，等鸭子重新上线后现场测试

## 备注

优先级不高——当前手动启动的方式完全可用，只是每次开机要多做一步。不影响日常测试/演示。
