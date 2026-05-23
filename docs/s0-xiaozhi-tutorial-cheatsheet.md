# S0 教程 6827 操作 cheatsheet

**生成日期**：2026-05-10 晚
**用途**：S0 路线图 #3-#9 期间的快速参考，避免重复 web fetch 教程
**来源**：https://www.ncnynl.com/archives/202509/6827.html（5/10 fetch 一次）
**适用阶段**：DNS + mcp-openduck 自检已完成 → 用户开始拆 ESP32 / 注册 xiaozhi.me 之后

> ⚠️ **教程的信息盲区**：教程 6827 大量靠**动图**展示 xiaozhi.me 控制台操作，文字描述简略。本 cheatsheet 把可机读的硬信息整理出来，**xiaozhi.me 网页操作仍需用户对照动图**（或 Playwright 协助勘察）。

---

## ESP32-S3 配网（路线图 #3+#5）

### 物理步骤

1. 上电（USB 供电或电池）
2. 等屏幕/LED 出现"扫描 wi-fi"字样
3. 按"上方右侧按钮"进入配网模式（关键按键位置）
4. ESP32 自动开自建热点
5. 手机 WiFi 列表连这个热点（教程未明确热点名 — 用户连接时记录下来）
6. 连上热点后通常自动跳转配网页 / 或手动浏览器开 192.168.4.1
7. 输入家里 WiFi（**1101 2.4G**，密码 `lm34618567`）
8. 等 ESP32 切换到 station 模式联网

### 重进配网模式

- "先断电再开机，然后等上方出现扫描 wi-fi 字样出来时，再按下上方右侧按钮即可"

### 联网成功后

- ESP32 屏幕/界面会出现一个**设备验证码**（关键 — 后续 xiaozhi.me 绑定要用）
- 截图保存这个验证码

---

## xiaozhi.me 控制台（路线图 #4+#6）

### 注册

- 网址 https://xiaozhi.me/
- 大概率手机号验证（用户操作，subagent 不替代）

### 绑定 ESP32（教程含动图，文字未详）

- 登录后台 → 找设备绑定入口
- 输入 ESP32 屏上的设备验证码
- ⚠️ **重要 reset 知识**："只有在小智 ai 官网解绑设备后才能重新出现设备验证码" — 如果验证码用过 / 过期，必须先官网解绑再重启 ESP32 才能拿新验证码

### 创建智能体（教程仅说"创建一个智能体角色"）

- 教程未列具体输入字段
- 推测：智能体名 / 模型选择 / 系统提示词等常规字段
- 用户操作时记录下来填了什么，反馈给 subagent

### 添加 MCP 端点（拿 wss URL）

- 教程描述："登录到小智 AI 官网创建一个智能体角色，添加上面配置好 wifi 的设备，然后获取其 mcp 接入点地址"
- 教程未明确 tab 名 / 字段名 — 仍靠动图
- **关键产出物**：一条形如 `wss://xxx.xiaozhi.me/...` 的 WebSocket URL
- 拿到后传给 subagent 填进 mcp_point.sh

---

## mcp_point.sh 创建（路线图 #7）

### mcp_point_example.sh 内容

教程未公开，但 bootstrap 自检 [L] 段确认文件存在（20 字节，符合一行 `export MCP_ENDPOINT= ` 的字节数）。

**实际操作前必做**：让用户 `cat /home/raspios/open_duck_mini_ws/mcp-openduck/mcp_point_example.sh` 拿真实内容样本。

### mcp_point.sh 应填什么

```bash
export MCP_ENDPOINT=<从 xiaozhi.me 拿到的完整 wss URL>
```

预计是 `wss://...` 开头（WebSocket Secure 协议），具体路径 / query 参数教程未定义。

### 创建命令（subagent 在路线图 #7 给）

```bash
cd /home/raspios/open_duck_mini_ws/mcp-openduck
cp mcp_point_example.sh mcp_point.sh
# 用 sed / nano 替换 export 后的占位符为真实 URL
```

⚠️ **不要把真实 wss URL 写进 git** — mcp_point.sh 应在 `.gitignore` 里（待验证；bootstrap [L] 段未列 .gitignore，下轮可补查）。

---

## 启动验收（路线图 #8）

### start_mcp.sh

成功输出关键词（教程提供）：
```
2025-09-27 10:32:42,685 - MCP_PIPE - INFO - [openduck.py] Connecting to WebSocket server...
INFO:OpenDuck:[Controller] {...}
```

**判健康**：日志含 `Connecting to WebSocket server` + `INFO:OpenDuck:[Controller]` = OK

### start_duck_mcp.sh

教程未提供成功输出样例。**判健康**：进程不闪退、不报 traceback 即可视为 OK；用喊话验收作真正判据。

⚠️ **5/22 实战发现的硬约束 — 必插 USB 手柄**：`Open_Duck_Mini_Runtime/scripts/v2_rl_walk_mujoco_mcp.py:125` 强制初始化 `PS4Controller`，`pygame.joystick.Joystick(0)` 在无手柄时**立即闪退**报 `pygame.error: Invalid joystick device number`。爱折腾整机版默认不带手柄，必须自备任意一个 USB 手柄（PS4/PS5/Xbox/杂牌通用都行）插上才能跑。不需要操作手柄，只需要让 pygame 看到 device 0 存在。S1 阶段改自家 MCP 时务必加 try/except fallback to dummy controller。

### 启动顺序

```bash
cd /home/raspios/open_duck_mini_ws/mcp-openduck
./start_mcp.sh           # 后台启动 WebSocket server (127.0.0.1:6789) + 注册 MCP 工具到云端
# 等几秒 server up
./start_duck_mcp.sh      # 启动 openduck.py 控制鸭子
```

两个 shell session（建议 tmux 分窗 / 两个 ssh 会话）分别跑两个 .sh，各自输出独立日志。

---

## 喊话验收语料（路线图 #9）

教程明确列出的 9 条命令（金标准 — 每条都应该能动）：

| # | 喊话 | 预期动作 |
|---|------|----------|
| 1 | 让鸭子向前两步 | 前进 2 步 |
| 2 | 让鸭子后退两步 | 后退 2 步 |
| 3 | 让鸭子左移一点 | 左横移 |
| 4 | 让鸭子右移一点 | 右横移 |
| 5 | 让鸭子左转一下 | 左转 |
| 6 | 让鸭子右转一下 | 右转 |
| 7 | 让鸭子动下左耳朵 | 左 SG90 舵机摆动 |
| 8 | 让鸭子动下右耳朵 | 右 SG90 舵机摆动 |
| 9 | 让鸭子叫一声 | 扬声器播音 |

**S0 验收最低门槛**：1 + 7（向前 + 动耳）任一通过 = 整链路 work。
**S0 完整验收**：9 条全过 = 出厂 MCP 工具集完整覆盖。

---

## reboot 验证（路线图 #10）

### 验收清单

```bash
# 1. DNS final 永久修复仍生效
cat /etc/resolv.conf  # 仍是 223.5.5.5 + 119.29.29.29
curl -sS https://gitee.com -o /dev/null -w "%{http_code}\n"  # 200

# 2. 关键服务自启
systemctl is-active systemd-networkd wpa_supplicant@wlan0 NetworkManager

# 3. mcp-openduck 仓库还在 + venv_duck 还在
ls /home/raspios/open_duck_mini_ws/mcp-openduck/mcp_point.sh
which python  # /home/raspios/venv_duck/bin/python

# 4. 重新启动 S0 链路
cd /home/raspios/open_duck_mini_ws/mcp-openduck
./start_mcp.sh &
./start_duck_mcp.sh &

# 5. ESP32 喊话验收（语料表第 1+7 条）
```

### 失败排查

| 现象 | 可能根因 | 应对 |
|------|---------|------|
| reboot 后 resolv.conf 变回电信 DNS | 某 daemon 启动时重写（理论不可能，实测排除） | 重新跑 `scripts/dns-arch-probe.txt` |
| start_mcp.sh 卡在 "Connecting to WebSocket server" 不进 INFO:OpenDuck | wss URL 错 / xiaozhi.me 服务挂 / 鸭子 DNS 解析 wss host 失败 | 看日志后续报错；用 `getent hosts <wss-host>` 测 DNS |
| start_duck_mcp.sh 立即闪退 | openduck.py 报错（依赖缺 / 硬件未就绪 / IMU 未校准） | 看 stderr |
| 喊话识别但不动 | start_mcp.sh 日志看到工具调用但 start_duck_mcp.sh 没反应 | mcp_point.sh URL 错（两进程连了不同的 wss） |

---

## 故障排查（教程未提供 FAQ，本 cheatsheet 补的）

### "重新拿验证码"流程

ESP32 配网完了 → 验证码用过 → 想再用：

1. 登录 xiaozhi.me → 设备页 → 解绑 ESP32
2. ESP32 断电 → 上电 → 等"扫描 wi-fi"字样 → 按上方右侧按钮
3. 屏幕显示新验证码

### PS4 手柄代码（5/22 升级：从"旁路警告"升为"强制依赖"）

教程明确："不保证使用 XBOX 协议手柄能直接通用，请根据实际情况进行处理"。**5/22 实战发现这不是"旁路警告"而是硬约束**：`start_duck_mcp.sh` 强制要求 USB 手柄存在（见上方 start_duck_mcp.sh 段）。S0 阶段必备任意 USB 手柄。S1 阶段重写时移除强制依赖。

---

## 教程未覆盖的盲区（subagent 注意）

下面这些**教程没写**的环节 subagent 必须**用户主导 + Playwright 协助勘察**，不要凭推测给指令：

1. xiaozhi.me 注册流程的具体页面（手机号 / 邮箱 / 第三方登录哪几种）
2. 智能体创建表单的具体字段
3. 添加 MCP 端点的菜单路径 / tab 名
4. wss URL 的实际格式样本（路径 / query / 是否含 token）
5. ESP32 屏幕的真实"扫描 wi-fi"字样位置（顶端 / 中间）
6. ESP32 自建热点的 SSID 名

**正确做法**：用户跑到这步时，**让用户描述当前屏幕 / 截图给主会话**，subagent 基于真实数据给指令。

---

## 相关脚本与文档

- 主 handoff：[`docs/s0-handoff-xiaozhi-voice-2026-05-10.md`](./s0-handoff-xiaozhi-voice-2026-05-10.md)
- WiFi 故障史：[`docs/troubleshoot-2026-05-10-huawei-5g-channel157-blocking-ssh.md`](./troubleshoot-2026-05-10-huawei-5g-channel157-blocking-ssh.md)
- ncnynl 教程总目录：[`docs/ncnynl-tutorial-index.md`](./ncnynl-tutorial-index.md)
- DNS 修复脚本：`scripts/dns-fix-final.txt`
- mcp 自检脚本：`scripts/mcp-openduck-bootstrap.txt`
