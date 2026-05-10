# S0 接手文档：小智语音整合（教程 6827）

**生成日期**：2026-05-10 晚
**当前 milestone**：M3-W2 / S0 验收阶段（4 步中第 3 步）
**适用场景**：清理上下文后接续推进
**前置文档**：
- [`docs/troubleshoot-2026-05-10-huawei-5g-channel157-blocking-ssh.md`](./troubleshoot-2026-05-10-huawei-5g-channel157-blocking-ssh.md)（SSH 不通已解决）
- [`docs/m3-s0-checklist.md`](./m3-s0-checklist.md)（S0 4 步状态总览）
- 教程：https://www.ncnynl.com/archives/202509/6827.html

---

## 🚦 一句话状态

鸭子 SSH 通了 + mcp-openduck 出厂预装在 Pi 上。**当前阻塞 = 鸭子 DNS 解析失败（gitee.com 不可达），导致 git pull / pip install 等都失败**。需要先排查 DNS 是哪一层断；同时**用户需要拆包 ESP32 + 注册 xiaozhi.me 账号**。

---

## ⏭️ 接手后下一步（按顺序）

### Step 1（立即）：DNS 排查 — 拿数据

**PC PowerShell**（73 字符）：
```
Get-Content -Raw D:\CODE\guagua\scripts\dns-diag-cmd.txt | clip
```
然后切到鸭子 SSH 终端右键粘贴 → 回车。诊断脚本输出 `[A]-[G]` 7 段（路由 / DNS / 网关 ping / 外网 IP ping / 域名解析 / HTTPS baidu / HTTPS gitee）。

**判断分支**：
| 现象 | 真因 | 修法 |
|---|---|---|
| [C] 网关 ping 不通 | 鸭子局域网都不通 | 检查 wlan0 接口状态 |
| [C] 通 + [D] 8.8.8.8 不通 | 路由器没让鸭子 NAT 出去（罕见） | 路由器后台允许该设备访问外网 |
| [D] 通 + [E] DNS 解析失败 | DNS server 配的不可达 | 改 `/etc/resolv.conf` 加 `nameserver 223.5.5.5` |
| 全通 + [G] gitee.com 200 | 已恢复，前面 git pull 是临时网络抖动 | 重试 git pull |

### Step 2（立即可并行）：用户做的两件事

- **A. 拆包 ESP32-S3 模块**（购买的"实战派ESP32-S3小智语音交互" ¥250，5/10 时还未拆包）
  - 上电、看 LED 行为、找按键（教程提到"上方右侧按钮"进配网模式）
  - 教程后续步骤：手机连 ESP32 自建热点 → 输入家里 WiFi 凭证 → ESP32 联网
- **B. 注册 xiaozhi.me 账号**（PC 浏览器，可能要手机号验证）
  - 注册完了解控制台/智能体/设备绑定页面在哪
  - 教程后续要在这里创建智能体 + 绑定 ESP32 + 配 MCP 端点

### Step 3（DNS 通了之后）：教程 6827 配置 MCP 端点

完整流程（教程 6827）：
1. ✅ git clone mcp-openduck — **出厂已装**（`/home/raspios/open_duck_mini_ws/mcp-openduck/`）
2. ⚠️ 仓库可能要 `git pull` 拉最新（DNS 通才行）；或检查 `requirements.txt` 是否已 pip install 过
3. ⏳ ESP32 配网（手机连 ESP32 热点 → 输 wifi 凭证）
4. ⏳ xiaozhi.me 网页绑定 ESP32（拿验证码）
5. ⏳ xiaozhi.me 创建智能体 + 添加 MCP 端点 → **拿到 MCP 端点 URL**
6. ⏳ 鸭子端 `cd ~/open_duck_mini_ws/mcp-openduck && cp mcp_point_example.sh mcp_point.sh` → 把端点 URL 粘到 mcp_point.sh
7. ⏳ `./start_mcp.sh`（启动 WebSocket server 127.0.0.1:6789，注册 MCP 工具到云端）
8. ⏳ `./start_duck_mcp.sh`（启动 openduck.py 控制鸭子）
9. ✅ 用 ESP32 喊话测试

**验收标志**：
- `start_mcp.sh` 输出 `Successfully connected to WebSocket server` + `server listening on 127.0.0.1:6789`
- 喊"让鸭子向前两步"鸭子能动

---

## 📋 关键事实（5 秒上下文恢复用）

### 鸭子身份与连接
| 字段 | 值 |
|---|---|
| Hostname | OPENDUCKMINI-V108 |
| MAC | B8:27:EB:0D:F0:CD |
| 当前 WiFi 模式 | **station 走 2.4G `1101` SSID**（不是 5G！5G channel 157 路由器拦截已知 bug） |
| LAN IP | 192.168.3.166（DHCP）|
| 热点模式备用 IP | 192.168.12.1（hostapd `openduckmini` 无密码）|
| SSH 凭据 | `raspios` / `raspios` |
| Python venv | `(venv_duck)` 自动激活 |
| sshd 配置 | UseDNS no（保留），LogLevel INFO（已恢复默认）|
| 持久化 journal | ✅ Storage=persistent |
| duck-debug.service | 已 disable 但脚本/service 文件保留，未来 `systemctl enable --now` 一秒启用 |

### 网络环境
| 字段 | 值 |
|---|---|
| 路由器 | 华为 AX2 Pro，固件 3.0.3.215，LAN IP 192.168.3.1 |
| 路由器登录密码 | `lm34618567`（仅本地 LAN 可达，已用于 Playwright 自动化） |
| 黑名单 | OPENDUCKMINI-V108 **当前已移除**（鸭子能正常接入 1101 2.4G） |
| 2.4G SSID | `1101` |
| 5G SSID | `1101_5G`（**禁用**——channel 157 LAN 拦截 bug，详见 troubleshoot 文档）|
| WiFi 密码 | 与路由器登录密码同 |
| PC IP | 192.168.3.41 |

### 出厂预装的 mcp-openduck
路径：`/home/raspios/open_duck_mini_ws/mcp-openduck/`
关键文件：
- `start_mcp.sh` ✅
- `start_duck_mcp.sh` ✅
- `mcp_point_example.sh` ✅（需 cp 成 `mcp_point.sh` + 填端点 URL）
- `openduck.py` ✅（MCP 工具定义）
- `requirements.txt` ✅（dependencies 可能已装；DNS 通后 `pip install -r requirements.txt` 验证）
- mtime 2025-09，可能要 `git pull` 拉最新

### ESP32 状态
- 还**未拆包**
- 立创·实战派 ESP32-S3 开发板
- 接 WiFi（不接 Pi）
- 通过 xiaozhi.me 云端跟 Pi 的 MCP server 联动

### xiaozhi.me 状态
- 还**未注册账号**
- 网址 https://xiaozhi.me/

---

## 🚧 已知坑 + 注意事项

1. **不要切回 5G**：5G channel 157 上 PC↔鸭子 22 端口被路由器 spoof RST，所有 LAN 内 TCP 通信都不通。已永久切到 2.4G `1101`，wpa_supplicant 5G 备份在 `.5g.bak`。
2. **不要替换爱折腾自家 MCP**（S0 阶段红线）。S0 = 用爱折腾出厂的 MCP + xiaozhi.me 后端，跑通整套不动。**自家 MCP 是 S1 的事**。
3. **不要在 Pi 3B+ 上跑 LLM**。LLM 推理在 xiaozhi.me 云端。Pi 只跑控制 + MCP。
4. **不要修改 ONNX 推理权重 / 重训**。
5. **PS4 手柄代码**：教程明确"不保证 XBOX 协议直接通用"。
6. **设备解绑**：xiaozhi.me 官网先解绑 ESP32，才能重新获取验证码。
7. **DEBUG3 已清掉，UseDNS no 保留**（防御性）。

---

## 📁 相关文件

### docs/
| 用途 | 路径 |
|---|---|
| 本文档（小智接手） | `docs/s0-handoff-xiaozhi-voice-2026-05-10.md` |
| WiFi 故障定位 | `docs/troubleshoot-2026-05-10-huawei-5g-channel157-blocking-ssh.md` |
| 旧 WiFi 接手（已过时） | `docs/s0-handoff-wifi-fix.md` |
| S0 4 步 checklist | `docs/m3-s0-checklist.md` |
| OpenDuckMini 知识库 | `docs/openduckmini-knowledge-from-share-2026-05-04.md` |
| 卖家聊天 OCR | `docs/seller-chat-aizheteng.md` |
| ncnynl 教程总目录 | `docs/ncnynl-tutorial-index.md` |

### scripts/
| 用途 | 路径 |
|---|---|
| DNS 诊断单行（clip 进剪贴板用） | `scripts/dns-diag-cmd.txt` ⭐ |
| DNS 诊断 bash（已废弃，scp 方案被否） | `scripts/dns-diag.sh`（可删）|
| 诊断框架脚本（已 disable，备用） | `scripts/duck-debug.sh` + `scripts/duck-debug.service` + `scripts/duck-debug-install.txt` |

### 鸭子端关键路径
- `/home/raspios/open_duck_mini_ws/mcp-openduck/`（出厂预装）
- `/etc/wpa_supplicant/wpa_supplicant-wlan0.conf`（已改 1101，备份 `.5g.bak`）
- `/etc/ssh/sshd_config.d/99-debug.conf`（仅 `UseDNS no`）
- `/etc/systemd/journald.conf`（`Storage=persistent`）
- `/var/log/journal/<machine-id>/`（持久化日志）
- `/usr/local/bin/duck-debug.sh` + `/etc/systemd/system/duck-debug.service`（disabled，备用）

---

## 🆘 万一接手后又 SSH 不通怎么办

按可能性排序：
1. **WiFi 路由器换了 IP**：路由器后台看鸭子 IP，直接用新 IP `ssh raspios@<new-ip>`
2. **wpa_supplicant SSID 被改回 5G**：手机连 `openduckmini` 热点 → SSH 进鸭子 → grep ssid `/etc/wpa_supplicant/wpa_supplicant-wlan0.conf` 确认是 `1101` 不是 `1101_5G`
3. **诡异故障重现**：路由器加回鸭子 MAC 黑名单触发 fallback → 手机连热点 SSH → `systemctl enable --now duck-debug.service` 复用 boot-time 诊断框架

详见 [`docs/troubleshoot-2026-05-10-huawei-5g-channel157-blocking-ssh.md`](./troubleshoot-2026-05-10-huawei-5g-channel157-blocking-ssh.md) 末尾"如果未来再不通"。

---

## 🔄 跨会话流程约束（新规则，2026-05-10 加固）

全局 `~/.claude/CLAUDE.md` 已强制：
- 给用户的命令必须 **真单行 + ≤120 字符**
- 超 120 字符必须落 `<project>/scripts/<name>.{sh,ps1,txt}`
- 给用户的指令变成跑文件路径 / `Get-Content -Raw <path> \| clip` 进剪贴板

剪贴板 trim 工具相关 todo：`D:\CODE\OS\rpiv\todo\todo-clipboard-trim-trigger-design.md`（在 OS 项目独立推进，不在本会话）。

---

**接手指引**：新会话进来读本文件 + 跑 Step 1 拿 DNS 数据，同时让用户做 Step 2（拆包 + 注册）。Step 3 要 DNS 通 + ESP32 配网 + xiaozhi.me 拿到 MCP 端点 URL 才能开始。
