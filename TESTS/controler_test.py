import pigpio
import pygame
import time

pygame.init()
pygame.joystick.init()

con = pygame.joystick.Joystick(0)
con.init()

# ---- PS4 Controller Mappings ----
# You can check these using the pygame event debugger if needed.
BUTTON_CROSS = 0    # Cross (Bottom button)
BUTTON_CIRCLE = 1   # Circle (Right button)
BUTTON_TRIANGLE = 2 # Triangle (Top button)
BUTTON_SQUARE = 3   # Square (Left button)
BUTTON_OPTIONS = 9  # Options button (used as toggle)

LEFT_JOYSTICK_X = 0  # Left stick horizontal
LEFT_JOYSTICK_Y = 1  # Left stick vertical

# ---- Thruster setup ----
thruster_1 = 0  # Center thruster 1
thruster_2 = 0  # Center thruster 2
thruster_3 = 0  # Left thruster
thruster_4 = 0  # Right thruster
thruster_pins = [thruster_1, thruster_2, thruster_3, thruster_4]

'''
pi = pigpio.pi()
for pin in thruster_pins:
    pi.set_servo_pulsewidth(pin, 1500)
'''

def map_values(value):
    """Maps joystick value (-1 to 1) to PWM pulse width."""
    return int(1500 + (value * 300)) if abs(value) > 0 else 1500

DEADZONE = 0.2
thrusters_enabled = True
toggle_last_state = False

print("PS4 controller & thrusters ready.")

try:
    while True:
        pygame.event.pump()

        # ---- Toggle kill switch ----
        toggle_pressed = con.get_button(BUTTON_OPTIONS)
        if toggle_pressed and not toggle_last_state:
            thrusters_enabled = not thrusters_enabled
            if not thrusters_enabled:
                print("[KILL SWITCH] Thrusters DISABLED")
                #for pin in thruster_pins:
                #    pi.set_servo_pulsewidth(pin, 1500)
            else:
                print("[KILL SWITCH] Thrusters ENABLED")
        toggle_last_state = toggle_pressed

        if not thrusters_enabled:
            time.sleep(0.02)
            continue

        # ---- Vertical control ----
        vertical_direction = "STOP"
        if con.get_button(BUTTON_TRIANGLE):
            value = map_values(1)
            vertical_direction = "UP"
        elif con.get_button(BUTTON_CROSS):
            value = map_values(-1)
            vertical_direction = "DOWN"
        else:
            value = 1500

        #pi.set_servo_pulsewidth(thruster_pins[0], value)
        #pi.set_servo_pulsewidth(thruster_pins[1], value)

        # ---- Horizontal control (joystick) ----
        forward = -con.get_axis(LEFT_JOYSTICK_Y)  # invert Y
        turn = con.get_axis(LEFT_JOYSTICK_X)

        if abs(forward) < DEADZONE:
            forward = 0
        if abs(turn) < DEADZONE:
            turn = 0

        if forward > 0 and turn == 0:
            horizontal_direction = "FORWARD"
        elif forward < 0 and turn == 0:
            horizontal_direction = "BACKWARD"
        elif turn > 0 and forward == 0:
            horizontal_direction = "RIGHT"
        elif turn < 0 and forward == 0:
            horizontal_direction = "LEFT"
        elif forward > 0 and turn > 0:
            horizontal_direction = "FORWARD-RIGHT"
        elif forward > 0 and turn < 0:
            horizontal_direction = "FORWARD-LEFT"
        elif forward < 0 and turn > 0:
            horizontal_direction = "BACKWARD-RIGHT"
        elif forward < 0 and turn < 0:
            horizontal_direction = "BACKWARD-LEFT"
        else:
            horizontal_direction = "STOP"

        left_thruster = max(min(forward + turn, 1), -1)
        right_thruster = max(min(forward - turn, 1), -1)

        pwm_left = map_values(left_thruster)
        pwm_right = map_values(right_thruster)

        #pi.set_servo_pulsewidth(thruster_pins[2], pwm_left)
        #pi.set_servo_pulsewidth(thruster_pins[3], pwm_right)

        print(f"[MOVEMENT] Vertical: {vertical_direction}, Horizontal: {horizontal_direction}")
        print(f"[THRUSTER PWM] Left: {pwm_left}, Right: {pwm_right}, Center: {value}")

        time.sleep(0.02)

except KeyboardInterrupt:
    print("Stopping...")

finally:
    for pin in thruster_pins:
        #pi.set_servo_pulsewidth(pin, 1500)
        print(f"[DEBUG] Reset thruster on pin: {pin}")
    #pi.stop()