---
title: "[M3-S0] walk 时鸭子失力倒下 - 根因 = UDP6730 限流 8A 触发 CC 模式 (5/26 用户实测打脸否定)"
type: issue
status: archived
priority: high
created_at: 2026-05-24T14:15:00
updated_at: 2026-05-26T21:30:00
superseded_by: rpiv/todo/m3-walk-stall-real-root-cause.md
---

## ⛔ 原根因 5/26 实测打脸否定 (2026-05-26 21:25)

5/26 会话末段用户主动 verify, **UDP6730 限流根因被实测否定**:
- 实测 walk 时电流 ≈ 1A (远小于 8A limit, CC 模式根本不可能触发)
- 切 25A 后地面 walk 表现跟 8A 完全一样 (右脚 stall + 倒)
- 5/24 14:40 closed 根因 = "8A 不够 burst 10-15A" 是 **凭印象推断** + **没实测**, 跟 hardware-inventory.md M1/M2/M3 三档限流配置 *理论值* 对得上但不等于真因

教训锚点 (CLAUDE.md 「根因优先」违反):
- 5/24 14:40 我把 docs/hardware-inventory.md 的"M3: 25A walk 专用" 当作 ground truth, 没让用户测真电流, 第一个看似合理的解释处停下
- 用户 5/26 实测 1A 是真 ground truth, 跟我推断完全相反
- CLAUDE.md 「事实承接」: 任务描述中的具体事实声明 ≠ ground truth, 必须 grep / Read / 实测 verify

继续调查走新 todo: [`m3-walk-stall-real-root-cause.md`](./m3-walk-stall-real-root-cause.md)

---

# (以下为 5/24 当时的根因结论, 现已否定, 保留作教训学习)

## (已否定) 已定根因 (2026-05-24 14:40)

**UDP6730 当前限流设定 M1 = 8A, 不够 walk burst peak 10-15A → 触发 CC 恒流模式 → 电压瞬间从 12V 掉到 5-10V → ST3215 失力 → 鸭子倒下.**

事实依据 (docs/hardware-inventory.md:97-99):
- M1: 12V / 8A 限流 (静止 + 对话, 起步保守值)
- M2: 12V / 15A 限流 (局部动作演示)
- **M3: 12V / 25A 限流 (走 walk policy / 激烈动作)**

数学验证: 长线压降 (12AWG 1m × 12A burst) = 0.125V (1% 跌幅), 完全可忽略, 否定假设 A. 假设 B/C 留作教训学习, 实际跑 walk 时先切 M3.

修复: 在 UDP6730 上调输出限流到 ≥25A (或直接调 M3 预设). 0 代码改动. 全部 5 个旧假设 + 3 个新假设 (A/B/C) 中 B/C 也不再需要 verify, 因为根因已确定.

教训锚点:
- 工程师视角: walk 跑 RL policy 的 burst peak 远超静态保持电流, 必须用 M3 不是 M1. 静态测试不能验证 walk 场景
- Claude 视角: hardware-inventory.md 里的 M1/M2/M3 三档限流配置我**根本没读**, 凭软件 verify 路径走了 1.5 小时. 全局 feedback_check_docs_before_hardware_advice.md 自己写的自己违反.

---

# (以下为定根因前的诊断历史, 保留作教训学习)



# Walk 时鸭子 stall 倒下 - 根因待 verify

## 触发场景 (2026-05-24 14:07-14:10)

会话上下文：当天上午做完 pygame 热插拔 verify (vendor hotplug patch 准备阶段)，用户报手柄连不上 → restart duck-mcp-runtime 让 RLWalk 重探手柄 → PS4Controller 真识别到 (Loaded joystick with 6 axes) → 用户用手柄走路 → **走路时舵机失力 + 鸭子倒下**

## 已收集事实

### 数据信号

```
14:07 boot 后启动期间:    CPU 59.1°C  volt=1.3125V  throttled=0x0    (健康)
14:10 stop 服务的瞬间:    CPU 64.5°C  volt=1.2313V  throttled=0x80008
                                                     (bit 3 当前 throttle + bit 19 历史)
14:11 stop 30 秒后:       CPU 58.0°C  volt=1.3125V  throttled=0x80000
                                                     (bit 3 清除，bit 19 历史保留)
```

### 用户提供的硬件事实

- 散热"非常好"（用户口头确认，未细化是风扇/被动/壳设计）
- 不是电池：当时接的是**稳压电源** + 拉长线供电

### journal 信号

- `Policy control budget exceeded by 0.002~0.004` 在 14:06:01 + 14:08:57 各出现 1 次 (50Hz loop 略超时)
- 无 servo error / timeout / fail 关键字
- 无 ST3215 通信错误日志

### 排除的假设

- ❌ **电池电量不足**（用户用稳压电源不是电池）
- ❌ **散热不足**（用户说散热好）
- ❌ **过热绝对值**（64.5°C 不算极高，但 Pi 3B+ soft limit 60°C 确实触发了 bit 3）
- ❌ **机械卡住**（关机后用户目视检查物理姿态正常，舵机外壳微热不烫手）
- ❌ **ST3215 normal noise 假设**（静止时假说成立，但 walk 时动作中仍有问题 → 此假说不成立）
- ❌ **本次会话期间 systemctl restart 反复磨损舵机**（合理但 stop 后扶起鸭子状态完好）

### 1.2313V 自适应电压 (不是供电问题)

Pi 3B+ DVFS 行为：CPU 负载/频率自适应调电压。high 频满载 1.3125V，throttle 降频后掉到 1.2V 区。这是**正常 DVFS**不是电源不足。我前面误判，已纠正。

## 新假设 (按 likelihood 排序，下次会话逐一 verify)

### A. 稳压电源 + 长线压降 (suspicious)

**信号**：用户用"稳压电源 + 长线"。舵机 burst 拉电时长线压降导致终端电压瞬时掉，舵机扭矩输出不足。
**verify 方法**：
- 测量稳压电源**直接出线端**电压（不接鸭子时 vs 接鸭子 walk 时）
- 测量鸭子**端子处**电压（同上）
- 计算 walk 时 burst 电流 × 线材长度+电阻 = 压降
- 也可以临时用电池 / 缩短供电线对照测试

### B. 单舵机老化/故障 (suspicious)

**信号**：5/22 通关 + 5/23 通关 + 5/24 早多次 restart + walk 累计应力。某 ST3215 可能内部齿轮磨损 / 电机线圈老化。
**verify 方法**：
- 用 vendor scripts/ 下的 ST3215 诊断工具 (如有) 走 TTL bus 读每个舵机状态：温度 / 电流 / 错误码 / 位置反馈 vs 目标偏差
- 找 `~/open_duck_mini_ws/Open_Duck_Mini_Runtime/tools/` 看有什么单舵机测试脚本
- 单独通电某腿，目视看是否能 hold target pose 还是抖动 / 漂移

### C. vendor RL loop 持续 walk 端到端未测过 (likely)

**信号**：教训锚点见 docs/duck-workspace-state.md §6 "vendor LLM 模式从未端到端测试过"。**今天 14:07 可能是 vendor walk 模式第一次连续 walk 多步**。5/22/5/23 测试都是"喊一下做一下"短动作，没有持续 walk 5+ 秒。
**verify 方法**：
- vendor `v2_rl_walk_mujoco_mcp.py` 50Hz loop 在持续 walk 命令期间的代码路径走查 (没有断言/超时保护？)
- 看 `Policy control budget exceeded` 在 walk 期间出现多少次，是否累积
- 单纯持续 walk（PS4 推杆） vs 单纯持续 LLM walk（"一直往前走"）双路径都试
- 5/23 同源 bug 模式：vendor 某 toggle / 状态机在持续触发时翻烧饼

### D. CPU 60°C soft limit 阈值在该 Pi 上偏低 (可能但次要)

**信号**：用户说散热好但 64.5°C 触发 throttle。可能 Pi config.txt 的 `temp_soft_limit` 被配置成更低值，或者实际温度感应点跟 Pi 板载传感器有差距。
**verify 方法**：
- 检查 `/boot/config.txt` 是否有 `temp_soft_limit` / `temp_limit` 自定义
- 持续 walk 时监控 `vcgencmd measure_temp` 趋势，看真触发阈值
- 如果是阈值问题，调整 config 或加散热

## 已落地的工件

- `D:/CODE/guagua/scripts/verify_pygame_hotplug.py` (pygame 热插拔 verify, 与本 issue 无关但同会话产物)
- `D:/CODE/guagua/scripts/verify_pygame_minimal.py`
- `D:/CODE/guagua/scripts/drive_hotplug_verify.sh`
- task #3 in-progress 标记

## 下次会话起手

1. 复读本 todo
2. 现场确认：用户当时的稳压电源是什么型号 / 输出电流多大 / 线多长多粗
3. 决定 verify 顺序：先 A (电源链路最易测) → 再 B (ST3215 状态) → 再 C (vendor 代码 walk 路径)
4. 不要凭今天的部分数据下结论。新会话 fresh thinking。

## 与 m3-vendor-hotplug-rpiv 的关系

- vendor hotplug patch RPIV 在本 issue 解决前应**暂缓**——如果 walk 本身有故障，热插拔解决了也走不了路
- 但本 issue 跟 hotplug verify 实验**无直接因果**（verify 脚本只跑 pygame.joystick，不动 ST3215）
- 下次会话先解决本 issue，再回 hotplug
