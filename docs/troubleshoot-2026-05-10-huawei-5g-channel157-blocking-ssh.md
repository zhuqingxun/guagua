# 华为 AX2 Pro 5GHz channel 157 LAN 内 SSH 拦截事件

**生成日期**：2026-05-10
**状态**：已解决（切 2.4G 修复）
**总耗时**：约 3 小时（含两个会话）
**Milestone 影响**：S0 阶段卡死 → 解除

---

## TL;DR

家里华为 AX2 Pro 路由器在 **5GHz channel 157** 上对 LAN 内同段 22 端口 TCP 包做 spoof RST 拦截。鸭子（Pi 3B+）连家里 5G WiFi `1101_5G` 后获得 192.168.3.166 IP，但 PC (192.168.3.41) → 鸭子 22 端口的 TCP 流量在路由器中段被假冒 RST，包从未到达鸭子的 wlan0 接口。**修复 = 把鸭子 wpa_supplicant SSID 从 `1101_5G` 改为 `1101`（2.4G）**。

---

## 故障现象

PC 端 PowerShell：
```
ssh raspios@192.168.3.166
Connection closed by 192.168.3.166 port 22
```
或者：
```
ssh: connect to host 192.168.3.166 port 22: Connection timed out during banner exchange
```

并发特征：
- 路由器后台显示鸭子在线 192.168.3.166 0/0 Kbps
- TCP 握手"成功"（`Test-NetConnection ... Port 22` 返回 True）
- ping 不通（同时受 Clash TUN 拦 ICMP 干扰，但即使 PC 关 Clash 仍不通）
- 手机连 1101_5G WiFi 试 ssh 鸭子也是同样症状（排除 PC 因素）

唯一可达通道：手机连鸭子的 fallback `openduckmini` 热点 (192.168.12.1)，走 hostapd 直连。

---

## 走过的弯路（假设 → 排除）

| # | 假设 | 排除证据 |
|---|---|---|
| A | tcpwrapper `/etc/hosts.deny` 拒绝 192.168.3.0/24 | 文件全注释，无活动规则 |
| B | iptables INPUT 链 REJECT/DROP | `iptables -S` 全 ACCEPT，无规则 |
| C | 22 端口被非 sshd 进程占 | `ss -tlnp` 确认 sshd pid=574 listen 22 |
| D | wifi_or_ap.sh 反复 station↔AP 翻转 | journal 显示 `WiFi is working, no need to start AP` 干净退出 |
| E | sshd MaxStartups 半开连接耗尽 | `0 of 10-100 startups`，nstat ListenOverflows=0 |
| F | sshd UseDNS=yes 反查 hang | 改 UseDNS no + 重启 sshd 后症状不变 |
| G | 22 端口实际不是 sshd | `ss -tlnp` 显示 sshd pid=574 fd=3,4 |
| H | 路由器 LAN 客户端隔离 | UI 找不到对应开关，但**最终证据指向同方向** |
| I | 鸭子 kernel netfilter drop | conntrack 22 完全空，nstat TcpOutRsts=0 |

---

## 真因定位的关键证据

部署 boot-time 自动诊断框架（`/usr/local/bin/duck-debug.sh` + `duck-debug.service`），在鸭子 station 模式期间自动采集 5 分钟数据：

**鸭子 5G station 模式 5 分钟内**（PC PowerShell 同步发了 5 次 SSH）：
- `ss tcp 22` → 全 4 次 iter 只有 LISTEN 状态，零 SYN_RECV/ESTABLISHED
- `pgrep sshd` → 全程 `0 of 10-100 startups`（零 child fork = sshd 没收到 connection）
- `/proc/net/nf_conntrack | grep 22` → **完全空**
- `nstat`：TcpOutRsts=0, TcpExtListenOverflows=0, TcpExtListenDrops=0, TCPAbortOn{Data,Close,Memory,Timeout,Linger,Failed} = 0

**双向钳制结论**：
- 鸭子 kernel 完全没看到 PC 的包 → 包没到 wlan0
- PC 看到的 RST/timeout 不是鸭子发的（鸭子 nstat TcpOutRsts=0）
- 既然 TCP 握手 PC 看到"成功"，那 SYN-ACK 一定是路由器 spoof 的
- → **包被路由器拦截 + 路由器 spoof RST 给 PC**

唯一遗憾：tcpdump 没装在鸭子上（脚本 fallback 设计漏洞），缺 wlan0 包级证据。但内核三重证据（ss + conntrack + nstat）已足够锁定。

---

## 验证修复

### 操作

鸭子端单行：
```bash
sudo sed -i 's/ssid="1101_5G"/ssid="1101"/' /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
```

然后路由器移除黑名单 + 关→开重启鸭子。

### 验证证据

PC PowerShell 5 次循环：
- 第 1 次：`Connection timed out`（鸭子还没 boot 完）
- 第 2-5 次：**`Permission denied (publickey,password)`** ← sshd 完整工作

`Permission denied` 是 sshd 在 BatchMode 拒绝交互密码时发的，意味着 TCP→banner→kex→auth 全流程 OK，仅 auth 失败。手动 SSH 输密码立刻登入 ✅。

---

## 防御性措施（永久）

1. **2.4G 配置已永久写入 `/etc/wpa_supplicant/wpa_supplicant-wlan0.conf`**，5G 配置备份在 `.5g.bak` 同目录
2. **保留 `UseDNS no`** 在 `/etc/ssh/sshd_config.d/99-debug.conf`（避免未来 station 模式 sshd DNS 反查 hang）
3. **保留 `/usr/local/bin/duck-debug.sh` + `duck-debug.service`** 但 `disable`（boot 不自启），未来再有同类问题 `systemctl enable --now duck-debug.service` 一秒启用
4. **保留 `/var/log/journal/` persistent journal**（已 `Storage=persistent`）

---

## 给爱折腾的反馈点

ncnynl.com 教程默认假设家里 WiFi 都能正常 SSH，未提到部分华为路由器 5GHz 信道 157 上对 LAN 内 22 端口的拦截 bug。建议：
- 装机文档加一行"如果 5G WiFi SSH 不通，先试 2.4G"
- wifi_or_ap.sh 默认 SSID 模板用 2.4G（兼容性更广）

---

## 鸭子时钟问题（次生发现，未修）

`timedatectl` 显示 `System clock synchronized: no`，鸭子时钟卡在 5/6（实际今天 5/10）。
- Pi 3B+ 没有 RTC
- AP 模式无外网无法 NTP 同步
- 当前 `/etc/systemd/timesyncd.conf` 用的 NTP server 在 station 模式下也未同步成功（推测：默认 `2.debian.pool.ntp.org` 在中国偶发不通）

**修复建议**（S0 阶段做）：改 `/etc/systemd/timesyncd.conf` 加 `NTP=ntp.aliyun.com cn.pool.ntp.org`。

---

## 经验沉淀

详见 [`~/.claude/rules/raspberry-pi-debugging.md`](~/.claude/rules/raspberry-pi-debugging.md)，本次事件的核心教训：

1. **取证设施先建好再做"复现循环"**，否则白跑用户时间。本次因 journal volatile + 没装 tcpdump 多绕了 2 轮
2. **journal Pi OS 默认 `Storage=volatile`**，仅 mkdir 不够，必须显式 `Storage=persistent` + `--flush --rotate` + 验证 `.journal` 文件落盘
3. **bash -c 链里 journalctl/systemctl 必须 --no-pager**，否则 less 吞掉后续命令静默失败
4. **诊断脚本设计假设"下次 SSH 进不来"**：所有输出 `tee` 到 `/var/log/` 持久文件，不只 stdout 一次
5. **LAN 内 SSH 不通时，鉴别"包到没到鸭子"的内核三重证据**：`ss <port>` 状态 + `cat /proc/net/nf_conntrack | grep <port>` + `nstat | grep -iE "Listen|Rst|Abort"`。三个都空 = 包没到，问题在中间网络
6. **PC 看到的 RST 不一定是 server 发的**——LAN 内中间路由器可能 spoof，必须看 server 端 nstat 才能反证

---

## 上下游影响

- **解除阻塞**：S0 阶段（py-xiaozhi 整机调试）原本依赖 SSH 进鸭子，现已可达
- **下次接手**：直接 `ssh raspios@192.168.3.166`，密码 `raspios`
- **如果未来再不通**：先确认是不是有人误把 wpa_supplicant SSID 改回 `1101_5G` 了；其次把鸭子加路由器黑名单 + 关→开 → 进 AP → 手机连 `openduckmini` SSH 进鸭子 → 启用 duck-debug 服务复诊

---

## 相关文件

| 用途 | 路径 |
|---|---|
| 本文档 | `docs/troubleshoot-2026-05-10-huawei-5g-channel157-blocking-ssh.md` |
| 上一接手文档 | `docs/s0-handoff-wifi-fix.md`（已过时，本文档替代） |
| 全局规则 | `~/.claude/rules/raspberry-pi-debugging.md` |
| 诊断脚本源 | `scripts/duck-debug.sh` + `scripts/duck-debug.service` |
| 一行 install | `scripts/duck-debug-install.txt` |

鸭子端关键文件：
- `/etc/wpa_supplicant/wpa_supplicant-wlan0.conf`（已改 1101，备份在 `.5g.bak`）
- `/etc/ssh/sshd_config.d/99-debug.conf`（仅含 `UseDNS no`）
- `/etc/systemd/journald.conf`（`Storage=persistent`）
- `/var/log/journal/<machine-id>/`（持久化日志已落盘）
- `/usr/local/bin/duck-debug.sh` + `/etc/systemd/system/duck-debug.service`（保留，已 disable）
