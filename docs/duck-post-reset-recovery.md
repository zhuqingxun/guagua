# 鸭子系统重置 / 重刷卡后的完整恢复 SOP

**最后更新**: 2026-06-06
**适用场景**: 鸭子(爱折腾整机版 OPENDUCKMINI-V108, Pi 3B+)被寄修/重置/重刷 SD 卡后, 出厂态需要重新配网 + 重施系统修复
**触发关键词**: 鸭子重置 / 系统重置 / 重刷卡 / 寄修回来 / WiFi 重新配 / 从头开始配网

> ## ⚠️ 最重要的一条 (配 WiFi 时务必记住)
>
> **填家里 2.4G WiFi `1101`, 绝对不要填 5G `1101_5G`!**
>
> 华为 AX2 Pro 路由器在 **5GHz channel 157** 上会拦截局域网内 22 端口 SSH 包。连 5G 会出现"路由器显示鸭子在线、但 SSH 全 timeout"的假象, 上次为此耗了约 4 小时。商家 web 配网面板让你手动填 WiFi 名, **没有 2.4G/5G 提示**, 全靠你自己填对。

---

## 完整恢复三步

### Step 1: web 配 WiFi (热点模式, 无法脚本化)

1. 鸭子开机, 没连上家里网时会自动起 `openduckmini` 热点(无密码)
2. 用手机或另一台 PC **连 `openduckmini` 热点**
3. 浏览器打开 `http://192.168.12.1:5051`
4. 找"配置 wifi", 填 **`1101`**(2.4G) + 家里 WiFi 密码, 更新服务
5. 鸭子尝试连 1101, 成功后关热点, 拿到家里网 IP(DHCP, 通常 `192.168.3.166`)

> 教程出处: https://www.ncnynl.com/archives/202507/6810.html

### Step 2: 部署 SSH 免密通道

PC 端(连家里网)运行, 输一次密码 `raspios`:

```
pwsh D:\CODE\guagua\scripts\deploy-ssh-key-to-duck.ps1
```

成功后 `ssh duck` 免密直达(ssh config 已配 `Host duck` -> `raspios@192.168.3.166`)。

> ⚠️ 重置后鸭子 SSH host key 会变, 若 PC 端 `ssh` 报 "HOST IDENTIFICATION CHANGED", 先跑 `ssh-keygen -R 192.168.3.166` 清旧指纹。

### Step 3: 一键重施系统修复

PC 端运行(幂等, 可重复跑):

```
pwsh D:\CODE\guagua\scripts\duck-post-reset-fix.ps1
```

重施三项(详见下方"修复项"), verify 全过即完成。可选 reboot 终验开机自动连。

---

## 修复项(脚本 duck-post-reset-fix.ps1 做的事)

| # | 修复 | 根因 | 做法 |
|---|------|------|------|
| 1 | WiFi fallback `TIMEOUT` 10→60 | 出厂 10 秒太短, 易误判连不上触发 fallback | 只改 `wifi_or_ap.sh` 第 5 行 TIMEOUT, **fallback 逻辑保持出厂不动** |
| 2 | DNS 静态化 + 锁定 | 出厂电信 DNS `202.96.128.x` 不通, networkd 配了被墙的 `8.8.8.8` | 写静态 `resolv.conf`(阿里 `223.5.5.5` + 路由器 `192.168.3.1`) + `chattr +i` 锁定; 改 `10-wlan0.network` 的 8.8.8.8 |
| 3 | NTP 阿里源 | 默认 `2.debian.pool.ntp.org` 国内偶发不通, 时钟不同步 | `timesyncd.conf` 加 `NTP=ntp.aliyun.com cn.pool.ntp.org` |

---

## ⭐ Fallback 方案决策记录 (2026-06-06, 关键, 勿改)

**结论: WiFi 连不上时, 用出厂的"清配置 + 起热点"路径, 只延长 TIMEOUT。不要改成"不清配置"。**

### 背景

出厂 `wifi_or_ap.sh` 的 else 分支(WiFi 连不上时)做两件事:
1. `yes y | remote_current_wifi.sh` —— **清空** `wpa_supplicant-wlan0.conf` 的 ssid/psk
2. `create_ap --no-virt wlan0 lo openduckmini ""` —— 起 `openduckmini` 热点

### 曾经的诱惑(已否决)

5/10 一份**已过时**文档(`s0-handoff-wifi-fix.md`)设计过"不清配置"改法(把第 1 步换成只 `stop wpa_supplicant`), 理由是"临时故障(路由器重启)后下次 boot 能自动重连, 不用 web 重配"。2026-06-06 会话一度照搬了它。

### 为什么否决(用户拍板)

- **"不清配置 → 起热点"这条路径从未实测过** —— 出厂的"清配置(含 restart wpa_supplicant/networkd)→ create_ap"可能是 create_ap 能干净接管 wlan0 的前提, 换成 stop wpa 是未验证的
- **赌注是"唯一访问入口"** —— 鸭子无 HDMI, `openduckmini` 热点是断网后唯一的进入方式, 不能拿它赌一条没验证的路径
- **出厂路径今天刚被实际验证可靠** —— 用户开机就是走出厂 fallback 起热点后 web 配网成功的
- **用户风险偏好明确**: 宁可永久故障后每次 reboot 要 web 重配(麻烦但 100% 可靠回热点), 也不要"自愈便利"换"可能失联"

### 最终方案

- 保留出厂 fallback(清配置 + 起热点)完全不动
- **只**把 `TIMEOUT` 10→60, 减少"误判连不上"的概率
- 正常情况(60 秒内连上, 实测 reboot 后 18 秒就连上): 不触发 fallback, 配置保留, 开机自动连
- 真连不上 ≥60 秒: 出厂路径清配置 + 起热点, 用户连热点 web 重配, 入口 100% 保住

---

## 踩过的坑速查

| 坑 | 症状 | 真因 | 修复 |
|----|------|------|------|
| 5G channel 157 拦 SSH | 路由器显示在线但 SSH 全 timeout | 华为 AX2 Pro 在 5G ch157 spoof RST 拦 22 端口 | 连 2.4G `1101`, 别连 `1101_5G` |
| 电信 DNS 不通 | `ping IP` 通但 `ping 域名` / 时钟不同步 失败 | 出厂 `resolv.conf` 配电信 `202.96.128.x` 不通 | 静态 DNS 阿里+路由器 + chattr 锁定 |
| 时钟不同步 | `synchronized: no`, 时间停在旧日期 | Pi 无 RTC + 默认 debian NTP 国内不通 | NTP 改阿里源(DNS 修好后才生效) |
| fallback 自爆(误解) | 以为"不清配置"更优 | 实为未验证路径, 赌唯一入口 | 见上方决策记录: 用出厂路径 |

---

## 验证清单 (恢复后逐项确认)

```
ssh duck 'ip -br addr show wlan0'          # 应: wlan0 UP 192.168.3.166 (station)
ssh duck 'getent hosts baidu.com'          # 应: 返回 IP (DNS 通)
ssh duck 'timedatectl | grep synchron'     # 应: synchronized: yes
ssh duck 'grep -nE "TIMEOUT|create_ap --no-virt|remote_current" /home/raspios/tools/network/wifi_or_ap.sh'
# 应: TIMEOUT=60 + remote_current_wifi.sh(1处) + create_ap(1处) 都在
```

reboot 终验(可选): `ssh duck 'sudo reboot'` 后约 18 秒 `ssh duck` 应自动恢复 = 开机自动连成功。

---

## 相关文件

| 文件 | 用途 |
|------|------|
| `scripts/deploy-ssh-key-to-duck.ps1` | Step 2 部署 SSH key |
| `scripts/duck-post-reset-fix.ps1` | Step 3 一键重施系统修复(幂等) |
| `docs/troubleshoot-2026-05-10-huawei-5g-channel157-blocking-ssh.md` | 5G 拦截坑的完整诊断过程 |
| `docs/s0-handoff-wifi-fix.md` | ⚠️ 已过时(fallback 不清配置那版), 仅作历史 |
| `~/.claude/rules/raspberry-pi-debugging.md` | 全局 Pi 调试规则(journal/NTP/取证) |

鸭子端关键路径:
- `/home/raspios/tools/network/wifi_or_ap.sh`(+ `.guagua-orig` 出厂备份)
- `/etc/wpa_supplicant/wpa_supplicant-wlan0.conf`(web 配网写入 1101)
- `/etc/resolv.conf`(静态 + chattr +i)
- `/etc/systemd/timesyncd.conf`(阿里 NTP)
- `/etc/systemd/network/10-wlan0.network`(DNS 已改)
