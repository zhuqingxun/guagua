#!/usr/bin/env python3
"""
Duck WS Unpause Experiment - 验证 mechanism 通路 (不改 vendor/config)

背景:
  - duck-mcp-runtime 启动时 start_paused=true (vendor 默认), self.paused=True
  - line 476 if self.paused: continue → 跳过 RL/写舵机 → 鸭子不动
  - line 469 if self.buttons.A.triggered: self.paused = not self.paused → 解锁路径
  - vendor bug: duck.start() 让 self.A_pressed=True 持续到下次 set_commands,
    broadcast 每 100ms 发一次 A=True, RLWalk 50Hz toggle 多次 paused 状态翻烧饼

验证:
  发 duck_start 后立刻发 duck_move_forward (set_commands 不传 A → A=False),
  使 A=True 只持续 < broadcast 一帧 (100ms) → 单次 trigger → 单次 toggle
  → paused True->False (UNPAUSE) → 鸭子走

不修改任何代码/配置, 跑完原状, 失败也无副作用.
"""
import asyncio
import json
import sys
import time

import websockets

URI = "ws://127.0.0.1:6789"


async def send_cmd(ws, cmd: str, args: dict = None, label: str = ""):
    payload = {"cmd": cmd, "args": args or {}}
    msg = json.dumps(payload)
    t0 = time.time()
    await ws.send(msg)
    print(f"[{time.time():.3f}] >>> {label or cmd} sent: {msg}")


async def drain_responses(ws, duration_s: float):
    """收 duration_s 秒内的全部 server 响应/broadcast, 不阻塞"""
    end = time.time() + duration_s
    while time.time() < end:
        try:
            timeout = max(0.0, end - time.time())
            msg = await asyncio.wait_for(ws.recv(), timeout=timeout)
            data = json.loads(msg) if msg else None
            # 只打印 cmd 响应 和 buttons 状态变化, 过滤 commands heartbeat
            if isinstance(data, dict):
                if "ok" in data:
                    print(f"[{time.time():.3f}] <<< RESPONSE: {msg}")
                elif "buttons" in data:
                    b = data.get("buttons", {})
                    if any(b.values()):  # 只打有非零 button 的帧
                        print(f"[{time.time():.3f}] <<< BUTTON: {b} cmds={data.get('commands')}")
        except asyncio.TimeoutError:
            break
        except Exception as e:
            print(f"[{time.time():.3f}] <<< ERROR: {e}")
            break


async def experiment(experiment_id: str, delay_after_start_s: float):
    """
    一次实验序列:
    1. 连 ws
    2. 发 duck_start (A=True)
    3. sleep delay_after_start_s
    4. 发 duck_move_forward distance=2 (set_commands(0,-1,0,0) → A=False)
    5. drain 8 秒响应

    delay_after_start_s 越小, A=True 持续越短, paused toggle 次数越少.
    """
    print(f"\n===== Experiment {experiment_id}: delay_after_start = {delay_after_start_s}s =====")
    async with websockets.connect(URI) as ws:
        await send_cmd(ws, "duck_start", label="STEP1 duck_start")
        await asyncio.sleep(delay_after_start_s)
        await send_cmd(ws, "duck_move_forward", {"distance": 2}, label="STEP2 duck_move_forward(2)")
        # drain 响应 8 秒 (move_forward 100 步 * 0.05s = 5s, 加余量)
        await drain_responses(ws, 8.0)
    print(f"===== Experiment {experiment_id} complete =====")


async def main():
    if len(sys.argv) < 2:
        print("Usage: duck-ws-unpause-experiment.py <delay_seconds>")
        print("  e.g. 0.05  (单帧, 期望单次 toggle → unpause → 鸭子走)")
        print("       0.5   (5 帧, 期望偶数次 toggle → 鸭子又锁)")
        print("       1.0   (10 帧)")
        sys.exit(1)
    delay = float(sys.argv[1])
    await experiment(f"delay_{delay}s", delay)


if __name__ == "__main__":
    asyncio.run(main())
