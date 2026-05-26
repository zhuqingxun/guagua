"""
IMU baseline 测试 (鸭子地上 paused, 不 walk)

目标: 区分 walk_stall_check.jsonl 中 baseline X=+2.56 是
  (a) 悬空姿态因素 → 假设 K 否定 (X 应在地上 ≈ 0)
  (b) IMU 配置 bug → 假设 K 命中 (X 仍 ≈ +2.56)

跑法: 由 verify_imu_ground_runner.sh 调用
"""
import time
import json
import sys
import traceback

def out(msg):
    print(msg, flush=True)
    sys.stdout.flush()

out("[1/2] IMU BNO055 setup (跟 vendor 一致: imu_upside_down=True)")
try:
    import adafruit_bno055
    import board
    import busio
    i2c = busio.I2C(board.SCL, board.SDA)
    imu = adafruit_bno055.BNO055_I2C(i2c)
    imu.mode = adafruit_bno055.IMUPLUS_MODE
    imu.axis_remap = (
        adafruit_bno055.AXIS_REMAP_Y,
        adafruit_bno055.AXIS_REMAP_X,
        adafruit_bno055.AXIS_REMAP_Z,
        adafruit_bno055.AXIS_REMAP_NEGATIVE,
        adafruit_bno055.AXIS_REMAP_NEGATIVE,
        adafruit_bno055.AXIS_REMAP_NEGATIVE,
    )
    time.sleep(0.5)
    out("    OK")
except Exception as e:
    out(f"    FAILED: {type(e).__name__}: {e}")
    out(traceback.format_exc())
    sys.exit(1)

out("[2/2] 采样 5 秒 50Hz, 鸭子保持站立不动")

def safe_round(v, n):
    return round(v, n) if v is not None else None

start = time.time()
samples = []
out_path = "/tmp/imu_ground_check.jsonl"
none_count = 0

with open(out_path, "w") as f:
    while True:
        t = time.time() - start
        if t >= 5:
            break
        try:
            acc = imu.acceleration
            gyr = imu.gyro
            if acc is None or gyr is None:
                none_count += 1
                time.sleep(0.02)
                continue
            ax, ay, az = acc
            gx, gy, gz = gyr
        except Exception as e:
            none_count += 1
            time.sleep(0.02)
            continue
        # 任一元素 None 跳过 (BNO055 偶发 None)
        if any(v is None for v in (ax, ay, az, gx, gy, gz)):
            none_count += 1
            time.sleep(0.02)
            continue
        rec = {
            "t": round(t, 3),
            "accel": [round(ax, 3), round(ay, 3), round(az, 3)],
            "gyro": [round(gx, 4), round(gy, 4), round(gz, 4)],
        }
        samples.append(rec)
        f.write(json.dumps(rec) + "\n")
        time.sleep(0.02)

if none_count > 0:
    out(f"    skipped {none_count} samples (BNO055 returned None)")

out("=== DONE ===")
out(f"    jsonl: {out_path}, samples: {len(samples)}")

# 平均
n = len(samples)
ax = sum(r["accel"][0] for r in samples) / n
ay = sum(r["accel"][1] for r in samples) / n
az = sum(r["accel"][2] for r in samples) / n
gx = sum(r["gyro"][0] for r in samples) / n
gy = sum(r["gyro"][1] for r in samples) / n
gz = sum(r["gyro"][2] for r in samples) / n
mag = (ax**2 + ay**2 + az**2) ** 0.5

# 标准差
import math
def stdev(vals, m):
    return math.sqrt(sum((v-m)**2 for v in vals) / len(vals))

ax_sd = stdev([r["accel"][0] for r in samples], ax)
ay_sd = stdev([r["accel"][1] for r in samples], ay)
az_sd = stdev([r["accel"][2] for r in samples], az)

out("")
out("=== 地上 baseline 结果 ===")
out(f"  accel avg: [{ax:+6.3f}, {ay:+6.3f}, {az:+6.3f}]  |a|={mag:.3f}")
out(f"  accel sd : [{ax_sd:6.3f}, {ay_sd:6.3f}, {az_sd:6.3f}]")
out(f"  gyro  avg: [{gx:+7.4f}, {gy:+7.4f}, {gz:+7.4f}]")

out("")
out("=== 对比悬空 baseline (5/26 22:27) ===")
out(f"  悬空: accel=[+2.564, +0.069, +9.583]  |a|=9.92")
out(f"  地上: accel=[{ax:+6.3f}, {ay:+6.3f}, {az:+6.3f}]  |a|={mag:.3f}")
out(f"  ΔX  : {ax - 2.564:+.3f}")
out(f"  ΔY  : {ay - 0.069:+.3f}")
out(f"  ΔZ  : {az - 9.583:+.3f}")
out("")
out("=== 判定 ===")
if abs(ax) > 1.5:
    out(f"  ⚠️ 地上 X 仍然 {ax:+.2f} (>|1.5|) → 假设 K 可能命中 (IMU 配置 bug)")
    out(f"     sim 训练 obs[3:6] 预期 [0, 0, ±9.8], real 持续偏置 → 系统性向某侧倒")
else:
    out(f"  ✅ 地上 X={ax:+.2f} (在 ±1.5 内) → 假设 K 否定 (悬空 +2.56 是姿态因素)")
    out(f"     继续排查 C IMU 动态噪声 / D dof_vel / I 机械承重")
