---
title: "[M3-S0] vendor 热插拔 patch RPIV - 满足'手柄随时接入'"
type: feature
status: open
priority: high
created_at: 2026-05-24T13:25:00
updated_at: 2026-05-24T13:25:00
---

# Vendor hotplug patch - 任何时候手柄都能蓝牙接入控制鸭子

## 背景

- 5/22 PS4 模式通关靠"开机时手柄必插"绕过；5/23 加 `_StubPS4` fallback 让无手柄场景能起 LLM 链路
- 5/24 用户场景明确："开机不带手柄, 开机后某时刻才用蓝牙连手柄" → systemd 启动 RLWalk 时 `pygame.joystick.Joystick(0)` 失败 fallback stub → 后续手柄就算重连也吃不到, 必须 `systemctl restart` 让 RLWalk 重探
- 5/24 verify 实验通过：pygame 2.6 + SDL 2.28 `JOYDEVICEADDED/REMOVED` 事件机制在 venv_duck 环境完全工作（v3 REMOVED + v7 ADDED 双向证据）

## 目标

改造 `v2_rl_walk_mujoco_mcp.py` 让手柄真正热插拔，不需要 restart 服务：

- 服务启动时手柄不存在 → 用占位/stub 起来，RL loop 跑 + LLM 链路可用
- 运行中按 PS 键连手柄 → `pygame.JOYDEVICEADDED` 事件触发 → 切到真 controller, 摇杆能控
- 运行中手柄断开 → `pygame.JOYDEVICEREMOVED` 事件触发 → 切回 stub, LLM 链路不挂

## 实施路径（待 PRD 细化）

1. **PS4Controller 改 lazy init**：移除 `__init__` 里硬调 `Joystick(0)`，改"无设备就空 + ADDED 事件时 attach"
2. **RL 主循环 pump events**：50Hz loop 里每 N 帧调 `pygame.event.get()` 处理 ADDED/REMOVED
3. **merge_commands 视接入状态**：PS4 在线时 ps4_values 非零优先，离线时全 zero（不阻塞 MCP）

## 验收门（4 种状态切换都要测）

| 启动时手柄 | 中途操作 | 期望 |
|---|---|---|
| 不在 | 按 PS 键连 | 摇杆能控（验证运行中 ADDED） |
| 不在 | 不连 | LLM 可控全程（验证 stub 兼容） |
| 在 | 长按 PS 键关 | LLM 仍可控（验证运行中 REMOVED） |
| 在 | 不动 | 摇杆能控 + LLM 能控（基线，5/22 已通） |

## 走 RPIV 完整流程

- requirements/prd-vendor-hotplug.md（待写）
- plans/plan-vendor-hotplug.md（待写）
- execute 落 patch 到 `guagua-customizations` 分支
- patch diff 副本到 `docs/patches/hotplug-2026-05-24.diff`
- duck-workspace-state.md §1 同步新 commit
- validation/validation-vendor-hotplug.md（4 种状态切换实测报告）

## verify 实验产物（已落地, 入 commit）

- `scripts/verify_pygame_hotplug.py` 事件机制最终版
- `scripts/verify_pygame_minimal.py` 单次 init 对照
- `scripts/drive_hotplug_verify.sh` ssh 自动驱动 disconnect+connect

## 暂缓原因（2026-05-24 13:25）

verify 通过后用户报舵机异响, RPIV 推进暂停, 优先诊断异响是否跟会话期间 3-4 次 systemctl restart 有关。
异响解决后回来继续走 PRD。
