import pygame
from threading import Thread
from queue import Queue
import time
import numpy as np
from mini_bdx_runtime.buttons import Buttons

# Movement and head control limits
X_RANGE = [-0.15, 0.15]      # Linear velocity in X (forward/backward)
Y_RANGE = [-0.2, 0.2]        # Linear velocity in Y (sideways)
YAW_RANGE = [-1.0, 1.0]      # Angular velocity in Yaw

# Head movement ranges (radians)
NECK_PITCH_RANGE = [-0.34, 1.1]
HEAD_PITCH_RANGE = [-0.78, 0.3]
HEAD_YAW_RANGE = [-0.5, 0.5]
HEAD_ROLL_RANGE = [-0.5, 0.5]

# Deadzone filter to prevent small drifting motion
def apply_deadzone(val, threshold=0.1):
    return 0.0 if abs(val) < threshold else val

# Scale joystick input (-1 to 1) to desired range
def scale(val, rng):
    return val * rng[1] if val >= 0 else val * abs(rng[0])

class PS4Controller:
    def __init__(self, command_freq, only_head_control=False):
        self.command_freq = command_freq
        self.head_control_mode = only_head_control
        self.only_head_control = only_head_control

        # 7 command outputs: [vx, vy, yaw, neck_pitch, head_pitch, head_yaw, head_roll]
        self.last_commands = [0.0] * 7
        self.last_left_trigger = 0.0
        self.last_right_trigger = 0.0

        # Initialize pygame (does not require joystick to be attached)
        pygame.init()

        # Lazy joystick attach: do not raise when no controller is present
        self.p1 = None
        self._attached = False

        self.cmd_queue = Queue(maxsize=1)

        # Button state flags
        self.A_pressed = False
        self.B_pressed = False
        self.X_pressed = False
        self.Y_pressed = False
        self.LB_pressed = False
        self.RB_pressed = False

        self.buttons = Buttons()

        # Try to attach joystick if already connected at startup
        self.try_attach()

        # Start the background command generator thread (always runs)
        Thread(target=self.commands_worker, daemon=True).start()

    def try_attach(self):
        """Try to attach to joystick index 0. Returns True on success, False otherwise.

        Safe to call repeatedly. Called once at __init__ and on JOYDEVICEADDED event.
        """
        if self._attached:
            return True
        try:
            # Re-init joystick subsystem so SDL re-enumerates devices
            pygame.joystick.quit()
            pygame.joystick.init()
            count = pygame.joystick.get_count()
            if count <= 0:
                return False
            self.p1 = pygame.joystick.Joystick(0)
            self.p1.init()
            self._attached = True
            print(f"[PS4Controller] Attached with {self.p1.get_numaxes()} axes.")
            return True
        except pygame.error as e:
            self.p1 = None
            self._attached = False
            return False

    def detach(self):
        """Mark controller as detached. Called on JOYDEVICEREMOVED event."""
        self.p1 = None
        self._attached = False
        # Reset button states so stale presses don't leak
        self.A_pressed = False
        self.B_pressed = False
        self.X_pressed = False
        self.Y_pressed = False
        self.LB_pressed = False
        self.RB_pressed = False
        print("[PS4Controller] Detached")

    def commands_worker(self):
        while True:
            if self._attached:
                try:
                    self.cmd_queue.put(self.get_commands())
                except pygame.error:
                    # Controller disappeared mid-read
                    self.detach()
            # If not attached, just sleep; do not push to queue.
            # get_last_command() returns stub when queue is empty.
            time.sleep(1 / self.command_freq)

    def get_commands(self):
        last_commands = self.last_commands

        # Read joystick axes and apply deadzone
        l_x = apply_deadzone(self.p1.get_axis(0))  # Left stick left/right
        l_y = apply_deadzone(self.p1.get_axis(1))  # Left stick up/down
        r_x = apply_deadzone(self.p1.get_axis(3))  # Right stick left/right (Yaw)
        r_y = apply_deadzone(self.p1.get_axis(4))  # Right stick up/down (not used here)

        # Triggers: L2 (axis 2), R2 (axis 5), normalized from [-1, 1] to [0, 1]
        left_trigger = np.around((self.p1.get_axis(2) + 1) / 2, 3)
        right_trigger = np.around((self.p1.get_axis(5) + 1) / 2, 3)

        if left_trigger < 0.1:
            left_trigger = 0
        if right_trigger < 0.1:
            right_trigger = 0

        if not self.head_control_mode:
            # Convert joystick values to robot movement commands
            lin_vel_x = -l_y  # Forward push on stick = positive velocity
            lin_vel_y = -l_x  # Left push = positive Y
            ang_vel = -r_x     # Right stick controls yaw

            last_commands[0] = scale(lin_vel_x, X_RANGE)
            last_commands[1] = scale(lin_vel_y, Y_RANGE)
            last_commands[2] = scale(ang_vel, YAW_RANGE)
        else:
            # When in head control mode, stop robot movement
            last_commands[0] = 0.0
            last_commands[1] = 0.0
            last_commands[2] = 0.0
            last_commands[3] = 0.0  # Neck pitch not implemented

            # Map left/right stick to head movements
            head_yaw = l_x
            head_pitch = l_y
            head_roll = r_x

            last_commands[4] = scale(head_pitch, HEAD_PITCH_RANGE)
            last_commands[5] = scale(head_yaw, HEAD_YAW_RANGE)
            last_commands[6] = scale(head_roll, HEAD_ROLL_RANGE)

        # Handle button events
        # NOTE: pygame.event.get() also drains JOYDEVICEADDED/REMOVED events.
        # Main loop also calls pygame.event.get() at ~2Hz to handle hotplug;
        # both consumers see different snapshots but that is OK -- hotplug events
        # are only relevant in the main loop, button events only here.
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if self.p1.get_button(0):  # X Button: paused
                    self.A_pressed = True
                if self.p1.get_button(1):  # Circle Button: play_random_sound
                    self.B_pressed = True
                if self.p1.get_button(3):  # Square Button: projector
                    self.X_pressed = True
                if self.p1.get_button(2):  # Triangle Button: head
                    self.Y_pressed = True
                    # Toggle head control mode if allowed
                    if not self.only_head_control:
                        self.head_control_mode = not self.head_control_mode
                        if self.head_control_mode == True:
                            print('Switch head control mode')
                        else:
                            print('Exit head control mode')

                if self.p1.get_button(4):  # L1: phase_frequency_factor = 1.3
                    self.LB_pressed = True
                if self.p1.get_button(5):  # R1: phase_frequency_factor = 0.7
                    self.RB_pressed = True

            if event.type == pygame.JOYBUTTONUP:
                self.A_pressed = False
                self.B_pressed = False
                self.X_pressed = False
                self.Y_pressed = False
                self.LB_pressed = False
                self.RB_pressed = False

        # Read D-pad (hat) vertical direction
        up_down = self.p1.get_hat(0)[1]
        pygame.event.pump()  # Update internal event state

        return (
            np.around(last_commands, 3),
            self.A_pressed,
            self.B_pressed,
            self.X_pressed,
            self.Y_pressed,
            self.LB_pressed,
            self.RB_pressed,
            left_trigger,
            right_trigger,
            up_down,
        )

    def get_last_command(self):
        # When not attached, return stub 4-tuple matching merge_commands unpack signature
        if not self._attached:
            return (
                np.zeros(7, dtype=np.float32),
                self.buttons,
                0.0,
                0.0,
            )
        try:
            (
                self.last_commands,
                A_pressed,
                B_pressed,
                X_pressed,
                Y_pressed,
                LB_pressed,
                RB_pressed,
                self.last_left_trigger,
                self.last_right_trigger,
                up_down,
            ) = self.cmd_queue.get(False)
        except Exception:
            A_pressed = B_pressed = X_pressed = Y_pressed = LB_pressed = RB_pressed = False
            up_down = 0

        # Update the Buttons helper object
        self.buttons.update(
            A_pressed,
            B_pressed,
            X_pressed,
            Y_pressed,
            LB_pressed,
            RB_pressed,
            up_down == 1,
            up_down == -1,
        )

        return (
            self.last_commands,
            self.buttons,
            self.last_left_trigger,
            self.last_right_trigger,
        )

# Run this for manual testing
if __name__ == "__main__":
    controller = PS4Controller(20)
    while True:
        print(controller.get_last_command())
        time.sleep(0.05)
