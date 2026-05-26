"""
ST3215 14 舵机 movement test v2 (2026-05-24, 修复 KP=2 推不动 bug)

★★★ 跑前必须确认鸭子已悬空 (四脚不接地, 肚子被支架架起) ★★★

v1 bug: KP=2 + wait 1s 太保守, 舵机扭矩输出不足以克服 ST3215 齿轮静摩擦,
       全部 14 ID actual ≈ init 看似 fail.
v2 修复: 用 KP=16 (vendor default 是 32 太冲击, 16 适中) + wait 2s.

诊断信号 (同 v1):
- 偏差大的 ID = 故障 / 卡顿 outlier
"""

import sys
import time
import traceback

if "--confirm-suspended" not in sys.argv:
    print("⛔ 必须传 --confirm-suspended 参数. 跑前确认鸭子已悬空.")
    sys.exit(1)

print("=== ST3215 movement test v2 (悬空, KP=16, ±0.1 rad, 2s wait) ===\n")

from mini_bdx_runtime.rustypot_position_hwi import HWI
from mini_bdx_runtime.duck_config import DuckConfig

duck_config = DuckConfig()
hwi = HWI(duck_config)
print(f"HWI ok, {len(hwi.joints)} expected joints\n")

# Phase 1: 读初始 position
print("--- Phase 1: 初始 position ---")
init_positions = {}
for joint_name, joint_id in hwi.joints.items():
    pos = hwi.io.read_present_position([joint_id])[0]
    init_positions[joint_name] = pos
    print(f"  ID={joint_id:2d} {joint_name:20s} pos={pos:+.3f}")

# Phase 2: 设 KP=16 (适中, 不冲击)
print("\n--- Phase 2: set KP=16 (vendor default 32 太冲击, 16 适中) ---")
KP = 16
for joint_id in hwi.joints.values():
    hwi.io.set_kps([joint_id], [KP])
time.sleep(1.0)  # 让 KP 写入生效
print(f"  KP={KP} set, 等 1s 生效")

# Phase 3: movement test ±0.1 rad, wait 2s
print("\n--- Phase 3: movement test (±0.1 rad, wait 2s) ---")
DELTA = 0.1
WAIT = 2.0
failures = []
for joint_name, joint_id in hwi.joints.items():
    current = init_positions[joint_name]
    target = current + DELTA
    try:
        hwi.io.write_goal_position([joint_id], [target])
        time.sleep(WAIT)
        actual = hwi.io.read_present_position([joint_id])[0]
        offset = actual - current
        diff = offset - DELTA

        hwi.io.write_goal_position([joint_id], [current])
        time.sleep(WAIT)
        ret = hwi.io.read_present_position([joint_id])[0]
        ret_diff = ret - current

        # 评估: 期望 offset ≈ 0.1, ret_diff ≈ 0
        # 异常: |diff| > 0.03 (30% 容差) 或 |ret_diff| > 0.03
        flag = "  "
        if abs(diff) > 0.03 or abs(ret_diff) > 0.03:
            flag = "⚠️"
            failures.append((joint_name, joint_id, round(diff, 3), round(ret_diff, 3)))

        print(f"  ID={joint_id:2d} {joint_name:20s} init={current:+.3f}  actual={actual:+.3f}  diff={diff:+.3f}  ret_diff={ret_diff:+.3f} {flag}")
    except Exception as e:
        print(f"  ID={joint_id:2d} {joint_name:20s} FAIL: {e}")
        failures.append((joint_name, joint_id, "exception", str(e)))

# Phase 4: disable_torque (悬空安全)
print("\n--- Phase 4: disable_torque ---")
for joint_id in hwi.joints.values():
    try:
        hwi.io.disable_torque([joint_id])
    except:
        pass

print("\n=== Summary ===")
print(f"Failures (|diff| > 0.03 or |ret_diff| > 0.03): {len(failures)}/14")
if failures:
    print("  ★ outliers:")
    for f in failures:
        print(f"    {f}")
else:
    print("  ✓ 14 ID 在 ±0.1 rad 范围内全部到位 → B 假设空载层面否定")
