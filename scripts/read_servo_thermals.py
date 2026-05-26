"""
walk 后立即跑: 读 14 ID 温度 + load + current 找嗡嗡声 ID

时序: 用户 walk 2-3 秒 → paused → 用户报 done → AI 立即 stop service + 跑本脚本
温度有 5-10 秒散热窗口, walk 时持续力矩饱和的 ID 此时仍最热
"""
from pypot.feetech import FeetechSTS3215IO
import time

IDS = {
    10: "right_hip_yaw", 11: "right_hip_roll", 12: "right_hip_pitch",
    13: "right_knee", 14: "right_ankle",
    20: "left_hip_yaw", 21: "left_hip_roll", 22: "left_hip_pitch",
    23: "left_knee", 24: "left_ankle",
    30: "neck_pitch", 31: "head_pitch", 32: "head_yaw", 33: "head_roll",
}

# 左右配对 (诊断右腿 stall)
PAIRS = [
    (20, 10, "hip_yaw"),
    (21, 11, "hip_roll"),
    (22, 12, "hip_pitch"),
    (23, 13, "knee"),
    (24, 14, "ankle"),
]

print(f"=== 读取时刻: {time.strftime('%H:%M:%S')} (walk 后越快越好) ===")
io = FeetechSTS3215IO("/dev/ttyACM0", baudrate=1000000)

# 读全部
data = {}
for sid, name in IDS.items():
    try:
        temp = io.get_present_temperature([sid])[0]
    except Exception as e:
        temp = None
    try:
        load = io.get_present_load([sid])[0]
    except Exception:
        load = None
    try:
        current = io.get_present_current([sid])[0]
    except Exception:
        current = None
    data[sid] = (name, temp, load, current)

print(f"\n{'ID':>3} {'name':22s} {'temp(°C)':>10} {'load':>8} {'current':>10}")
print("-" * 60)
for sid in sorted(IDS.keys()):
    name, temp, load, current = data[sid]
    t_str = f"{temp}" if temp is not None else "ERR"
    l_str = f"{load}" if load is not None else "ERR"
    c_str = f"{current}" if current is not None else "ERR"
    print(f"{sid:>3} {name:22s} {t_str:>10} {l_str:>8} {c_str:>10}")

print(f"\n=== 左右对比 (诊断右腿 stall) ===")
print(f"{'pair':12s} {'L_temp':>8} {'R_temp':>8} {'Δ':>6}  {'L_load':>8} {'R_load':>8} {'L_curr':>8} {'R_curr':>8}")
for left_id, right_id, pair_name in PAIRS:
    _, lt, ll, lc = data[left_id]
    _, rt, rl, rc = data[right_id]
    delta = (rt or 0) - (lt or 0) if lt is not None and rt is not None else "?"
    flag = "  ⚠️" if isinstance(delta, (int, float)) and delta >= 3 else ""
    delta_str = f"{delta:+}" if isinstance(delta, (int, float)) else str(delta)
    print(f"{pair_name:12s} {lt!s:>8} {rt!s:>8} {delta_str:>6}  {ll!s:>8} {rl!s:>8} {lc!s:>8} {rc!s:>8}{flag}")

print("")
print("=== 判定 ===")
# 找 right 比 left 高 ≥3°C 的关节
right_hotter = []
for left_id, right_id, pair_name in PAIRS:
    _, lt, _, _ = data[left_id]
    _, rt, _, _ = data[right_id]
    if lt is not None and rt is not None and rt - lt >= 3:
        right_hotter.append((pair_name, lt, rt, rt - lt))

if right_hotter:
    print("⚠️ 右腿明显比左腿热的关节:")
    for name, lt, rt, d in right_hotter:
        print(f"   {name}: L={lt}°C R={rt}°C Δ={d:+}°C")
    print("   → 假设 I (机械卡阻) 或 假设 F (过热) 直接命中, 该 ID 是嗡嗡声来源")
else:
    print("左右温度差均 <3°C → 假设 F/I 弱否定")
    print("可能 walk 时间太短温度还没显著上升, 或问题在 RL output 端非力矩饱和")
    print("下一步: 路径 1 vendor patch instrumentation 录 motor_targets vs present_pos")
