---
title: "鸭子 LLM/MCP 语音交互链路未重建"
type: todo
status: open
priority: medium
created_at: 2026-07-01T23:15:00
updated_at: 2026-07-01T23:15:00
---

# 鸭子 LLM/MCP 语音交互链路未重建

## 任务描述

2026-06-06/07 系统整盘重置后，小智语音交互链路的配置（`~/open_duck_mini_ws/mcp-openduck/mcp_point.sh`，含 wss URL token）随系统一起丢失，至今未重新配置。2026-07-01 验证走路控制时，`v2_rl_walk_mujoco_mcp.py` 是在"`MCPController` 挂起、纯 PS4 手柄驱动"的模式下跑通的——MCP 侧一直没有客户端连接，也就是说 S0 阶段原本已经打通的 LLM 语音指令控制走路的能力，现在实际上是不可用的。

这属于 S0（跑通整机）阶段完整环境的一部分，此前 5/23 曾经完整验证过（`#10 reboot 自启 + LLM 链路完整闭环`），但重置后失效，且还牵涉 xiaozhi.me token rotate 这项更早的遗留待办（自 5/22 起就 pending，未处理）。

## 涉及文件

- 鸭子端 `~/open_duck_mini_ws/mcp-openduck/mcp_point.sh`（当前不存在，需要根据爱折腾原始配置方式重新生成，含 xiaozhi.me 的 wss token）
- 参考文档：`docs/s0-handoff-passed-2026-05-22.md`（如果还在）、CLAUDE.md 里 System 2 演进路径 S0 阶段说明

## 完成标准

- `mcp_point.sh` 重新生成并验证 wss 连接正常
- 语音喊"前进"之类指令能让鸭子实际走动（端到端到物理动作，不能只看 MCP 工具调用响应——这是之前 5/23 踩过的坑，见 `docs/duck-workspace-state.md` §6 修订记录）
- 顺带处理 xiaozhi.me token rotate 这项更早的遗留待办

## 备注

优先级中——不影响当前"手柄直接控制走路"这条主线路径的日常使用/演示，但属于 S0 阶段本该完整闭环的能力，之前已经验证过一次说明可行，只是重置后没跟着重建。跟 [[infra-duck-reboot-autostart]] 是两回事：这个是"语音链路能不能连上"，那个是"走路进程要不要开机自启"，两者独立，谁先做不影响另一个。
