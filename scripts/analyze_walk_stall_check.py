"""离线分析 /tmp/walk_stall_check.jsonl"""
import json
from collections import defaultdict

data_by_phase = defaultdict(list)
with open("/tmp/walk_stall_check.jsonl") as f:
    for line in f:
        rec = json.loads(line)
        data_by_phase[rec["phase"]].append(rec)

print("="*70)
print(" walk stall J+K verify 分析")
print("="*70)

for phase, recs in data_by_phase.items():
    n = len(recs)
    left_low_n = sum(1 for r in recs if r["left"])
    right_low_n = sum(1 for r in recs if r["right"])
    # accel/gyro 平均
    ax = sum(r["accel"][0] for r in recs if r["accel"][0] is not None) / n
    ay = sum(r["accel"][1] for r in recs if r["accel"][1] is not None) / n
    az = sum(r["accel"][2] for r in recs if r["accel"][2] is not None) / n
    gx = sum(r["gyro"][0] for r in recs if r["gyro"][0] is not None) / n
    gy = sum(r["gyro"][1] for r in recs if r["gyro"][1] is not None) / n
    gz = sum(r["gyro"][2] for r in recs if r["gyro"][2] is not None) / n
    mag = (ax**2 + ay**2 + az**2) ** 0.5
    print(f"\n[{phase}] n={n}")
    print(f"  left_LOW : {left_low_n}/{n} ({100*left_low_n/n:5.1f}%)")
    print(f"  right_LOW: {right_low_n}/{n} ({100*right_low_n/n:5.1f}%)")
    print(f"  accel avg: [{ax:+6.3f}, {ay:+6.3f}, {az:+6.3f}]  |a|={mag:.3f}")
    print(f"  gyro  avg: [{gx:+7.4f}, {gy:+7.4f}, {gz:+7.4f}]")
