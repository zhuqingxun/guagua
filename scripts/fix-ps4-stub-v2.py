#!/usr/bin/env python3
"""
PS4 Stub Fix v2 - 修复 _StubPS4 数据结构错误

旧 stub (v1, 2026-05-23 11:21) 返回 [0.0]*7 (单 list 7 元素),
导致 merge_commands() 的 `p_last, p_buttons, p_left, p_right = ps4_values` 失败
报 "ValueError: too many values to unpack (expected 4)".

新 stub (v2) 返回 4 元 tuple (np.zeros(7), Buttons(), 0.0, 0.0), 匹配 PS4Controller.get_last_command()
真实签名 (Open_Duck_Mini_Runtime/mini_bdx_runtime/.../ps4_controller.py:186-191).

幂等: 跑过的话再跑无副作用.
"""
import sys
from pathlib import Path

TARGET = Path("/home/raspios/open_duck_mini_ws/Open_Duck_Mini_Runtime/scripts/v2_rl_walk_mujoco_mcp.py")

OLD_BLOCK = """                class _StubPS4:
                    def get_last_command(self):
                        return [0.0] * 7
"""

NEW_BLOCK = """                class _StubPS4:
                    def __init__(self):
                        self._buttons = Buttons()
                    def get_last_command(self):
                        return (
                            np.zeros(7, dtype=np.float32),
                            self._buttons,
                            0.0,
                            0.0,
                        )
"""

def main() -> int:
    if not TARGET.exists():
        print(f"FAIL: {TARGET} not found", file=sys.stderr)
        return 1

    text = TARGET.read_text(encoding="utf-8")

    if NEW_BLOCK in text:
        print("OK: already patched (v2 stub present), no-op")
        return 0

    count = text.count(OLD_BLOCK)
    if count == 0:
        print("FAIL: old stub block not found - file may have been modified, abort", file=sys.stderr)
        return 1
    if count > 1:
        print(f"FAIL: old stub block found {count} times - ambiguous, abort", file=sys.stderr)
        return 1

    new_text = text.replace(OLD_BLOCK, NEW_BLOCK, 1)
    TARGET.write_text(new_text, encoding="utf-8")
    print(f"OK: patched v1 -> v2 stub in {TARGET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
