# S0 通关 handoff（2026-05-22）

> **状态**：✅ **S0 教程 6827 整套打通**——"听到 → 听懂 → MCP → 做动作"闭环验收通过，能用小智语音控制鸭子做动作。
> **下次会话用**：catch up 当前状态 + 剩余两件待办（token rotate + reboot 验证）。

---

## 🚦 一句话状态

S0 路线图 #3-#9 全部 ✅，剩 #10（reboot 验证）+ **token rotate**（安全清理）。M3-W2 阶段已完成主体目标。

---

## ✅ 5/22 晚通关流程实录

| # | 任务 | 实际操作 |
|---|------|---------|
| #3 拆 ESP32-S3 包 | ✅ | 用户物理拆包上电（具体按键位置等细节未单独记录） |
| #4 注册 xiaozhi.me | ✅ | 用 `+86 135****4082` 手机号 |
| #5 ESP32 配网 | ✅ | 用另一台电脑连 ESP32 热点 → `192.168.4.1` → 选 `1101` 2.4G WiFi + 输密码 |
| #6 绑定 + 智能体 + MCP URL | ✅ | xiaozhi.me 自动有"默认智能体"（音色:湾湾小何, 模型:小智 Lite），自动绑了 ESP32（卡片显示"管理设备(1)"+ "最近对话:几秒前"）。MCP 接入点在智能体详情页拿，URL 形如 `wss://api.xiaozhi.me/mcp/?token=eyJ...`（JWT，agentId=1886229, userId=939129, exp=2027-???） |
| #7 mcp_point.sh 创建 | ✅ | PC 端写 D:/tmp/mcp_point.sh → scp 单行传到鸭子 `/home/raspios/open_duck_mini_ws/mcp-openduck/mcp_point.sh`。**example 实际格式 = `export MCP_ENDPOINT=` 一行**（带 `=`，原推测正确） |
| #8 start_mcp.sh + start_duck_mcp.sh | ✅（踩坑） | 第一个 SSH 跑 start_mcp.sh 正常（看到 `INFO:OpenDuck:[Controller]` 心跳广播）；第二个跑 start_duck_mcp.sh 闪退 → PS4 手柄强制初始化报错 → 插 USB 手柄绕过 |
| #9 喊话验收 | ✅ | 用户报告"现在已经可以用小智来控制鸭子的行为了" |

---

## 🔥 5/22 新发现的坑（务必记下）

### 坑 1: `v2_rl_walk_mujoco_mcp.py:125` 强制初始化 PS4 手柄

**症状**：`start_duck_mcp.sh` 立即闪退，报 `pygame.error: Invalid joystick device number`。

**根因**：`Open_Duck_Mini_Runtime/scripts/v2_rl_walk_mujoco_mcp.py` 在 RLWalk 构造函数里调 `PS4Controller(self.command_freq)`，PS4Controller `__init__` 调 `pygame.joystick.Joystick(0)`。**没插手柄就报错**。

**爱折腾整机版默认不带手柄**，所以出厂代码 vs 出厂硬件不匹配——这是 ncnynl 教程 6827 cheatsheet 早就预判过的盲区，5/22 实战触发。

**临时方案**：跑前插任意 USB 手柄（PS4 / PS5 / Xbox / 杂牌通用都行），让 pygame.joystick 识别到 device 0 即可。即使不用手柄操作，只要存在就行。

**S1 阶段要处理**：自家 MCP 重写时给 PS4Controller 加 try/except，无手柄时 fallback to dummy。

### 坑 2: wss URL 的 JWT token 进入对话上下文

**情况**：用户在 5/22 对话中**完整粘贴**了含 token 的 wss URL：
`wss://api.xiaozhi.me/mcp/?token=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjkzOTEyOSwiYWdlbnRJZCI6MTg4NjIyOSwiZW5kcG9pbnRJZCI6ImFnZW50XzE4ODYyMjkiLCJwdXJwb3NlIjoibWNwLWVuZHBvaW50IiwiaWF0IjoxNzc5NDU5OTM3LCJleHAiOjE4MTEwMTc1Mzd9.MlcqJGwS68_l9...`

**风险**：Claude Code transcript 保留这条记录，可能同步到 cloud / 用作 NeuroMem 等。视为已泄漏。

**rotate 步骤**（下次会话第一件事）：
1. 登录 https://xiaozhi.me/console/agents
2. 点击"默认智能体" → 进入详情页
3. 在"管理设备"里**解绑** ESP32
4. **重新绑定** ESP32（可能要按 ESP32 上方右侧按钮重进配网流程，或直接重新拿验证码）
5. 在智能体详情页**重新获取 MCP 接入点 URL**（拿到新 wss URL）
6. PC 端改 `D:/tmp/mcp_point.sh` 替换新 URL（**或直接删掉这个文件，避免本地残留**）
7. SSH 进鸭子 `nano /home/raspios/open_duck_mini_ws/mcp-openduck/mcp_point.sh` 替换新 URL
8. 重启 `start_mcp.sh` + `start_duck_mcp.sh`
9. 喊话验证新 URL 生效

**rotate 后下次提及 URL 时**：只贴前 40 字符（`wss://api.xiaozhi.me/mcp/?token=eyJhbGc...`），不贴完整 token。

---

## ⏭️ 下次会话第一件事

按重要性排序：

1. **🔐 rotate token**（见上方 rotate 步骤）—— 安全清理，建议尽快做
2. **♻️ #10 reboot 验证整套自启** —— S0 最终验收，验证：
   - DNS final 永久修复（`/etc/resolv.conf` 仍 `223.5.5.5` + `119.29.29.29`）
   - WiFi 仍连 2.4G `1101`（不被切回 5G）
   - mcp-openduck 仓库 + venv_duck 还在
   - 手动跑 `./start_mcp.sh` + `./start_duck_mcp.sh`（**记得插手柄**）
   - 喊话再次验证
3. **Step 4 录 demo + 备份 SD 卡**（m3-s0-checklist 的剩余任务）：
   - 完整跑一遍（行走 + web 控制 + 小智语音对话），3-5 分钟一镜到底
   - 用 Win32DiskImager 或 dd 把当前 SD 卡完整克隆，存外置硬盘 / 华为云盘
4. **进入 S1**：替换爱折腾自家 MCP 为 guagua 应用层 MCP 工具集，仍接 xiaozhi.me 后端

---

## 📋 当前关键事实（5 秒上下文恢复用）

### 鸭子状态
- Hostname: `OPENDUCKMINI-V108`, SSH `raspios@192.168.3.166` / `raspios`
- WiFi: 2.4G `1101`（5G 已禁用，5/10 channel 157 LAN 拦截 bug）
- DNS: `223.5.5.5` + `119.29.29.29`（运行时层 + systemd-networkd 防御层）
- mcp-openduck: `/home/raspios/open_duck_mini_ws/mcp-openduck/` HEAD `3fa9fd5`
- mcp_point.sh: 已落地，含 token（343 字节）
- Open_Duck_Mini_Runtime: `/home/raspios/open_duck_mini_ws/Open_Duck_Mini_Runtime/`
- venv_duck: `/home/raspios/venv_duck/`（Python 3.11.2）

### xiaozhi.me 状态
- 用户账号: `+86 135****4082`
- 智能体: "默认智能体"
  - userId=939129, agentId=1886229, endpointId=agent_1886229
  - 音色: 湾湾小何
  - 模型: 小智 Lite
- 设备: 1 个 ESP32-S3（实战派立创版，¥250 套件随机配的）

### 当前运行进程（如果还活着）
- 第一个 SSH 窗口: `start_mcp.sh`（在 mcp-openduck 目录），日志含 `INFO:OpenDuck:[Controller] {'commands': [0.0, ...]}` 心跳
- 第二个 SSH 窗口: `start_duck_mcp.sh`，PS4Controller 初始化通过（手柄已插）

---

## 📁 相关文档

- 本文档: `docs/s0-handoff-passed-2026-05-22.md`
- 主 checklist: `docs/m3-s0-checklist.md`（已更新 Step 3 → done）
- 教程 cheatsheet: `docs/s0-xiaozhi-tutorial-cheatsheet.md`（已升级 PS4 手柄硬警告）
- 上一接手（5/10）: `docs/s0-handoff-xiaozhi-voice-2026-05-10.md`
- WiFi 故障史: `docs/troubleshoot-2026-05-10-huawei-5g-channel157-blocking-ssh.md`

---

## 🛡️ 红线提醒

- ❌ 不要替换爱折腾自家 MCP（S0 阶段红线）。S1 阶段才换。
- ❌ 不要在 Pi 3B+ 跑 LLM。
- ❌ 不要修改 50Hz 控制循环 / ONNX 推理权重。
- ❌ 不要修改 ESP32 配网到 5G `1101_5G`（已知 channel 157 LAN 拦截 bug）。
