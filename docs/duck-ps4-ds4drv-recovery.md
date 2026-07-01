# 鸭子 PS4 (DS4) 手柄连接 — 根因最终结论 + 标准恢复流程

**最后更新**: 2026-07-01（根因复核完成 + 真机走路验证通过）
**状态**: ✅ 根因已锁定并复核，标准流程已固化，走路测试通过

> 本文档此前(2026-06-07)有两版错误假设("蓝牙信号弱/需转 USB"、"需要 ds4drv 驱动")，均已否定。历史假设不再保留在本文档中，需要考古见 git blame（关键词 `ds4drv` / `信号弱`）。以下是唯一权威结论。

---

## 一、核心事实

| 项 | 值 |
|---|---|
| 真手柄 MAC | `A0:5A:5F:0A:0F:2C`（btmon 实锤，17 次主动 Connect） |
| 硬件性质 | **副厂 DS4 兼容手柄**（`Modalias: usb:v054Cp05C4d0100`，PID 会在 05C4/09CC 间漂移） |
| 蓝牙可发现性 | **inquiry scan 扫不到**（`btmgmt find` / `hcitool scan` / `bluetoothctl scan on` 全部失败，贴 5cm 也不行）。但**可 page（可被动接受连接）** |
| 手柄配对模式 | Share + PS 同时长按至指示灯**快速闪烁** |
| js0 来源 | **内核原生** `hid_sony` + `joydev`（由 `/etc/modules-load.d/duck-ps4.conf` 开机自启加载）直接创建，**不需要 ds4drv** |

## 二、真正的根因：Bonded vs Paired

这是整个 saga 最终定位到的关键机制，此前所有失败/困惑都由此解释：

1. **`scan on` 扫不到手柄是正常的**——这台副厂 DS4 不回应 inquiry。但这**不影响连接**：手柄在"快速闪烁"配对模式下会**自己主动发起连接**（page）到鸭子，此时 `bluetoothctl` 会看到设备以 `[NEW]` 形式出现，`connect <MAC>` 直接可用。
2. **真正决定成败的是 SSP 协商时的 Authentication 标志位（Bonding + MITM）**，不是"用了哪个 agent 工具"：
   - 如果 host 端 IO Capability Reply 携带 **`MITM required`**：这台手柄的固件会在 IO Capability Response 阶段**卡住不回应**（btmon 看到 host 发完 6.4 秒超时）→ `Simple Pairing Complete: Authentication Failure (0x05)`
   - 如果 host 端携带 **`No Bonding`**（例如用交互式 `bluetoothctl` 默认 agent，走卖家官方教程 ncnynl 6745 的标准四步 `scan on`→`pair`→`trust`→`connect`）：手柄能顺利回应并完成 SSP，`bluetoothctl info` 显示 **`Paired: yes` 但 `Bonded: no`**——**看起来连上了，但这个配对是临时会话级的，不会写入 `/var/lib/bluetooth` 的持久 link key**
   - 只有携带 **`General Bonding`**（用 `bt-agent -c NoInputNoOutput` 显式声明 Just Works 能力）才能拿到真正持久化的 `Bonded: yes` + 写入磁盘的 link key
3. **`bluetoothd` 的 HID input profile 插件会拒绝为非 bonded 设备建立 HIDP 连接**，实测日志实锤：
   ```
   profiles/input/device.c:hidp_add_connection() Rejected connection from !bonded device A0:5A:5F:0A:0F:2C
   ```
   这就是为什么"卖家官方教程走一遍显示 Connected: yes"，但 `/dev/input/js0` 死活不出现——**能连接 ≠ 能当作 HID 输入设备用**，两者是 bluetoothd 内部两个独立的判定关卡。

**结论**：卖家官方文档(ncnynl 6745)的简单四步流程，对"建立蓝牙连接"这个环节是有效的（不需要 NoInputNoOutput 也能连上），但**不足以让手柄真正可用**（拿不到 js0）。必须用 `bt-agent -c NoInputNoOutput` 强制协商出 `General Bonding`，才能同时满足"连接成功"+"bluetoothd 愿意建 HIDP session"两个条件。这是本机型（副厂 DS4）的必需步骤，不是绕远路。

## 三、标准恢复流程（配对从零开始，含系统重置后）

```bash
# 0. 清理可能存在的旧配对残留（如果之前配对失败或不确定状态）
ssh duck "sudo bluetoothctl remove A0:5A:5F:0A:0F:2C"

# 1. 启动 NoInputNoOutput agent（必须用 systemd-run detach，SSH 里普通后台会被 hold 住）
ssh duck "sudo systemctl stop btagent 2>/dev/null; sudo systemd-run --unit=btagent --collect bt-agent -c NoInputNoOutput"

# 2. 手柄操作：Share + PS 同时长按至快速闪烁（配对模式）

# 3. 直连（跳过 inquiry，这台手柄扫不到但可以 page 直连）
ssh duck "sudo hcitool cc A0:5A:5F:0A:0F:2C"

# 4. 走标准 pair/trust/connect（此时 agent 是 NoInputNoOutput，会协商出 General Bonding）
ssh duck 'echo -e "pair A0:5A:5F:0A:0F:2C\ntrust A0:5A:5F:0A:0F:2C\nconnect A0:5A:5F:0A:0F:2C\nexit" | bluetoothctl'

# 5. 验证：Bonded 必须是 yes，js0 必须存在
ssh duck "bluetoothctl info A0:5A:5F:0A:0F:2C | grep -E 'Paired|Bonded|Connected'; ls -la /dev/input/js0"
# 期望: Paired: yes / Bonded: yes / Connected: yes / js0 存在

# 6. 清理临时 agent（可选，已 bonded 的手柄后续短按 PS 自动回连不需要 agent）
ssh duck "sudo systemctl stop btagent"
```

**reboot 持久化**：一旦 `Bonded: yes` 且 link key 已写入 `/var/lib/bluetooth/<adapter_mac>/<controller_mac>/info`，之后每次开机短按 PS 键即可自动回连，js0 自动出现，不需要重复以上流程（除非系统整盘重置）。

## 四、手柄连上之后：如何让呱呱真正响应手柄走路

手柄配对/连接只是"输入设备就绪"，**不代表控制程序在跑**。要让呱呱响应按键，必须手动启动 RL 走路控制进程（除非已部署 `guagua-customizations` 分支的 reboot 自启 systemd unit——见 [duck-workspace-state.md](duck-workspace-state.md)）：

```bash
ssh duck "sudo systemd-run --unit=duckwalk-test --collect \
  --uid=raspios --gid=raspios \
  --working-directory=/home/raspios/open_duck_mini_ws/Open_Duck_Mini_Runtime/scripts \
  -E PYTHONUNBUFFERED=1 -E HOME=/home/raspios \
  /home/raspios/venv_duck/bin/python3 v2_rl_walk_mujoco.py \
  --onnx_model_path /home/raspios/open_duck_mini_ws/Open_Duck_Mini/BEST_WALK_ONNX_2.onnx \
  --duck_config_path /home/raspios/duck_config.json"
```

**⚠️ 坑：`sudo systemd-run` 不加 `--uid=raspios --gid=raspios` 会以 root 身份运行**，`HOME` 变成 `/root`，脚本默认 `duck_config_path = ~/duck_config.json` 解析成 `/root/duck_config.json`（不存在），触发"用默认值继续运行？(y/N)"交互式确认 → systemd 无 stdin → `EOFError` 直接崩溃。**必须显式加 `--uid/--gid` 且传 `-E HOME=` 和 `--duck_config_path`**，双保险。

**安全提示**：进程启动后会立即执行舵机初始化序列（低 KP → 摆到 init 姿势 → 高 KP 站稳），**启动前先扶稳/支撑呱呱**，尤其是刚更换过舵机或刚重装系统后的第一次测试。

**按键**（vendor 命名，PS4 对应关系）：
- **✕ (Cross) = "A"：pause/unpause**——进程默认 `start_paused: true`（`duck_config.json`），必须按一次才会响应走路指令，这是安全设计不是 bug
- □ (Square) = "X"：开关投影仪
- ○ (Circle) = "B"：随机播放声音
- △ (Triangle) = "Y"：头部控制开关（实验性，不建议用，可能弄坏脖子）
- LB：按住加快步频（"冲刺"模式）
- 左摇杆：走路方向

## 五、诊断方法论沉淀

- **蓝牙/HID 连接问题先抓 btmon，不从症状猜假设**：`sudo systemd-run --unit=btmon-cap --collect btmon`，事后 `journalctl -u btmon-cap --no-pager -o cat` 直接看人类可读的 HCI 事件流，重点抓 `IO Capability Request/Response`、`Simple Pairing Complete`、`Auth Complete`
- **`bluetoothd` 自身日志同样关键**：`sudo journalctl -u bluetooth --no-pager -S '5 min ago'`，本次案例的决定性证据（`Rejected connection from !bonded device`）就是从这里找到的，btmon 只能看到"连接建立成功"，看不到 bluetoothd 应用层为什么拒绝 HID profile
- **"Connected: yes" 不代表真正可用**：还要看 `Bonded` 字段 + 实际 `/dev/input/js0` 是否存在，两者都要核对
