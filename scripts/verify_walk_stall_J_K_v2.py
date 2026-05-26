"""
walk stall 假设 J + K 联合 verify v2 (2026-05-26)

v2 改动 (相对 v1):
- self-paced: 不靠时间表, 脚本检测 GPIO state 自动推进
- 每 phase 30 秒超时 (超时 = sensor 失效 → 假设 J 直接命中)
- IMU 全程采样
- 输出 + flush 强化

跑法 (服务 stop 后, 用户终端必须 ssh -t):
  ssh -t duck "bash /tmp/verify_walk_stall_runner.sh"
"""

import time
import json
import sys
import traceback

def out(msg):
    """强 flush print"""
    print(msg, flush=True)
    sys.stdout.flush()

# ===== Step 1: setup GPIO =====
out("[1/3] GPIO setup ...")
try:
    import RPi.GPIO as GPIO
    LEFT_FOOT_PIN = 22
    RIGHT_FOOT_PIN = 27
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LEFT_FOOT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(RIGHT_FOOT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    out("    OK")
except Exception as e:
    out(f"    GPIO setup FAILED: {e}")
    sys.exit(1)

# ===== Step 2: setup BNO055 IMU =====
out("[2/3] IMU BNO055 setup ...")
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
    test_accel = imu.acceleration
    test_gyro = imu.gyro
    out(f"    OK, baseline accel={test_accel}")
    out(f"    baseline gyro={test_gyro}")
except Exception as e:
    out(f"    IMU setup FAILED: {type(e).__name__}: {e}")
    out(traceback.format_exc())
    sys.exit(1)

# ===== Step 3: self-paced verify =====
out("[3/3] self-paced verify (每 phase 30 秒超时)")
out("")

def read_state():
    """读 GPIO + IMU 一次"""
    left = (GPIO.input(LEFT_FOOT_PIN) == GPIO.LOW)
    right = (GPIO.input(RIGHT_FOOT_PIN) == GPIO.LOW)
    try:
        accel = imu.acceleration
        gyro = imu.gyro
    except Exception:
        accel = (None, None, None)
        gyro = (None, None, None)
    return left, right, accel, gyro

def sample_for(out_f, label, duration_s, start_t):
    """label 当前 phase, 采 duration_s 秒, 写 jsonl"""
    end_t = time.time() + duration_s
    while time.time() < end_t:
        t = time.time() - start_t
        left, right, accel, gyro = read_state()
        rec = {
            "phase": label,
            "t": round(t, 3),
            "left": left,
            "right": right,
            "accel": [round(a, 3) if a is not None else None for a in accel],
            "gyro": [round(g, 4) if g is not None else None for g in gyro],
        }
        out_f.write(json.dumps(rec) + "\n")
        out_f.flush()
        time.sleep(0.02)

def wait_for(condition_fn, label, timeout_s, start_t, out_f):
    """等 condition_fn() 返回 True, 期间也采样写 jsonl. 超时返回 False"""
    end_t = time.time() + timeout_s
    while time.time() < end_t:
        t = time.time() - start_t
        left, right, accel, gyro = read_state()
        rec = {
            "phase": label,
            "t": round(t, 3),
            "left": left,
            "right": right,
            "accel": [round(a, 3) if a is not None else None for a in accel],
            "gyro": [round(g, 4) if g is not None else None for g in gyro],
        }
        out_f.write(json.dumps(rec) + "\n")
        out_f.flush()
        if condition_fn(left, right):
            return True
        time.sleep(0.02)
    return False

out_path = "/tmp/walk_stall_check.jsonl"
start_t = time.time()

with open(out_path, "w") as out_f:
    # === phase 1: 2 秒 baseline 静止 ===
    out(">>> phase 1: 静止 baseline (2 秒, 不要碰鸭子)")
    sample_for(out_f, "baseline_idle", 2.0, start_t)

    # === phase 2: 等用户按右脚 ===
    out(">>> phase 2: 请按住右脚底 (30 秒超时)")
    ok = wait_for(lambda l, r: r, "waiting_right_press", 30, start_t, out_f)
    if not ok:
        out("    !!! 30 秒未检测到 right_contact=LOW → 假设 J 命中 (右脚 sensor 卡死)")
    else:
        out("    detected right_press, 继续采样 2 秒")
        sample_for(out_f, "right_pressed", 2.0, start_t)

    # === phase 3: 等用户松开右脚 ===
    out(">>> phase 3: 请松开右脚 (30 秒超时)")
    ok = wait_for(lambda l, r: not r, "waiting_right_release", 30, start_t, out_f)
    if not ok:
        out("    !!! 30 秒右脚未释放, 跳过")
    else:
        out("    detected right_release")
        sample_for(out_f, "after_right_release", 1.0, start_t)

    # === phase 4: 等用户按左脚 ===
    out(">>> phase 4: 请按住左脚底 (30 秒超时)")
    ok = wait_for(lambda l, r: l, "waiting_left_press", 30, start_t, out_f)
    if not ok:
        out("    !!! 30 秒未检测到 left_contact=LOW → 左脚 sensor 卡死")
    else:
        out("    detected left_press, 继续采样 2 秒")
        sample_for(out_f, "left_pressed", 2.0, start_t)

    # === phase 5: 等用户松开左脚 ===
    out(">>> phase 5: 请松开左脚 (30 秒超时)")
    ok = wait_for(lambda l, r: not l, "waiting_left_release", 30, start_t, out_f)
    if not ok:
        out("    !!! 30 秒左脚未释放")
    else:
        out("    detected left_release")
        sample_for(out_f, "after_left_release", 1.0, start_t)

    # === phase 6: 双脚同时按 (验证两边能否独立切换) ===
    out(">>> phase 6: 现在双脚同时按住 (30 秒超时)")
    ok = wait_for(lambda l, r: l and r, "waiting_both_press", 30, start_t, out_f)
    if not ok:
        out("    !!! 30 秒未检测到 both press → 至少一边 sensor 有问题")
    else:
        out("    detected both press, 采样 2 秒")
        sample_for(out_f, "both_pressed", 2.0, start_t)

    out(">>> all phases done, 松开双脚, 采集 1 秒结束")
    sample_for(out_f, "final_idle", 1.0, start_t)

out("")
out("=== DONE ===")
out(f"    jsonl: {out_path}")

# 摘要
import os
size = os.path.getsize(out_path)
out(f"    size: {size} bytes")

# 各 phase 摘要
from collections import Counter
phase_counter = Counter()
left_low_count = 0
right_low_count = 0
total = 0
with open(out_path) as f:
    for line in f:
        rec = json.loads(line)
        phase_counter[rec["phase"]] += 1
        if rec["left"]:
            left_low_count += 1
        if rec["right"]:
            right_low_count += 1
        total += 1

out(f"    total samples: {total}")
out(f"    left LOW: {left_low_count} ({100*left_low_count/total:.1f}%)")
out(f"    right LOW: {right_low_count} ({100*right_low_count/total:.1f}%)")
out("    phase samples:")
for ph, n in phase_counter.most_common():
    out(f"      {ph}: {n}")
