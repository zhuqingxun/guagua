"""
pygame.joystick 热插拔 verify v2 (2026-05-24, 事件机制)

第一版 (quit+init loop) 失败了——SDL 2.28 不会在 joystick 子系统 reinit 时重扫描设备.
本版改用 SDL 原生热插拔事件 JOYDEVICEADDED / JOYDEVICEREMOVED.

流程: 跑 40 秒, 每秒 pump pygame.event.get() + 处理热插拔事件 + 周期 (每 5s) 打印状态.

操作时间表:
- T=00-10: 别动 (看初始连接状态)
- T≈10s: 长按 PS 键关掉手柄
- T=10-25: 别动 (看 REMOVED 事件 + count→0)
- T≈25s: 按 PS 键重连手柄
- T=25-40: 别动 (看 ADDED 事件 + count→1)
"""

import time
import pygame

DURATION = 60

pygame.init()
print(f"pygame {pygame.version.ver}", flush=True)
print(f"initial count={pygame.joystick.get_count()}", flush=True)

joysticks = {}
# 初始已有的设备先 attach 上
for i in range(pygame.joystick.get_count()):
    j = pygame.joystick.Joystick(i)
    j.init()
    joysticks[j.get_instance_id()] = j
    print(f"T=00 INIT-ATTACH idx={i} iid={j.get_instance_id()} name='{j.get_name()}' axes={j.get_numaxes()}", flush=True)

start = time.time()
last_status = -1
while time.time() - start < DURATION:
    t = int(time.time() - start)
    for ev in pygame.event.get():
        if ev.type == pygame.JOYDEVICEADDED:
            j = pygame.joystick.Joystick(ev.device_index)
            j.init()
            joysticks[j.get_instance_id()] = j
            print(f"T={t:02d} >>> ADDED idx={ev.device_index} iid={j.get_instance_id()} name='{j.get_name()}' axes={j.get_numaxes()}", flush=True)
        elif ev.type == pygame.JOYDEVICEREMOVED:
            if ev.instance_id in joysticks:
                joysticks[ev.instance_id].quit()
                del joysticks[ev.instance_id]
            print(f"T={t:02d} <<< REMOVED iid={ev.instance_id} (remaining={len(joysticks)})", flush=True)
    if t != last_status and t % 5 == 0:
        last_status = t
        if joysticks:
            js = next(iter(joysticks.values()))
            ax = [round(js.get_axis(i), 2) for i in range(min(2, js.get_numaxes()))]
            print(f"T={t:02d} STATUS count={len(joysticks)} axes={ax}", flush=True)
        else:
            print(f"T={t:02d} STATUS count=0", flush=True)
    time.sleep(0.2)

pygame.quit()
print("=== done ===", flush=True)
