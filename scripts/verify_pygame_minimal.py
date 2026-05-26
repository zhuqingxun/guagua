"""单次 init 最小验证: ssh 用户态能否看到 joystick (对照 vendor PS4Controller 写法)"""
import pygame

pygame.init()
print(f"pygame {pygame.version.ver}")
print(f"get_count={pygame.joystick.get_count()}")
try:
    js = pygame.joystick.Joystick(0)
    js.init()
    print(f"name='{js.get_name()}' axes={js.get_numaxes()}")
    print(f"axis0={js.get_axis(0):.3f} axis1={js.get_axis(1):.3f}")
except pygame.error as e:
    print(f"ERR: {e}")
pygame.quit()
