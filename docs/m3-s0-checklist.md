# M3 / S0 阶段剩余 Checklist

> 创建时间：2026-05-09
> 上下文：5/8 晚上已完成教程 6757「测试行走」（S0 第一个验收点），鸭子能跑步态。剩余任务用户已与 Claude 一起排序确认。
> 接续入口：未来任何会话进来读这个文件就能接上工作。

## 状态总览

| 阶段 | 状态 | 说明 |
|------|------|------|
| ✅ M3-W0 收货 | done | 5/7 18:28 |
| ✅ M3-W1 装配 | done | 5/7 21:22 装好支架 + 低压报警 |
| ✅ M3-W1 首次开机 | done | 5/8 22:21 接电池 + 扫到 `openduckmini` 热点 |
| ✅ M3-W1 行走测试 | done | 5/8 晚上跑通教程 6757 |
| ✅ M3-W2 S0 验收 | **主体完成** | Step 1 ✅ (5/10) / Step 2 ✅ (5/15) / Step 3 ✅ (5/22 跑通) / Step 4 待做（录 demo + 备份 SD 卡） |

## 接下来要做的步骤（按用户确认顺序）

### Step 1️⃣ 教程 6810 快速联网（切家庭 WiFi）

- 教程：https://www.ncnynl.com/archives/202507/6810.html
- 目标：把 Pi 3B+ 从默认热点 `openduckmini` 切到家庭 WiFi → 解决"电脑老切热点干不了别的活"
- 估时：30 min
- 验收：电脑保持在家庭 WiFi 上，能 ping / SSH 到 Pi
- 触发条件：完成
- ✅ **5/10 完成**（实际 ~3 小时，因华为 AX2 Pro 5GHz channel 157 LAN 拦截 bug，最终切 2.4G `1101` SSID 解决）
- 接手参考：[`docs/troubleshoot-2026-05-10-huawei-5g-channel157-blocking-ssh.md`](./troubleshoot-2026-05-10-huawei-5g-channel157-blocking-ssh.md)
- 当前 SSH：`ssh raspios@192.168.3.166`（password `raspios`）

### Step 2️⃣ 教程 6812 web 控制（探索 web 管理界面）

- 教程：https://www.ncnynl.com/archives/202507/6812.html
- 目标：看清楚爱折腾的 web 管理界面有哪些功能（卖家在 5/3 20:31 把它列为爱折腾的核心增值之一）
- 估时：30-60 min
- 验收：浏览器能打开 web UI，知道每个按钮 / 页面是干什么的
- 触发条件：Step 1 完成（这步也可以走默认热点，但联网后体验更好)
- ✅ **5/15 回溯确认完成**：行走测试 (Step 1 触发条件之前) + 切 WiFi (Step 1) 全部是通过爱折腾出厂 web 前端完成的, 自然过关。无需再单独走教程 6812

### Step 3️⃣ 教程 6827 整合小智语音控制（S0 验收终点）

- 教程：https://www.ncnynl.com/archives/202509/6827.html
- 目标：让鸭子能"听到 → 听懂 → 调用 MCP → 做动作"，整套出厂体验闭环
- 估时：1-2h（需要专注时间块，不要碎片化）
- 验收：用小智语音模块对鸭子说话，鸭子能识别 + 通过 MCP 调用动作
- 触发条件：Step 1+2 完成 + 你有完整的 1-2h 空闲时间
- **5/10 晚进度（已归档）**：DNS 修复双层闭环 + mcp-openduck 仓库自检
- **5/22 晚跑通**：✅ S0 验收通过
  - ✅ 拆 ESP32-S3 包 + 注册 xiaozhi.me（`+86 135****4082`）+ 用另一台电脑连 ESP32 热点(`192.168.4.1`)配 `1101` 2.4G WiFi 成功
  - ✅ xiaozhi.me 默认智能体自动绑定 ESP32（音色"湾湾小何" / 模型"小智 Lite" / agentId=1886229）+ 拿 MCP 接入点 wss URL
  - ✅ PC 端 `D:/tmp/mcp_point.sh` → scp 单行传到鸭子 → head -c 80 验证落地 OK
  - ✅ 第一个 SSH 跑 `start_mcp.sh` 正常（看到 `INFO:OpenDuck:[Controller]` 心跳）
  - ⚠️ 第二个 SSH 跑 `start_duck_mcp.sh` 闪退于 PS4 手柄初始化 → 插任意 USB 手柄绕过（**见下方踩坑详情**）
  - ✅ 喊话能用小智控制鸭子做动作 — "听到→听懂→MCP→做动作"闭环打通
  - ⏳ 剩两件：(1) **rotate wss URL token**（已进入对话上下文，视为泄漏）(2) reboot 验证整套自启
- **PS4 手柄踩坑**（5/22 新增 — S1 阶段务必处理）：
  - 文件：`Open_Duck_Mini_Runtime/scripts/v2_rl_walk_mujoco_mcp.py:125` 调 `PS4Controller(self.command_freq)`
  - 错误：`PS4Controller.__init__` line 40 调 `pygame.joystick.Joystick(0)` 失败 → `pygame.error: Invalid joystick device number`
  - 根因：爱折腾整机版默认**不带手柄**，出厂代码 vs 出厂硬件不匹配
  - 临时方案：跑 `start_duck_mcp.sh` 前**必插 USB 手柄**（任意手柄都行，pygame 只需要 device 0 存在）
  - S1 阶段修法：自家 MCP 实现里给 PS4Controller 加 try/except，无手柄时 fallback to dummy controller
- 注意：S0 = 用爱折腾出厂的 MCP + xiaozhi.me 后端，**不替换为自家 MCP**（违反 CLAUDE.md 红线）。自家版本是 S1+ 的事。
- 接手 handoff：[`s0-handoff-passed-2026-05-22.md`](./s0-handoff-passed-2026-05-22.md)（5/22 通关详情 + 剩余 token rotate / reboot 验证步骤）

### Step 4️⃣ 录 demo 视频 + 备份 SD 卡

- 拆为两个子任务：
  - **A. 录 demo 视频**：完整跑一遍（行走 + web 控制 + 小智语音对话），3-5 分钟一镜到底，存 `docs/m3-s0-demo-evidence/`
  - **B. 备份 SD 卡**：用 Win32DiskImager 或 dd 把现在的 Pi SD 卡完整克隆一份，存到外置硬盘 / 华为云盘
- 估时：30 min + 1h
- 触发条件：Step 1+2+3 完成
- **未做**

## 已记录的小问题（暂缓）

| Issue | 文件 | 状态 |
|-------|------|------|
| 一只脚内八字 | `rpiv/todo/m3-issue-pigeon-toed.md` | open / medium / 暂缓 |
| 文档优化建议（红线 / 电池 T 插 / 后盖卡扣） | 已 5/8 22:21 当面提给卖家，等他回复 | 等待 |

## S0 通关后的下一步（不在本 checklist 范围）

- **S1 自家 MCP 替换**：用 guagua 应用层 MCP 工具集替换爱折腾自家 MCP，但仍接 xiaozhi.me 后端（PRD §S1）
- **M1 W4**：参考动作处理（教程 6760，sim 项目里继续推进）
- **内八字处理**：满足 Step 1+2+3 完成 + 有标定教程实操经验后回来开 plan-feature

## 不要做的事（红线提醒）

- ❌ 不要修改 ONNX 推理权重 / 重训
- ❌ 不要修改 50Hz 控制循环代码
- ❌ 不要在 Pi 3B+ 上跑 LLM
- ❌ 不要替换爱折腾自家 MCP（S0 阶段，S1 才换）
- ❌ 不要现在就调内八字（满足触发条件后再开 plan）
