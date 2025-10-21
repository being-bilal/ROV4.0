import pygame
import numpy as np
import math
import time

# --- Constants ---
DEADZONE = 0.1  # Axis deadzone
PWM_MIN = 1100
PWM_MAX = 1900

# --- Thruster Calculation ---
def compute_thruster_forces(surge, sway, yaw, L=1.0):
    """
    Computes thrusts for 4 diagonal thrusters on a square ROV.
    surge: forward/backward [-1,1]
    sway: left/right [-1,1]
    yaw: rotation [-1,1]
    """
    positions = np.array([
        [-L/2,  L/2],  # T1 FL
        [ L/2,  L/2],  # T2 FR
        [-L/2, -L/2],  # T3 RL
        [ L/2, -L/2],  # T4 RR
    ])
    angles = np.deg2rad([45, 135, -45, -135])
    
    B = np.zeros((3,4))
    for i, ((x, y), theta) in enumerate(zip(positions, angles)):
        B[0,i] = np.cos(theta)                  # Fx
        B[1,i] = np.sin(theta)                  # Fy
        B[2,i] = x * np.sin(theta) - y * np.cos(theta) # Torque

    v = np.array([surge, sway, yaw])
    thrusters = np.linalg.pinv(B) @ v

    max_force = np.max(np.abs(thrusters))
    if max_force > 1:
        thrusters /= max_force

    return thrusters

def thrust_to_pwm(thrust):
    """Map thrust [-1,1] to PWM [1100,1900]"""
    return int(PWM_MIN + (thrust + 1)/2 * (PWM_MAX - PWM_MIN))

# --- Main Loop ---
def main():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No joystick detected.")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Joystick detected: {joystick.get_name()}")

    try:
        while True:
            # Process events to keep joystick responsive
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    print(f"Button {event.button} pressed")
                elif event.type == pygame.JOYBUTTONUP:
                    print(f"Button {event.button} released")

            # --- Read axes (PS4 mapping) ---
            surge = -joystick.get_axis(1)  # Left stick vertical: forward/backward
            sway  = joystick.get_axis(0)   # Left stick horizontal: left/right
            yaw   = joystick.get_axis(2)   # Right stick horizontal: rotation

            # Apply deadzone
            if abs(surge) < DEADZONE: surge = 0.0
            if abs(sway)  < DEADZONE: sway  = 0.0
            if abs(yaw)   < DEADZONE: yaw   = 0.0

            # Compute thruster forces and PWM
            thrusters = compute_thruster_forces(surge, sway, yaw)
            pwm_values = [thrust_to_pwm(f) for f in thrusters]

            # Compute movement angle relative to X-axis (forward = 0°)
            # Compute movement angle relative to X-axis (right = 0°)
            if surge == 0 and sway == 0:
                angle_deg = 0.0
            else:
                angle_deg = math.degrees(math.atan2(surge, sway)) % 360

            # Print outputs
            print(f"Thrusters PWM: {pwm_values} | ROV angle: {angle_deg:.2f}°", end='\r')

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nExiting...")
        pygame.quit()

if __name__ == "__main__":
    main()