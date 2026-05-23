#!/usr/bin/env python3
"""
Paused Trigger Consume Fix - 修 vendor LLM 模式无法稳定 unpause 的 bug

背景:
  - vendor 设计: A.triggered=True 一帧 -> toggle paused 一次 (物理按键脉冲语义)
  - LLM 模式: duck_start 让 self.A_pressed=True 持续多帧 (vendor 没复位机制),
    broadcast 100ms 周期发 A=True, RLWalk 50Hz 主循环, update_if_changed 在
    is_pressed 不变时不替换 self.buttons -> self.buttons.A.triggered 持续 True
    -> RLWalk 每帧都 toggle paused (50Hz!) -> 翻烧饼最终落点不定

修复 (1 行):
  if self.buttons.A.triggered 处理完后立刻 self.buttons.A.triggered = False
  -> 处理完即 consume, 即使后续帧 self.buttons 不替换, triggered 也不再 True
  -> 单次 toggle, paused 稳定切换

保留 vendor 设计哲学: 启动后默认锁定, LLM 调 duck_start 主动解锁 (Arm/Disarm 安全语义).

幂等: 跑过的话再跑无副作用.
"""
import sys
from pathlib import Path

TARGET = Path("/home/raspios/open_duck_mini_ws/Open_Duck_Mini_Runtime/scripts/v2_rl_walk_mujoco_mcp.py")

OLD_BLOCK = """                    if self.buttons.A.triggered:
                        print("self.buttons.A.triggered")
                        self.paused = not self.paused
                        if self.paused:
                            print("PAUSE")
                        else:
                            print("UNPAUSE")
"""

NEW_BLOCK = """                    if self.buttons.A.triggered:
                        print("self.buttons.A.triggered")
                        self.paused = not self.paused
                        if self.paused:
                            print("PAUSE")
                        else:
                            print("UNPAUSE")
                        self.buttons.A.triggered = False
"""


def main() -> int:
    if not TARGET.exists():
        print(f"FAIL: {TARGET} not found", file=sys.stderr)
        return 1

    text = TARGET.read_text(encoding="utf-8")

    if NEW_BLOCK in text:
        print("OK: already patched (trigger consume present), no-op")
        return 0

    count = text.count(OLD_BLOCK)
    if count == 0:
        print("FAIL: old block not found - file may have diverged", file=sys.stderr)
        return 1
    if count > 1:
        print(f"FAIL: old block found {count} times - ambiguous", file=sys.stderr)
        return 1

    new_text = text.replace(OLD_BLOCK, NEW_BLOCK, 1)
    TARGET.write_text(new_text, encoding="utf-8")
    print(f"OK: patched paused trigger consume in {TARGET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
