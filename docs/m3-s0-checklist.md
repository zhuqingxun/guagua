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
| 🚧 M3-W2 S0 验收 | **进行中** | Step 1 ✅ (5/10) / Step 2 ✅ (回溯确认, 5/15) / Step 3 进行中 (5/10 晚 DNS+mcp ✅) / Step 4 待做 |

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
- **5/10 晚进度**：进行中
  - ✅ 鸭子端 DNS 修复双层闭环（临时手改 + 永久 .network 防御性 DNS=223.5.5.5/119.29.29.29，避免未来装 systemd-resolved 后回退）
  - ✅ mcp-openduck 仓库自检通过（HEAD 最新 / pip 依赖全装好 / 4 关键脚本齐：start_mcp / start_duck_mcp / mcp_point_example / openduck.py）
  - ✅ 接手文档 + 教程 6827 cheatsheet 已写（[`s0-handoff-xiaozhi-voice-2026-05-10.md`](./s0-handoff-xiaozhi-voice-2026-05-10.md) + [`s0-xiaozhi-tutorial-cheatsheet.md`](./s0-xiaozhi-tutorial-cheatsheet.md)）
  - ⏳ 待做物理活：拆 ESP32-S3 包 + 注册 xiaozhi.me 账号 + ESP32 配网 + 控制台拿 wss URL + start_mcp 启动 + 喊话验收 + reboot 验证
- 注意：S0 = 用爱折腾出厂的 MCP + xiaozhi.me 后端，**不替换为自家 MCP**（违反 CLAUDE.md 红线）。自家版本是 S1+ 的事。

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
