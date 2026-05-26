---
title: "[M3-S0] walk 地面承重右脚 stall 真因 - 锁定 right_knee (ID 13) 物理故障"
type: issue
status: in-progress
priority: high
created_at: 2026-05-26T21:30:00
updated_at: 2026-05-26T23:10:00
---

## 🎯 2026-05-26 23:05 真因锁定

**right_knee (ID 13) 物理故障** (假设 I 机械卡阻 / 假设 F 过热)

证据 (按强度):
1. 两次 walk 热分布 reproducible: knee Δ=+8°C 完全一致 (排除偶发误差)
2. ID 13 残留 current 9→14 (其他 leg ID 0-2): 持续力矩饱和直接证据
3. ID 13 load 188 vs ID 23 load 61: 3x 不对称
4. 5 个症状全匹配: 右腿迈不开 / 鸭子向右转 / 嗡嗡声 / paused 地上倒 / 5/22 起恶化

待 verify 子假设:
- A: ID 13 舵机个体故障 (最可能, swap test 验证)
- B: right_knee 位置机械装配应力 (次可能, swap test 验证)
- C: 上游 right_hip 传导应力 (弱否定, right_hip 温度未异常)

下一步: 详见 handoff-2026-05-26-v6.md

# Walk 地面承重时右脚 stall - 限流根因排除后的新假设清单

## 触发场景 (2026-05-26 21:15-21:25)

会话上下文: 5/26 会话末段, 完成 vendor 5+6 bug fix (obs dim + detach) + commit 26c4cc6 + 悬空 walk verified 对称摆动后, 用户放地上测真 walk:
- 地面 + UDP6730 切 25A + 按 X unpause + 推 stick 前进
- 现象: **能向前走 (5+ 步), 但右脚仍有问题** (handoff v4 描述: "右腿 stall + 向右转 + 倒")
- 用户判断: "应该是舵机的问题"

## 已 verify 的事实 (排除假设)

### ❌ UDP6730 限流不是根因 (5/26 用户实测打脸)
- walk 时实测电流 ≈ **1A**, 远小于 8A limit, CC 模式根本不会触发
- 8A vs 25A 同样表现 (用户原话: "调了 25A 的电流还是一样的问题。和 8A 没区别")
- 老 todo [`m3-walk-stall-investigation.md`](./m3-walk-stall-investigation.md) 5/24 14:40 closed 的根因 = **错误推断**, 已 archive + supersede 到本文件
- **教训**: 凭硬件清单理论值 + 没真测就 close = 「根因优先」+「事实承接」双违反

### ❌ ST3215 个体故障不是根因 (5/24 + 5/26 双重 verify)
- 5/24 verify_servos_loaded.py 承重测试 14 ID 全 ✓ 对称
- 5/26 verify_servos.py 静止扫描 14 ID 全 responsive + vel=0 + 14 个 ID 全部 readable
- 5/26 静止扫描看到 5 个 position outlier (left/right hip_pitch + neck/head_pitch + left_knee) 但 **两腿对称偏离** = 重力效应 / 上次 walk 残留, 不是个体故障

### ❌ obs dim concat bug 不是 walk stall 根因
- 5/26 修了 obs dim (PS4Controller line 34 list→ndarray, commit 26c4cc6 第 5 bug 修复)
- 悬空 walk verify: 两腿对称摆动 + 双脚升降交替 ✓
- 地面 walk: 仍有右脚问题 = obs dim 修复跟 walk stall 是两个独立 bug

### ❌ vendor RL hallucinate (commands=0 时 RL 输出非零) 不是
- 5/26 verify: 按 X unpause + 不推 stick = 鸭子腿不动
- handoff v4 §"task #4 真凶锁定" 描述的 "commands=0 仍输出 + 倒" 可能是 obs dim 时代的伪现象, 修了 obs dim 后消失

### ❌ 装配假设 (5/24 已用户事实校正) — ⚠️ 部分作废 (2026-05-26 22:30 advisor 提醒)
- 用户事实: "鸭子买回来一直能走", 装配没变过
- 否定 "右脚某关节螺丝松动" 类假设
- ⚠️ **advisor 2026-05-26 22:30 提醒**: 5/22 之后 walk 测试反复跌倒/冲击可能累积机械损伤, "5/22 一直能走" 不能完全排除当前状态。新增 **假设 I (机械不对称)** 见下

### ❌ 假设 H 软件 joints_offsets 不对称 (2026-05-26 22:00-22:30 已 verify)
- 触发: ncnynl 6737 舵机配置教程引出 soft_offsets 路径
- verify 方法: ssh duck cat `~/duck_config.json` + grep `init_pos` / `zero_pos` in `rustypot_position_hwi.py`
- 结果: `joints_offsets` 数值符号**完全符合** vendor sign convention:
  - hip_yaw / hip_roll / hip_pitch: **镜像** (init_pos ±0.002 / ±0.053 / ±0.63) — joints_offsets 也镜像 (-0.30/+0.30 等)
  - knee / ankle: **同号** (init_pos +1.368/+1.368, -0.784/-0.784) — joints_offsets 也同号 (+0.20/+0.20)
- 结论: joints_offsets 不是 bug
- 副发现: `polynomial_coefficients.pkl` 是 RL 参考动作 PolyReferenceMotion 类的多项式拟合, 跟硬件无关, 排除
- 副发现: `scripts/duck_config.json` 是 symlink → `/home/raspios/duck_config.json`, DuckConfig 单一 load 路径 verified

## 新假设清单 (按 likelihood 排序, 下次会话逐一 verify)

### A. ST3215 KP 不平衡 (likely - 静态参数检查)
**信号**: vendor `v2_rl_walk_mujoco_mcp.py:start()` 设置 KP:
```python
kps = [self.pid[0]] * 14    # default
kps[5:9] = [8, 8, 8, 8]      # neck + head 低 KP
```
左右 5 个 leg ID (0-4 vs 9-13 内部 index, 即 ST3215 ID 20-24 vs 10-14) KP 相同。但**实际跑时是否对称**? 可能 vendor 老版本有 right_foot KP override 残留, 或 `polynomial_coefficients.pkl` 含左右不同 calibration。

**verify 方法** (下次会话):
- ssh duck cat 完整 v2_rl_walk_mujoco_mcp.py start() 看 final kps 数组
- check `polynomial_coefficients.pkl` content (是否有 left vs right 不同)
- check `imu_calib_data.pkl` 是否有 left/right 偏置
- 加 debug print 看 walk 主循环 motor_targets 在左右对应 ID 是否对称

### B. RL Policy sim2real gap (likely - 系统层最常见)
**信号**: ONNX 模型 BEST_WALK_ONNX_2 是 Playground 训练出来的 sim policy。Sim 中假设完美对称 ST3215, real ST3215 个体扭矩响应有差异 → sim→real 时左右脚响应不对称 → policy 在某些 dof_pos 区间输出非对称 action。**这是最常见的 sim2real 表现**, 跟 Open Duck Mini 上游 issues 可能有线索。

**verify 方法**:
- 上 GitHub apirrone/Open_Duck_Mini_Runtime issues 搜 "right foot" / "stall" / "asymmetric" 看是否上游已有 known issue
- 上 Discord 看 sim2real 主帖
- 试 BEST_WALK_ONNX.onnx vs BEST_WALK_ONNX_2.onnx vs ONNX.onnx (有 3 个 onnx 模型, 训练版本差异可能影响 sim2real gap)
- 如果是真 sim2real gap → 需要 Playground 端 re-train (本仓库 M2 阶段事, 不是 S0 S1 范围)

### C. 承重时 IMU 数据偏置导致 RL 不对称输出 (medium)
**信号**: obs[0:3] gyro + obs[3:6] accel. 鸭子放地上后 IMU 读到 1g 重力 + 鸭子可能稍倾斜, RL 用这些信号决策。若 IMU 安装位置不正 / calibration 数据偏 → RL 误以为鸭子向某侧倾 → 输出反向修正 → 右脚 stall。

**verify 方法**:
- 让鸭子站平地不走 + ssh duck cat /tmp/imu_data.log (vendor 已有 imu telemetry?)
- 加 debug print 看 obs[0:3] + obs[3:6] 是否稳定 (gyro 应 ≈ 0, accel 应 ≈ [0, 0, 9.8])
- 看 `imu_calib_data.pkl` 是否针对当前装配做过校准

### D. 承重时 dof_vel 噪声导致 RL 不稳定 (low-medium)
**信号**: obs[dof_vel * 0.05] (14 维)。ST3215 静止读 vel ≈ 0, 但 walk 时 vel 信号可能有大噪声 (尤其右脚承重瞬间), RL 收到噪声 → 输出抖动 / 偏置。

**verify 方法**:
- 加 debug print 看 walk 5 秒 dof_vel 各 ID 范围 + 标准差

### E. 头部 / 脖子摆动影响 RL 输入 (low)
**信号**: 5/26 verify_servos 看到 head_pitch / neck_pitch 偏离 init pos 0.7 rad (鸭子垂头)。如果 head joint 在 walk 时摆动 → 重心偏 → 影响 RL 行走稳定性。

**verify 方法**: 用 PS4 头部按键 (Y 键 head control) 把头摆到 init pos 再 walk, 看是否好转。

### F. ST3215 过热保护 (low - 但要排除)
**信号**: walk 持续运行后某 ID 温升 → 自动降扭矩。但用户描述 "走 5+ 步就 stall" = 起步就有问题, 不是持续温升累积。

**verify 方法**: walk 持续 30+ 秒 + 同时跑监控脚本读 ID 10-14 temp (但 verify_servos.py 抢占串行 bus, 需要写新 background telemetry 脚本)。

### G. ONNX policy 本身在 corner case 出错 (low)
**信号**: ONNX 训练分布外的 obs 组合可能让模型输出奇异 action。但这个排查成本高 (需 onnx 内部 weight 分析), 留作 last resort。

### H'. joints_offsets 已过期 / 鸭子运输/磕碰漂移 (medium - 5/26 22:30 升级)
**信号**: 当前 duck_config.json 是爱折腾出厂校准 + 用户可能历史跑过 find_soft_offsets.py。但 5/22 起反复 walk + 跌倒, zero 位置可能漂移, 需重新校准。

**verify 方法**:
- ssh duck 上跑 `scripts/find_soft_offsets.py` (但需要 stop 服务 + 物理操作: disable_torque 后手动把鸭子摆到 zero 姿势)
- 比对脚本给出的新 offset vs 当前 duck_config.json 各关节 diff
- 任何 diff > 0.05 rad (~3°) → 重写 duck_config.json + 重测 walk

### I. 机械不对称 / 右腿铰链 / 齿轮磨损 (medium - 5/26 22:30 advisor 提出)
**信号**: 5/22 起 walk 反复跌倒, 右腿冲击累积可能让铰链松 / 螺丝松 / ID 13 right_knee 或 ID 14 right_ankle 齿轮内部磨损。用户 "5/22 一直能走" 不能完全排除当前状态。

**verify 方法** (advisor 建议在 A + instrumentation 后做):
- 物理检查: 用手按左右腿每个关节, 对比转动阻尼 + 是否有间隙松动
- 用手把左右腿每个关节摆到极限位置, 对比 range of motion 是否对称
- 拆开看 ID 13/14 齿轮有无可见磨损 (last resort, 拆装风险)

## 下次会话起手 (2026-05-26 22:30 advisor 重排后)

**核心洞察 (advisor)**: 一次 5 秒 walk 录制 `[commands → RL action[14] → motor_targets[14] → present_position[14]]` 可一次性区分 5 个假设 (B/C/D/G + A), 比逐个 verify 高效。

按 cost ascending:

1. **A: check_motors_params.py 只读检查** (最便宜, 5 分钟):
   - `sudo systemctl stop duck-mcp-runtime mcp-openduck`
   - `cd ~/open_duck_mini_ws/Open_Duck_Mini_Runtime/scripts && ~/venv_duck/bin/python check_motors_params.py`
   - 期望: 14 个 ID 全部 P=32 / I=0 / D=0 / mode=0
   - 任一 diverge → 假设 A 命中, 直接 set_*_coefficient 写回 32 + 重测

2. **instrumentation v2_rl_walk_mujoco_mcp.py 加 logging** (10-30 分钟, advisor 主推):
   - 在 main control loop 加 `[t, commands, action14, motor_targets14, present_pos14]` append-to-file
   - 走 5 秒 + ssh-cat log + diff 左右 paired IDs
   - 一次区分 5 个假设 B/C/D/G + A

3. **H': find_soft_offsets.py 重校准** (要 disable_torque + 物理摆位, 风险较高, A + instrumentation 之后做)

4. **I: 机械不对称物理检查** (advisor 兜底, A + instrumentation 都清白后做)

5. **B: GitHub apirrone issues + Discord 调研** (并行可做)

## 调试工具清单 (本 issue 可用)

| 脚本 | 路径 | 用途 |
|---|---|---|
| `verify_servos.py` | `D:/CODE/guagua/scripts/` | 14 ID 静止只读扫描 (已 verify 全 responsive) |
| `verify_servos_movement.py` | `D:/CODE/guagua/scripts/` | 14 ID 空载 ±0.1 rad 测试 (5/24 已跑) |
| `verify_servos_loaded.py` | `D:/CODE/guagua/scripts/` | 14 ID 承重 ±0.05 rad 测试 (5/24 已跑) |
| `verify_single_joint.py` | `D:/CODE/guagua/scripts/` | 单 ID 测试 (需 `--id X` 参数) |
| - 待加 | - | walk 期间 background telemetry monitor (温度 / 电流 / position) |

## 相关 commits

| Commit | 作用 | 是否影响本 issue |
|---|---|---|
| `26c4cc6` fix(ps4_controller) | 5/26 修 obs dim + detach | ❌ 修了别的 bug, walk stall 仍存在 |
| `20916cb` feat(ps4 hotplug) | 5/24 hotplug v1 | 不直接相关 |
| `b7d1529` chore(antennas) | 5/24 注释耳朵 | 不直接相关 |
| `1e5f7e5` fix(paused) | 5/23 unpause toggle 修复 | 不直接相关 |
