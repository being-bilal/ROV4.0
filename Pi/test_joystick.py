import pygame
import time

# Initialize pygame and the joystick
pygame.init()
pygame.joystick.init()

# Check if a joystick is connected
if pygame.joystick.get_count() == 0:
    print("No joystick connected.")
    exit(1)

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(joystick.get_name())

print(f"Joystick detected: {joystick.get_name()}")
print(f"Number of axes: {joystick.get_numaxes()}")
print("Move each stick or axis to see which number changes.\nPress Ctrl+C to stop.")

try:
    while True:
        pygame.event.pump()  # Allow pygame to read events

        for i in range(joystick.get_numaxes()):
            val = joystick.get_axis(i)
        print()
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nDone.")
finally:
    pygame.quit()
