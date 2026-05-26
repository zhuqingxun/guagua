"""
ST3215 14 舵机响应扫描 (2026-05-24, walk stall B 假设 verify)

设计目标:
- ★ 只读 / noninteractive / 不改舵机状态 (KP / position 都不动)
- 鸭子站立姿态下安全跑, 不会因为 set_kps 让它失力倒下
- 跑前必须先 `sudo systemctl stop duck-mcp-runtime` 释放 /dev/ttyACM0

输出诊断信号:
- 14 个 ID 各自的 present_position (vs init_pos 期望值的偏差)
- 各 ID 的 present_velocity (静止时应 ≈ 0)
- 各 ID 的 voltage (应 ≈ 12V, 看 burst 时是否压降, 但本脚本只在静止读)
- 任何 unresponsive outlier (TTL bus 通信故障 / 舵机损坏)

跑法 (在鸭子上):
  sudo systemctl stop duck-mcp-runtime
  ~/venv_duck/bin/python /tmp/verify_servos.py
"""

import traceback

print("=== ST3215 14 舵机响应扫描 (只读, noninteractive) ===\n")

# Step 1: HWI 初始化 (只开 rustypot 连接, 不改舵机状态)
print("--- Step 1: HWI init (open /dev/ttyACM0) ---")
try:
    from mini_bdx_runtime.rustypot_position_hwi import HWI
    from mini_bdx_runtime.duck_config import DuckConfig

    duck_config = DuckConfig()
    hwi = HWI(duck_config)
    print(f"OK, {len(hwi.joints)} expected joints\n")
except Exception as e:
    print(f"HWI init FAILED: {type(e).__name__}: {e}")
    print(traceback.format_exc())
    print("\n常见原因: (1) duck-mcp-runtime 还没 stop, 占着 /dev/ttyACM0  (2) USB 线松了  (3) ttyACM0 不是 ST3215 控制板")
    exit(1)

# Step 2: 逐 ID 读 present_position (只读, 安全)
print("--- Step 2: read present_position (rad) + init_pos expected ---")
unresponsive = []
position_data = {}
for joint_name, joint_id in hwi.joints.items():
    expected = hwi.init_pos[joint_name]
    try:
        pos = hwi.io.read_present_position([joint_id])[0]
        diff = pos - expected
        position_data[joint_name] = (joint_id, pos, expected, diff)
        flag = "⚠️" if abs(diff) > 0.3 else "  "
        print(f"  ID={joint_id:2d} {joint_name:20s} pos={pos:+.3f}  init={expected:+.3f}  diff={diff:+.3f} {flag}")
    except Exception as e:
        unresponsive.append((joint_name, joint_id))
        print(f"  ID={joint_id:2d} {joint_name:20s} ERR: {type(e).__name__}: {e}")

# Step 3: 逐 ID 读 present_velocity (静止应 ≈ 0)
print("\n--- Step 3: read present_velocity (静止应 ≈ 0) ---")
for joint_name, joint_id in hwi.joints.items():
    if (joint_name, joint_id) in unresponsive:
        continue
    try:
        vel = hwi.io.read_present_velocity([joint_id])[0]
        flag = "⚠️" if abs(vel) > 0.1 else "  "
        print(f"  ID={joint_id:2d} {joint_name:20s} vel={vel:+.3f} {flag}")
    except Exception as e:
        print(f"  ID={joint_id:2d} {joint_name:20s} vel ERR: {type(e).__name__}: {e}")

# Step 4: voltage (pypot 路径, 鸭子可能没装 pypot, 失败不致命)
print("\n--- Step 4: voltage (12V 期望) ---")
try:
    from pypot.feetech import FeetechSTS3215IO

    pio = FeetechSTS3215IO("/dev/ttyACM0", baudrate=1000000, use_sync_read=True)
    voltages = pio.get_present_voltage(list(hwi.joints.values()))
    for name, raw in zip(hwi.joints.keys(), voltages):
        v = round(raw * 0.1, 2)
        flag = "⚠️" if v < 10.5 or v > 13.5 else "  "
        print(f"  ID={hwi.joints[name]:2d} {name:20s} {v:5.2f} V {flag}")
except ImportError:
    print("  pypot 未安装 (skip voltage)")
except Exception as e:
    print(f"  voltage read failed: {type(e).__name__}: {e}")

# Summary
print("\n=== Summary ===")
print(f"Total joints: {len(hwi.joints)}")
print(f"Responsive: {len(position_data)}")
print(f"Unresponsive: {len(unresponsive)}")
if unresponsive:
    print(f"  ⚠️ outliers: {unresponsive}")
    print("  → 故障舵机/通信问题确认 (B 假设命中)")

big_diff = [(n, *d) for n, d in position_data.items() if abs(d[3]) > 0.3]
if big_diff:
    print(f"\n  ⚠️ position 跟 init_pos 偏差 > 0.3 rad 的关节:")
    for n, jid, pos, exp, diff in big_diff:
        print(f"     ID={jid:2d} {n} pos={pos:+.3f} init={exp:+.3f} diff={diff:+.3f}")
    print("  → 可能机械姿态偏离 / KP 不够 hold / 上次 walk 残留")

print("\n--- 不调 disable_torque, 保持当前舵机状态退出 ---")
