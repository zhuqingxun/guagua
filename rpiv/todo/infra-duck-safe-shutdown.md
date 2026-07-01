---
title: "设计呱呱安全关机方案 — 含能否直接断物理电源的调研"
type: todo
status: open
priority: low
created_at: 2026-07-02T00:20:00
updated_at: 2026-07-02T00:20:00
---

# 设计呱呱安全关机方案 — 含能否直接断物理电源的调研

## 任务描述

2026-07-01 会话里给鸭子做了一次手动安全关机，流程是 SSH 上去手动敲三步：

1. `sudo systemctl stop duckwalk` —— 停走路控制服务（发现问题：主循环没有 `SIGTERM` 处理逻辑，systemd 硬等 `TimeoutStopSec` 默认值 90 秒超时后才 `SIGKILL` 强杀，本次关机因此多等了 91 秒）
2. `cd scripts && python3 turn_off.py` —— 调用 vendor 自带的 `hwi.turn_off()` 释放全部舵机力矩（这一步验证是必需的：走路服务停止后舵机仍然带力矩保持最后姿态，不释放就切电源，腿部会在失去支撑的瞬间"硬摔"）
3. `sudo shutdown -h now`

用户问：**这个流程是不是太麻烦了？有没有更简单的方式，比如直接按外壳上的物理电源开关关机？**

需要调研/设计的方向：
- **物理电源开关直接断电是否安全**：需要搞清楚（a）STS3215 串行总线舵机在带电状态下被突然断电，是否有损坏风险（比如总线通信中断、EEPROM 写入中断）；（b）Raspberry Pi OS 文件系统在未执行 `shutdown`/`sync` 的情况下被硬断电，SD 卡数据损坏的概率有多大（参考 `rpiv/archived/m3-issue-battery-cell-dead.md` 如果有类似的硬断电经验可以复用）
- **优雅关机能否一键化**：给 `duckwalk.service` 加 `SIGTERM` 处理逻辑（收到信号后自动调用 `turn_off.py` 的等价逻辑释放力矩、再退出），这样 `sudo shutdown -h now` 一条命令就能完成现在的三步，不用分开敲
- **是否需要一个物理/远程的"一键关机"入口**：比如手柄某个按键组合触发安全关机、或者一个简单的 shell 脚本/别名封装三步命令，降低下次操作门槛

## 涉及文件

- 鸭子端 `systemd/duckwalk.service`（如果走"加 SIGTERM handler"方向，需要改 `scripts/v2_rl_walk_mujoco_mcp.py` 主循环 + 可能加 `TimeoutStopSec=` 配置）
- 鸭子端 `scripts/turn_off.py`（参考现有释放力矩逻辑）
- 硬件层面：外壳电源开关的具体接线方式（关系到断电是切主电池还是切逻辑电源，需要现场确认，参考 `docs/hardware-inventory.md` 电源系统章节）
- 可能新增：`docs/duck-workspace-state.md` 新增"安全关机 SOP"章节，或独立脚本 `scripts/duck-safe-shutdown.ps1`

## 完成标准

- 明确回答"能不能直接按物理开关关机"这个问题，给出结论和依据（不是猜测，需要查阅 STS3215/舵机总线断电安全性的实测或官方资料，或找到卖家/上游的说法）
- 产出一个比现在更简单的关机操作方式（一键脚本，或者验证物理开关本身就够安全从而不需要额外流程）
- 更新 `docs/` 里的关机 SOP，让下次会话不用重新摸索

## 备注

优先级低——当前手动三步流程已经验证可行（2026-07-01 亲测成功），只是操作繁琐。不是紧急项，等有空或者下次关机嫌麻烦的时候再处理。
