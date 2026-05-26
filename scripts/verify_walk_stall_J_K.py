"""
walk stall 假设 J + K 联合 verify (2026-05-26)

J: feet_contacts microswitch 物理传感器是否两边都正常 (BCM 22/27 + PUD_UP)
K: IMU BNO055 配置 (imu_upside_down=True axis_remap) 是否产生合理 accel/gyro

设计目标:
- 用户只做单次确定性动作 (按右脚 / 按左脚), 不做判断 (按 feedback_minimize_physical_operations)
- 脚本 12 秒采样, 50Hz, 输出 jsonl
- AI 离线分析 jsonl 判断 J + K 状态

跑法 (服务 stop 后):
  sudo systemctl stop duck-mcp-runtime mcp-openduck
  ~/venv_duck/bin/python /tmp/verify_walk_stall_J_K.py
  sudo systemctl start duck-mcp-runtime mcp-openduck

操作指令 (脚本自己 print, 用户按节奏):
  T+0s   静止 (鸭子悬空, 不要碰)
  T+2s   开始按住右脚底
  T+5s   松开右脚
  T+6s   开始按住左脚底
  T+9s   松开左脚
  T+10s  静止 1s
  T+11s  采集结束
"""

import time
import json
import sys
import traceback

# ===== Step 1: setup GPIO (feet contacts) =====
print("[1/3] GPIO setup ...", flush=True)
try:
    import RPi.GPIO as GPIO
    LEFT_FOOT_PIN = 22
    RIGHT_FOOT_PIN = 27
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LEFT_FOOT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(RIGHT_FOOT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print("    OK", flush=True)
except Exception as e:
    print(f"    GPIO setup FAILED: {e}", flush=True)
    sys.exit(1)

# ===== Step 2: setup BNO055 IMU =====
print("[2/3] IMU BNO055 setup ...", flush=True)
try:
    import adafruit_bno055
    import board
    import busio
    i2c = busio.I2C(board.SCL, board.SDA)
    imu = adafruit_bno055.BNO055_I2C(i2c)
    imu.mode = adafruit_bno055.IMUPLUS_MODE
    # 跟 vendor 一致: imu_upside_down=True 走 NEGATIVE/NEGATIVE/NEGATIVE
    imu.axis_remap = (
        adafruit_bno055.AXIS_REMAP_Y,
        adafruit_bno055.AXIS_REMAP_X,
        adafruit_bno055.AXIS_REMAP_Z,
        adafruit_bno055.AXIS_REMAP_NEGATIVE,
        adafruit_bno055.AXIS_REMAP_NEGATIVE,
        adafruit_bno055.AXIS_REMAP_NEGATIVE,
    )
    time.sleep(0.5)  # 让 axis_remap 生效
    # 试读一次
    test_accel = imu.acceleration
    test_gyro = imu.gyro
    print(f"    OK, test accel={test_accel}, gyro={test_gyro}", flush=True)
except Exception as e:
    print(f"    IMU setup FAILED: {type(e).__name__}: {e}", flush=True)
    print(traceback.format_exc(), flush=True)
    sys.exit(1)

# ===== Step 3: 12 秒采样, 50Hz =====
print("[3/3] 采样 12 秒 50Hz, 输出 /tmp/walk_stall_check.jsonl", flush=True)
print("", flush=True)
print("=== 操作指令 ===", flush=True)
print("  T+0~2s   静止 (不要碰鸭子)", flush=True)
print("  T+2~5s   按住右脚底", flush=True)
print("  T+5~6s   松开右脚 (静止)", flush=True)
print("  T+6~9s   按住左脚底", flush=True)
print("  T+9~11s  松开左脚 (静止)", flush=True)
print("  T+11s    结束", flush=True)
print("", flush=True)
print("3 秒后开始 ...", flush=True)
time.sleep(1)
print("  2", flush=True)
time.sleep(1)
print("  1", flush=True)
time.sleep(1)
print("=== START === T+0s (静止)", flush=True)

start = time.time()
out_path = "/tmp/walk_stall_check.jsonl"
last_marker = -1
markers = {
    2: "T+2s: 现在按右脚底",
    5: "T+5s: 松开右脚",
    6: "T+6s: 按左脚底",
    9: "T+9s: 松开左脚",
    11: "T+11s: 结束",
}

with open(out_path, "w") as f:
    while True:
        t = time.time() - start
        if t >= 12:
            break

        # 打印里程碑 (用户按节奏触发)
        sec = int(t)
        if sec > last_marker and sec in markers:
            print(f">>> {markers[sec]}", flush=True)
            last_marker = sec

        # 采样 feet contacts
        left_low = (GPIO.input(LEFT_FOOT_PIN) == GPIO.LOW)
        right_low = (GPIO.input(RIGHT_FOOT_PIN) == GPIO.LOW)

        # 采样 IMU
        try:
            accel = imu.acceleration  # m/s^2
            gyro = imu.gyro            # rad/s
        except Exception:
            accel = (None, None, None)
            gyro = (None, None, None)

        rec = {
            "t": round(t, 3),
            "left_contact": left_low,
            "right_contact": right_low,
            "accel": [round(a, 3) if a is not None else None for a in accel],
            "gyro": [round(g, 4) if g is not None else None for g in gyro],
        }
        f.write(json.dumps(rec) + "\n")

        # 50Hz
        time.sleep(max(0, 0.02 - (time.time() - start - t)))

print("=== END === 数据落 /tmp/walk_stall_check.jsonl", flush=True)
print("", flush=True)

# ===== 摘要统计 =====
print("[摘要]", flush=True)
import os
size = os.path.getsize(out_path)
print(f"  jsonl size: {size} bytes", flush=True)

# 简易摘要 - 让 AI 离线详细分析
contacts_left_count = 0
contacts_right_count = 0
total = 0
with open(out_path) as f:
    for line in f:
        rec = json.loads(line)
        total += 1
        if rec["left_contact"]:
            contacts_left_count += 1
        if rec["right_contact"]:
            contacts_right_count += 1

print(f"  total samples: {total}", flush=True)
print(f"  left contact LOW samples: {contacts_left_count} ({100*contacts_left_count/total:.1f}%)", flush=True)
print(f"  right contact LOW samples: {contacts_right_count} ({100*contacts_right_count/total:.1f}%)", flush=True)
print("", flush=True)
print("AI 会 ssh cat /tmp/walk_stall_check.jsonl 详细分析时间分布", flush=True)
