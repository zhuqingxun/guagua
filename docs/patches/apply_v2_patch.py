#!/usr/bin/env python3
"""Apply hotplug patch to v2_rl_walk_mujoco_mcp.py on duck."""

import sys

TARGET = "/home/raspios/open_duck_mini_ws/Open_Duck_Mini_Runtime/scripts/v2_rl_walk_mujoco_mcp.py"

with open(TARGET, "r", encoding="utf-8") as f:
    src = f.read()

# ----- Patch 1: replace _StubPS4 try/except block with direct PS4Controller call -----
OLD_BLOCK = """            self.mcp_controller = MCPController()
            try:
                self.ps4_controller = PS4Controller(self.command_freq)
            except Exception as _ps4_err:
                print(f"[WARN] PS4 unavailable, using stub: {_ps4_err}")
                class _StubPS4:
                    def __init__(self):
                        self._buttons = Buttons()
                    def get_last_command(self):
                        return (
                            np.zeros(7, dtype=np.float32),
                            self._buttons,
                            0.0,
                            0.0,
                        )
                self.ps4_controller = _StubPS4()
"""

NEW_BLOCK = """            self.mcp_controller = MCPController()
            # PS4Controller now has built-in lazy attach + detached stub.
            # No try/except needed: __init__ never raises when joystick is absent.
            self.ps4_controller = PS4Controller(self.command_freq)
"""

if OLD_BLOCK not in src:
    print("ERROR: could not locate Patch 1 old block. Aborting.")
    sys.exit(1)

src = src.replace(OLD_BLOCK, NEW_BLOCK, 1)
print("[patch 1] _StubPS4 block replaced")

# ----- Patch 2: add pygame event pump every 25 frames in run() main loop -----
# Insert hotplug pump right at the top of the while True body, BEFORE the
# `left_trigger = 0` reset. We use the existing `i` counter from `i = 0` above.
OLD_LOOP_HEAD = """            while True:
                left_trigger = 0
                right_trigger = 0
                self.left_trigger = 0
                self.right_trigger = 0"""

NEW_LOOP_HEAD = """            while True:
                # Hotplug: every 25 frames (~0.5s @ 50Hz) drain pygame events
                # so JOYDEVICEADDED / JOYDEVICEREMOVED trigger attach/detach.
                # Without this, a controller plugged in after startup is invisible
                # until process restart.
                if self.commands and i % 25 == 0:
                    for ev in pygame.event.get():
                        if ev.type == pygame.JOYDEVICEADDED:
                            self.ps4_controller.try_attach()
                        elif ev.type == pygame.JOYDEVICEREMOVED:
                            self.ps4_controller.detach()

                left_trigger = 0
                right_trigger = 0
                self.left_trigger = 0
                self.right_trigger = 0"""

if OLD_LOOP_HEAD not in src:
    print("ERROR: could not locate Patch 2 old block. Aborting.")
    sys.exit(1)

src = src.replace(OLD_LOOP_HEAD, NEW_LOOP_HEAD, 1)
print("[patch 2] hotplug event pump inserted into run() loop")

# ----- Patch 3: ensure `import pygame` is present at top -----
# Original file does not import pygame directly; it comes in through ps4_controller.
# But our hotplug pump references pygame.event / pygame.JOYDEVICEADDED, so import explicitly.
if "import pygame" not in src.split("class RLWalk")[0]:
    # Insert after the first import block
    src = src.replace(
        "import time\nimport pickle\n",
        "import time\nimport pickle\nimport pygame\n",
        1,
    )
    print("[patch 3] added `import pygame` at top")
else:
    print("[patch 3] `import pygame` already present, skipped")

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(src)

print("DONE. Patched file written.")
