# 鸭子 PS4 (DS4) 手柄连接 — ds4drv 驱动恢复

**创建**: 2026-06-07 (系统重置后重配手柄会话)
**状态**: ds4drv 已修复能建 js0 + 连上手柄; 卡在蓝牙信号弱(14 reports/s), 待手柄充电后验证

> ⚠️⚠️ **本文档根因已过时, 待改写 (2026-06-07 晚更新, 见 `rpiv/handoff-2026-06-07-v8.md`)** ⚠️⚠️
> - 真根因**不是**"信号弱"也**不是** ds4drv 问题。手柄已彻底连通 + reboot 持久化验证通过(js0 真实输入 125 事件/6秒)
> - **不需要 ds4drv**: 内核 `hid_sony` + `joydev`(modules-load.d 自启)直接建 js0
> - 真手柄 MAC = `A0:5A:5F:0A:0F:2C`(btmon 实锤); 是**副厂 DS4**(PID 漂移 + inquiry 扫不到只能 page)
> - 连通方式: `bt-agent -c NoInputNoOutput`(Just Works) + `hcitool cc` 直连 + `bluetoothctl pair`
> - **但"标准 bluetoothctl 撞 MITM"这个结论尚未对照验证**(我测的是一次性命令, 卖家官方文档 ncnynl 6745 用的是交互式 shell, 待复核)
> - 下方"信号弱/转 USB"等内容**全部作废**, 仅作历史保留

---

## 一、核心原理 (2026-06-07 完整诊断, 多假设逐一验证后锁定)

### js0 唯一来源 = ds4drv (不是内核)

- 鸭子内核**没有 joydev 模块**: `modules.builtin` 只有 `hid-generic.ko`; `modinfo joydev/hid_sony/hid_playstation` 全部无 filename
- 所以**内核无法创建 `/dev/input/js*`** —— 不管蓝牙连不连、重不重启都不会有 js0
- vendor 代码 (`Open_Duck_Mini_Runtime/.../ps4_controller.py`) 用 `pygame.joystick.Joystick(0)` 读 `/dev/input/js0`
- **js0 必须由 `ds4drv` 用 uinput 创建** (`99-uinput.rules` 给 uinput 权限)
- ds4drv 在 `/usr/local/bin/ds4drv` v0.5.1 (系统级 pip 装)

### 关键陷阱 1: ds4drv 因 evdev 版本不兼容崩溃 (已修复)

- ds4drv 0.5.1 (2017) 用 python-evdev 旧 API `.fn`, 但系统 evdev 是 **1.9.2**, 新版把 `InputDevice.fn` 改名成 `.path`
- 崩溃点: `/usr/local/lib/python3.11/dist-packages/ds4drv/actions/input.py` **line 84** `joystick.device.device.fn`
- 报错: `AttributeError: 'InputDevice' object has no attribute 'fn'. Did you mean: 'fd'?`
- **修复 (已应用)**: 把该行 `.fn` 改成 `.path` (只是 logger.info 日志语句, 不影响逻辑)
  - 原文件已备份: `input.py.bak-guagua`
  - patch 后 ds4drv 正常启动, 立即创建 `/dev/input/js0` + `/dev/input/event2`

### 关键陷阱 2: `pkill -f ds4drv` 自杀

- ssh 执行的命令字符串里含 "ds4drv" 几个字, `pkill -f ds4drv` 匹配**完整命令行**, 会把**正在执行这条命令的 shell 自己杀掉** → 命令在那一行中断
- 这曾导致多次 ds4drv "启动失败" (实际是命令被自杀截断, 后面没执行到)
- **禁止用 `pkill -f ds4drv`**; 清进程用精确 unit 名 (`systemctl stop ds4drv-tmp`)

### 手柄特性 (用户实测, 非标准)

- **长按 PS 单键 → 白灯双闪配对模式** (⚠️ 本手柄 Share+PS 无反应, 与标准 DS4 相反)
- 灯色: ds4drv 默认**不设蓝色 LED** → 连上是**白色常亮** (蓝灯需 `--led` 参数)。**灯色不是接管成功的标志**, 以 ds4drv 日志 `Connected to` + `Battery:` 为准

---

## 二、正确启动 + 连接流程

### 启动 ds4drv (systemd-run, 完全 detach)

`nohup`/普通后台在 ssh 下会被 hold 住, 用 systemd-run 最可靠:

```
sudo systemctl stop ds4drv-tmp 2>/dev/null; sudo systemctl reset-failed ds4drv-tmp 2>/dev/null
sudo systemd-run --unit=ds4drv-tmp --collect ds4drv
sleep 3
systemctl is-active ds4drv-tmp    # active
ls /dev/input/js0                 # ds4drv 在跑就有
```

### 连接手柄

1. ds4drv 跑着 + 蓝牙 controller on (`bluetoothctl power on`)
2. **长按 PS 键进白灯双闪** (保持别松)
3. ds4drv 日志依次出现: `Found device A0:5A:5F:0A:0F:2C` → `Connected to Bluetooth Controller` → `Battery: NN%`
4. 验证 js0 输入: `sudo timeout 6 jstest --event /dev/input/js0` (拨摇杆/按键, 看有无 `type 1`/`type 2` 实时事件; `type 129/130` 是 INIT 快照不算)

---

## 三、当前卡点 (2026-06-07, 待手柄充电后验证)

**进展**: ds4drv 能连上手柄 (`Connected` + `Battery` 读数), js0 设备完全正确 (jstest 识别 `Sony Computer Entertainment Wireless Controller`, 14 axes + 14 buttons, 正是 vendor 需要的)

**卡点**: 蓝牙信号弱 **14 reports/s** (正常 60+) → 手柄按键**无实时反应** (jstest 只有 INIT 事件)

**已排除的假设** (不要重走):
- ❌ joydev 缺失 (内核本就无, js0 靠 ds4drv)
- ❌ uhid 缺失 (`/dev/uhid` 存在, 内核内置)
- ❌ 按键方式错 (用户一直按 PS 双闪, 正确)
- ❌ 灯色判断 (白灯=ds4drv默认不设LED, 不代表没接管)
- ❌ bluetoothd 争用带宽 (disconnect bluetoothd 后 ds4drv 也断 = **共享同一连接**, 非争用)

**真实根因方向**: 蓝牙链路质量问题, 软件解决不了。**旁证**: 手柄电量掉异常快 (75%→62%→50% 几分钟) → 疑**电池老化**, 供电不足导致蓝牙发射弱

**用户决定**: 先把手柄充满电再试蓝牙

---

## 四、充电后继续步骤

1. 确认 ds4drv 跑着: `ssh duck "systemctl is-active ds4drv-tmp"` (没跑则用上面 systemd-run 重启)
2. 长按 PS 双闪, 监控 ds4drv: `ssh duck "sudo journalctl -u ds4drv-tmp --no-pager | tail"` 看 `Connected` + reports/s
3. 关键看 **reports/s 是否回到正常 (60+)**, 然后采样 js0 看按键有无 `type 1`/`type 2` 实时事件
4. **若仍 14 reports/s** → 转 USB 有线: micro-USB **数据线**(非纯充电线)插 DS4 到鸭子 → 内核 hid_generic 接管出 hidraw → `ds4drv --hidraw` 读它建 js0 → 稳定 60+/s, 绕过蓝牙

---

## 五、⚠️ 持久化提醒 (系统重置会丢这些)

- ds4drv 的 `.fn→.path` patch 在鸭子端文件系统, **系统重置会丢失**
- 整盘镜像备份 `D:\duck-backup\duck-env-initial-2026-06-07.img.zst` 是**本次 patch 之前**的, **不含此 patch**
- ds4drv 当前也**没配开机自启** (systemd-run 是临时 transient unit, reboot 后消失)
- **TODO** (手柄跑通后做): 把以下纳入 `scripts/duck-post-reset-fix.ps1` 或新建 ds4drv systemd service:
  1. 重施 ds4drv input.py 的 `.fn→.path` patch
  2. 配 ds4drv 开机自启 (systemd unit, `ds4drv --hidraw` 或蓝牙模式)
  3. 这样 reboot / 重置后手柄自动可用
