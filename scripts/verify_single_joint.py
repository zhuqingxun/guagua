"""
单 ID 承重测试 (用户逐个 control 节奏版)

用法:
  python verify_single_joint.py --id 13 --delta 0.05

跑前确认:
- duck-mcp-runtime 已 stop
- 鸭子放地上承重 / 或 用户手扶
- 该 ID 单独动 ±delta rad, 其他 13 ID 保持 KP=32 不变
"""

import sys
import time

# CLI parse
def get_arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1]
    return default

joint_id = int(get_arg("--id", "0"))
delta = float(get_arg("--delta", "0.05"))
wait = float(get_arg("--wait", "2.0"))

if joint_id == 0:
    print("⛔ 必须传 --id X (X 是舵机 ID, 见 hwi.joints 字典)")
    print("  腿部: 10/11/12/13/14 (右), 20/21/22/23/24 (左)")
    print("  头部: 30/31/32/33")
    sys.exit(1)

from mini_bdx_runtime.rustypot_position_hwi import HWI
from mini_bdx_runtime.duck_config import DuckConfig

hwi = HWI(DuckConfig())

# 找 joint_name
joint_name = next((n for n, jid in hwi.joints.items() if jid == joint_id), None)
if not joint_name:
    print(f"⛔ ID={joint_id} 不在 hwi.joints 字典里")
    sys.exit(1)

current = hwi.io.read_present_position([joint_id])[0]
target = current + delta

print(f"=== ID={joint_id} {joint_name} 承重测试 ===")
print(f"  init={current:+.3f}  target={target:+.3f}  (delta=+{delta})")

# 移动
hwi.io.write_goal_position([joint_id], [target])
time.sleep(wait)
actual = hwi.io.read_present_position([joint_id])[0]
diff = (actual - current) - delta
print(f"  >>> 移动后: actual={actual:+.3f}  diff={diff:+.3f}")

# 归位
hwi.io.write_goal_position([joint_id], [current])
time.sleep(wait)
ret = hwi.io.read_present_position([joint_id])[0]
ret_diff = ret - current
print(f"  >>> 归位后: ret={ret:+.3f}  ret_diff={ret_diff:+.3f}")

flag = "⚠️ outlier" if abs(diff) > 0.025 or abs(ret_diff) > 0.025 else "✓ 正常"
print(f"  结果: {flag}")
