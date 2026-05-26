"""
ST3215 14 舵机承重单关节顺序测试 (2026-05-24, walk stall B 假设承重 verify)

跟之前的 verify_servos_movement.py 区别:
- 鸭子放地上 (脚承重, 不悬空)
- ±0.05 rad 保守幅度 (承重下大幅会让鸭子失衡)
- KP 保持 vendor turn_on() 留下的 high kps=32 (不主动改 KP)
- 14 ID 顺序固定, 每 ID 4-5 秒, 总时长 ~70 秒
- 用户视觉跟节奏看每个动作 (心里按下方 ID 顺序数)

★★★ 跑前 5 个前提:
1. duck-mcp-runtime 已 stop (释放 /dev/ttyACM0)
2. 鸭子放地上承重 (脚接地)
3. 用户**扶住鸭子身体**, 防止单 ID 失衡摔倒
4. 视觉记住 14 个 ID 的顺序 (脚本会按此顺序逐个测)
5. 准备好录像 / 留意每个 ID 测试时的鸭子动作

ID 顺序 (hwi.joints 字典定义):
  腿部 (10 个):
    20 left_hip_yaw    | 21 left_hip_roll  | 22 left_hip_pitch
    23 left_knee       | 24 left_ankle
    30 neck_pitch      | 31 head_pitch
    32 head_yaw        | 33 head_roll
    10 right_hip_yaw   | 11 right_hip_roll | 12 right_hip_pitch
    13 right_knee      | 14 right_ankle
"""

import sys
import time

if "--confirm-loaded" not in sys.argv:
    print("⛔ 必须传 --confirm-loaded 参数. 跑前确认: 鸭子放地上承重 + 用户扶住身体")
    sys.exit(1)

from mini_bdx_runtime.rustypot_position_hwi import HWI
from mini_bdx_runtime.duck_config import DuckConfig

DELTA = 0.05  # 3°, 承重下保守
WAIT = 2.0    # 每方向等 2s

hwi = HWI(DuckConfig())
print(f"=== 承重单关节测试 (DELTA=±{DELTA} rad, wait={WAIT}s per direction) ===")
print(f"→ 14 ID 顺序测试, 每 ID 约 {(WAIT*2 + 1):.0f}s, 总 ~{int(len(hwi.joints) * (WAIT*2 + 1))}s\n")

# 5 秒倒计时让用户 ready
for i in range(5, 0, -1):
    print(f"  开始倒计时... {i}")
    time.sleep(1)
print("  >>> 开始测试 <<<\n")

results = []
for idx, (joint_name, joint_id) in enumerate(hwi.joints.items(), 1):
    current = hwi.io.read_present_position([joint_id])[0]
    target = current + DELTA

    print(f"\n[{idx:2d}/14] >>> ID={joint_id:2d} {joint_name:20s}")
    print(f"        init={current:+.3f}  →  target={target:+.3f}")

    # 移动到 target
    hwi.io.write_goal_position([joint_id], [target])
    time.sleep(WAIT)
    actual = hwi.io.read_present_position([joint_id])[0]
    diff = (actual - current) - DELTA

    # 归位
    hwi.io.write_goal_position([joint_id], [current])
    time.sleep(WAIT)
    ret = hwi.io.read_present_position([joint_id])[0]
    ret_diff = ret - current

    # 评估 (承重下容差稍宽: 0.025 rad = 50% DELTA)
    flag = "⚠️" if abs(diff) > 0.025 or abs(ret_diff) > 0.025 else "✓ "
    print(f"        actual={actual:+.3f}  diff={diff:+.3f}  ret_diff={ret_diff:+.3f} {flag}")
    results.append((joint_id, joint_name, round(diff, 3), round(ret_diff, 3)))

# 总结
print("\n\n=== 承重测试总结 ===")
fails = [r for r in results if abs(r[2]) > 0.025 or abs(r[3]) > 0.025]
print(f"承重下 outliers (|diff| > 0.025 或 |ret_diff| > 0.025): {len(fails)}/14")
for r in fails:
    print(f"  ID={r[0]:2d} {r[1]:20s} diff={r[2]:+.3f}  ret_diff={r[3]:+.3f}")
if not fails:
    print("  无 outliers → B 假设承重层面也否定 → 真凶可能是 vendor walk policy (C 假设)")
