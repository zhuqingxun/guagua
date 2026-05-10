# S0 接手文档：鸭子 WiFi 切换 fallback 故障修复

> ## ⚠️ 状态：本文档已过时（2026-05-10 晚）
>
> SSH 不通的真因**不是** wifi_or_ap.sh fallback 行为，而是 **华为 AX2 Pro 路由器在 5GHz channel 157 上对 LAN 内 22 端口 TCP 包做 spoof RST 拦截**。
>
> **修复 = 把鸭子 WiFi 从 `1101_5G` 切到 `1101`（2.4G）**。已完成，PC 端 `ssh raspios@192.168.3.166` 当前可达。
>
> 完整定位过程 + 经验沉淀 → [`docs/troubleshoot-2026-05-10-huawei-5g-channel157-blocking-ssh.md`](./troubleshoot-2026-05-10-huawei-5g-channel157-blocking-ssh.md)
>
> 本文档下方的 wifi_or_ap.sh TIMEOUT/fallback 修改仍然有效（防御性，避免未来误连不上 WiFi 时失联），保留作历史参考。

**生成日期**：2026-05-10
**当前 milestone**：M3 到货后 / S0 装机调试阶段
**适用场景**：上一会话上下文膨胀，需要新会话接手继续

---

## 🚦 一句话状态

鸭子（爱折腾整机版 OPENDUCKMINI-V108，Pi 3B+）卡在"配置家里 WiFi 后路由器看到在线但 SSH 全 timeout、0 Kbps 流量"故障。**根因已定位、SSH 修复方案已应用到鸭子文件系统、待用户做最后两步物理操作验证**。

---

## ⏭️ 接手后下一步（按顺序）

### Step 1（用户在 PC 上操作）：路由器移除黑名单

浏览器 `http://192.168.3.1` → 登录（密码 = 家里 WiFi 密码）→ **更多功能 → Wi-Fi 设置 → Wi-Fi 防蹭网 → 黑名单列表** → 找到 `OPENDUCKMINI-V108` (`B8:27:EB:0D:F0:CD`)→ 点 **移除**。

### Step 2（用户操作鸭子）：物理重启

鸭子背后物理开关：关 → 等 10 秒 → 开 → 等 1~2 分钟让鸭子完整 boot。

### Step 3（PC 上验证）：SSH 测试

```
ssh raspios@192.168.3.166
```

密码 `raspios`。⚠️ Clash Verge TUN 模式拦 ICMP（ping 不通是正常的），但 TCP/SSH 应该能通。

### Step 4（验证修复成功的标志）

- ✅ SSH 一秒进 → 修复完成，进入 Step 5
- ❌ SSH timeout 但鸭子 `openduckmini` 热点出现了 → 说明 80 秒还不够 / 黑名单没移除 / 信号弱，进 fallback 排查
- ❌ SSH timeout 且 `openduckmini` 也没出现 → 罕见，说明鸭子 boot 卡死，得物理重启再来一遍

### Step 5（S0 阶段后续工作）：验证 py-xiaozhi 服务

SSH 通后立即检查 OpenDuck Runtime 状态：

```bash
sudo systemctl --failed
systemctl is-active wifi_or_ap
ps -ef | grep -E 'xiaozhi|duck' | grep -v grep
ls /home/raspios/open_duck_mini_ws/
ls /home/raspios/tools/commands/
```

接下来按用户在 [`docs/openduckmini-knowledge-from-share-2026-05-04.md`](./openduckmini-knowledge-from-share-2026-05-04.md) 里规划的 **S0 → S1 路径** 推进：跑通整机用爱折腾出厂 py-xiaozhi → xiaozhi.me 后端，整套不动。

---

## 📋 关键事实（5 秒上下文恢复用）

### 鸭子身份

| 字段 | 值 |
|---|---|
| Hostname | `OPENDUCKMINI-V108` |
| MAC（家里网络） | `B8:27:EB:0D:F0:CD` (Pi 基金会官方 OUI) |
| Kernel | Linux 6.12.25+rpt-rpi-v8 aarch64 (2025-04-30) |
| 家里 WiFi 网段下 IP | `192.168.3.166` (DHCP) |
| 热点模式 IP | `192.168.12.1` (固定) |
| 热点 SSID | `openduckmini` (无密码，rfc 7858 风格) |
| SSH user/pass | `raspios` / `raspios` |
| Python venv | `(venv_duck)` 自动激活在 raspios shell |

### 网络环境

| 字段 | 值 |
|---|---|
| 路由器 | 华为 AX2 Pro (WS7000 V2)，固件 3.0.3.215 |
| 家里 WiFi 网段 | `192.168.3.0/24`，网关 `192.168.3.1` |
| 家里 WiFi 频段 | 5GHz channel 157 (U-NII-3，非 DFS) |
| WiFi SSID | `1101_5G` |
| WiFi 密码 | 已存在鸭子 web 服务面板的"配置 wifi"启动命令里 + 已写入 `/etc/wpa_supplicant/wpa_supplicant-wlan0.conf` |
| PC IP | `192.168.3.41` (Wi-Fi 6E AX211) |
| PC VPN | Clash Verge Rev (Mihomo Meta TUN)，**ICMP 被拦但 LAN TCP DIRECT 通**——别再被 ICMP 误导 |

### Web 服务面板

`http://192.168.12.1:5051` （仅在鸭子热点模式下可访问，由 gunicorn 跑在 `/home/raspios/tools/commands/commands_web/`）。预存了 8 个"服务"按钮：
- 配置 wifi（命令：`set_wifi.sh 1101_5G <密码>`）⚠️ 跑这个会重启 wpa_supplicant，破坏现有热点 SSH 会话
- 配置固定 IP / 重启树莓派 / 关闭树莓派
- duck_test / duck_mcp / duck_test_with_mcp / check_sounds

---

## 🔧 已应用的鸭子端修改

修改了 **`/home/raspios/tools/network/wifi_or_ap.sh`** 两处（已备份到 `.orig`）：

| 行号 | 原内容 | 新内容 | 作用 |
|---|---|---|---|
| 5 | `TIMEOUT=10` | `TIMEOUT=80` | 给 wpa_supplicant 80 秒做 5GHz 关联+DHCP（U-NII-3 通常需 13-25s，留 2x 余量） |
| 57 | `        yes y \| /home/raspios/tools/network/remote_current_wifi.sh` | `        sudo systemctl stop wpa_supplicant.service wpa_supplicant@wlan0.service 2>/dev/null \|\| true` | fallback 时只停 wpa_supplicant 释放 wlan0，不再清空 SSID/PSK |

写入了 **`/etc/wpa_supplicant/wpa_supplicant-wlan0.conf`**：含 `1101_5G` SSID + 密码 + `country=CN` + `WPA-PSK`。

### 验证修改是否还在（任何时候都可以跑）

```bash
grep -nE 'TIMEOUT|systemctl stop wpa|remote_current_wifi' /home/raspios/tools/network/wifi_or_ap.sh
```

期待输出：
```
5:TIMEOUT=80
57:        sudo systemctl stop wpa_supplicant.service wpa_supplicant@wlan0.service 2>/dev/null || true
```

⚠️ 不应该再有 `# DISABLED` 或 `remote_current_wifi.sh` 出现。如果出现，说明 web 上有人误点了"配置 wifi"或 wifi_or_ap.sh 被重置了。

---

## 🛡️ Fallback Safety（重要）

修改后的 wifi_or_ap.sh **保证以下 5 种 WiFi 失败场景都能稳定回到 `openduckmini` 热点**（用户唯一的远程通道）：

| 失败场景 | 行为 |
|---|---|
| 信号丢失 / 出门搬家 | 80s timeout → stop wpa_supplicant → create_ap 起热点 |
| 路由器拒绝（黑名单/MAC 过滤）| 同上 |
| 密码错误 | 同上 |
| DHCP 超时 | 同上 |
| 弱信号 80s 还连不上 | 同上 |

**关键改进**：之前 fallback 会清空 SSID/PSK，导致每次重启都重蹈失联覆辙；现在 fallback 不清配置，下次 boot 仍能尝试连家里 WiFi。

---

## 🧨 故障背景一页纸（如果新会话需要理解）

**用户报告的现象**：5 月 10 日开始，配置家里 WiFi 后鸭子能在路由器上"看到在线"但任何 TCP 连接全 timeout，0 Kbps 流量持续。

**走过的弯路**（耗时 ~4 小时）：
1. 一开始误诊为 sshd 5 秒 close（实际是 Clash TUN 假阳性）
2. 误诊为 NetworkManager 接管（实际是 systemd-networkd + wpa_supplicant + 自定义脚本）
3. 误诊为路由器 AP 隔离（华为 AX2 Pro 没这个开关）

**真正的根因**（铁证 systemd journal）：

```
14:54:00  wifi_or_ap.service 启动
14:54:14  (10 秒到点) try_wifi_connect 失败  ← TIMEOUT 太短
14:54:14  yes y | remote_current_wifi.sh 执行  ← 自爆清空 SSID
14:54:14  Network services restarted. WiFi info cleared.
14:54:14  [WARN] WiFi check failed, starting create_ap service...
14:54:16  wlan0: AP-ENABLED  ← create_ap 接管
```

但 wpa_supplicant 在第 4 步前已关联到 1101_5G、拿到 IP 192.168.3.166（路由器 ARP cache 已记），create_ap 接管后 wlan0 在 hostapd master 模式 → 路由器到 192.168.3.166 的 TCP 包被丢弃 → "假装在线但全 timeout"。

**绕路诊断手段**：把鸭子 MAC 加入路由器 Wi-Fi 防蹭网黑名单 → 强迫鸭子触发 fallback 进 `openduckmini` 热点 → 用户手机连热点用 termux ssh 进鸭子（这是用户唯一可用的诊断通道，没有 HDMI 显示器）。

---

## 📧 已发邮件

诊断报告 + 给商家的改进建议已发到 `qingxun.zhu@qq.com`。用户会自己转发给爱折腾。给商家提的 3 条必须改进：

1. wifi_or_ap.sh 默认 TIMEOUT 改 60s+
2. fallback 不要清空 wpa_supplicant-wlan0.conf
3. fallback 切 AP 前先 stop wpa_supplicant

---

## 📁 相关文件

| 用途 | 路径 |
|---|---|
| 当前文档 | `docs/s0-handoff-wifi-fix.md`（本文件）|
| 上次 milestone 接手 | `docs/m0-handoff-notes.md` |
| OpenDuckMini 知识库 | `docs/openduckmini-knowledge-from-share-2026-05-04.md` |
| 卖家聊天 OCR | `docs/seller-chat-aizheteng.md` |
| 卖家发的 ncnynl 教程 #6810 | https://www.ncnynl.com/archives/202507/6810.html |

鸭子端关键路径：
- `/home/raspios/tools/network/wifi_or_ap.sh`（已改）+ `.orig` 备份
- `/home/raspios/tools/network/{set_wifi,set_static_ip,remote_current_wifi}.sh`
- `/home/raspios/tools/commands/commands_web/`（5051 web 服务源码）
- `/home/raspios/open_duck_mini_ws/`（OpenDuck Runtime 工作区）
- `/etc/systemd/system/wifi_or_ap.service` + `unblock-wifi.service` + `wifi-power-fix.service`
- `/etc/wpa_supplicant/wpa_supplicant-wlan0.conf`（已改）+ `.bak`（爱折腾历史备份，已是清空版）

---

## 🆘 万一新会话也修不好怎么办

**不要着急走 SD 卡重刷的核选项**。先按以下顺序排查：

1. **绕路通道还在吗**：鸭子 MAC 仍在路由器黑名单时（如未移除），鸭子 boot 必然进热点 → SSH 永远可达
2. **如果黑名单已移除但鸭子失联**：手动加回 MAC 到黑名单 → 强迫鸭子 fallback 进热点 → 重新诊断
3. **如果热点也起不来**：唯一物理通道是 HDMI 显示器 + USB 键盘（用户当前没有）。最后选项 = 联系爱折腾客服远程支持。

**关键不变量**：只要 wifi_or_ap.sh 的修改保持，鸭子失联是可恢复的（路由器拉黑名单 → fallback → SSH）。

---

**接手指引**：新会话开始时，先读本文件 + Step 1-5；如用户已完成 Step 1-2 且 SSH 不通，跳到「万一新会话也修不好」排查；如 SSH 已通，直接进入 Step 5 S0 工作。
