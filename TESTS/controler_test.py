import pigpio
import pygame
import time

pygame.init()
pygame.joystick.init()

con = pygame.joystick.Joystick(0)
con.init()

BUTTON_A = 0
BUTTON_Y = 3
LEFT_JOYSTICK_Y = 1
LEFT_JOYSTICK_X = 0
BUTTON_TOGGLE = 9  # Kill switch button

# Thruster pins
thruster_1 = 0  # Center thruster 1
thruster_2 = 0  # Center Thruster 2
thruster_3 = 0  # Left Thruster
thruster_4 = 0  # Right Thruster
thruster_pins = [thruster_1, thruster_2, thruster_3, thruster_4]

'''
pi = pigpio.pi()
for pin in thruster_pins:
    pi.set_servo_pulsewidth(pin, 1500)  # Arming the Thrusters
'''

def map_values(value):
    """Maps joystick value (-1 to 1) to PWM."""
    if value < -1 or value > 1:
        return None
    elif value == 0:
        return 1500
    else:
        return int(1500 + (value * 300))

# Adjustable deadzone
DEADZONE = 0.2

# Kill switch state
thrusters_enabled = True
toggle_last_state = False

print("Controller & thrusters ready.")

try:
    while True:
        pygame.event.pump()

        # --- Toggle logic ---
        toggle_pressed = con.get_button(BUTTON_TOGGLE)
        if toggle_pressed and not toggle_last_state:  # Button just pressed
            thrusters_enabled = not thrusters_enabled
            if not thrusters_enabled:
                print("[KILL SWITCH] Thrusters DISABLED")
                #pi.set_servo_pulsewidth(thruster_pins[0], 1500)
                #pi.set_servo_pulsewidth(thruster_pins[1], 1500)
                #pi.set_servo_pulsewidth(thruster_pins[2], 1500)
                #pi.set_servo_pulsewidth(thruster_pins[3], 1500)
            else:
                print("[KILL SWITCH] Thrusters ENABLED")
        toggle_last_state = toggle_pressed

        # If thrusters disabled, skip input processing
        if not thrusters_enabled:
            time.sleep(0.02)
            continue

        # --- Debug buttons ---
        for i in range(con.get_numbuttons()):
            if con.get_button(i):
                print(f"[DEBUG] Button {i} pressed")

        # --- Vertical Movement ---
        vertical_direction = "STOP"
        if con.get_button(BUTTON_Y):
            value = map_values(1)
            vertical_direction = "UP"
        elif con.get_button(BUTTON_A):
            value = map_values(-1)
            vertical_direction = "DOWN"
        else:
            value = 1500

        #pi.set_servo_pulsewidth(thruster_pins[0], value)
        #pi.set_servo_pulsewidth(thruster_pins[1], value)

        # --- Horizontal Movement ---
        forward = -con.get_axis(LEFT_JOYSTICK_Y)  # left stick Y-axis
        turn = con.get_axis(LEFT_JOYSTICK_X)      # left stick X-axis

        # Apply deadzone
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
        print(f"[THRUSTER PWM VALUES] Left: {pwm_left}, Right: {pwm_right}, Center: {value}")

        time.sleep(0.02)

except KeyboardInterrupt:
    print("Stopping...")

finally:
    for pin in thruster_pins:
        #pi.set_servo_pulsewidth(pin, 1500)
        print(f"[DEBUG] Reset thruster on pin: {pin}")
    #pi.stop()
