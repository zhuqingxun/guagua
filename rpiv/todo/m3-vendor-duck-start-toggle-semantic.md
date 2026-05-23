---
title: "[vendor bug] duck_start MCP 工具语义 = toggle 而非 unpause, LLM 模式反 intuition"
type: issue
status: open
priority: medium
created_at: 2026-05-23T19:55:00
updated_at: 2026-05-23T19:55:00
---

# Vendor bug: duck_start MCP 工具语义错位

## 现象

LLM 模式下,用户说"鸭子启动"时:

- **用户期望**: 鸭子从锁定态进入可活动态(产品语义: 准备开始走路)
- **LLM 实际**: 调 `duck_start` MCP 工具
- **vendor 实际**: `OpenDuckController.start()` 设 `A_pressed=True` 一帧 → broadcast → MCPController 收到 → `self.buttons.A.triggered` → toggle paused (**翻转**当前状态,不是 set False)
- **后果**: 当 `paused=False` 已解锁时,喊"启动"反而锁回 True

实测 2026-05-23 19:50:26 reboot 后(`start_paused=false` config),用户喊"启动" → PAUSE → 然后喊"向右转" 鸭子不动。

跟 PS4 物理模式 X 键(=Xbox A)语义不一致——物理按键模式下用户能看到 PAUSE/UNPAUSE log 自行调节,LLM 模式下用户看不到内部状态。

## 根因

`mcp-openduck/openduck_controller.py:243` `start()` 实现:

```python
def start(self):
    cmd = self.set_commands(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, True, False, False, False, False)
    #                                                       ↑ A=True
    self.update_cmd_queue(cmd)
    return "OpenDuck 左耳动了一下"
```

vendor 实现 = "模拟物理按 A",意图是 toggle paused。但物理按键有"按下 0.2s 松开"的脉冲性质,LLM 调用没有"松开"语义——本会话 `1e5f7e5` 修了 A.triggered storm,但没解决"toggle 方向不可预测"的问题。

## 影响

S0 阶段表面通过(已验证 reboot + LLM → 鸭子动),但用户体验有 corner case:

- 喊"启动"成败取决于鸭子当前 paused 状态,而用户看不到此状态
- 喊"暂停"实际是 `duck_pause` → `set_default()` → A=False,**根本不 toggle paused**(因 trigger 需 is_pressed False→True 转换)
- 失去"对话语义" / "Arm/Disarm 安全 gate" 的产品价值

## 修复路径选项(留 S1 决策)

### 选项 A: 修 mcp-openduck 仓库(违 S0 红线,需 S1 解锁)

改 `openduck_controller.py`:
- `start()`: 直接发送 unpause 命令(需新增 ws/MCP 协议:"set_paused False"),而非 set A=True
- `pause()`: 同上,发送 pause 命令

需配合修改 `mini_bdx_runtime/mcp_controller.py` 解析新协议,以及 `v2_rl_walk_mujoco_mcp.py` 处理新 MCP 字段(非通过 buttons.A 间接)。

### 选项 B: 在 Runtime customization 加 MCP-vs-PS4 source 区分

merge_commands 当前把 mcp_values + ps4_values OR 合并,失去来源信息。改 merge 保留来源,然后:
- `if mcp_values.A.triggered`: paused = False(幂等 unpause)
- `if ps4_values.A.triggered`: paused = not paused(物理按键 toggle 语义)

需改 `v2_rl_walk_mujoco_mcp.py` 多处。

### 选项 C: xiaozhi.me 端 system prompt 引导 LLM 行为

在 xiaozhi.me agentId=1886229 配置页加 system prompt:
- "duck_start 是切换鸭子锁定状态的工具,不是开始走路。用户说'启动/准备'时直接走路指令即可,不要主动调 duck_start"
- "duck_pause 同理,不要主动调"

不改代码,但依赖 LLM 跟随 prompt 准确度。

## 推荐

短期(本阶段): 选 C(system prompt 引导),0 代码变更,可逆。
长期(S1 时): 选 B(Runtime customization),保持 PS4 模式语义同时让 LLM 模式 work。
避免选 A(违 S0)。

## 关联

- 修复尝试 `1e5f7e5` 解决了 toggle storm,但没解决 toggle 方向不可预测
- `~/duck_config.json: start_paused=false` 让 boot 后默认 unlock,但 `duck_start` 调用仍反向 toggle
- 见 `docs/duck-workspace-state.md` §6 修订记录
