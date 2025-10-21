import pygame
import numpy as np
import math

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLUE = (0, 170, 255)
RED = (255, 50, 50)
GREEN = (0, 200, 100)

ROV_WIDTH, ROV_HEIGHT = 150, 150
VECTOR_SCALE = 100  # How long the vector lines are at full thrust

# --- Thruster Calculation Logic (with correction) ---
def compute_thruster_forces(x_input, y_input, yaw_input, L=1.0):
    """
    Computes the thrust for each of 4 diagonal-facing thrusters of a square ROV.
    :param x_input: Desired surge (-1 to 1)
    :param y_input: Desired sway (-1 to 1)
    :param yaw_input: Desired yaw rate (-1 to 1)
    :param L: Side length of the square
    :return: Array of thruster forces [T1, T2, T3, T4]
    """
    # Thruster positions (x, y)
    positions = np.array([
        [-L/2,  L/2],  # T1 (Front-Left)
        [ L/2,  L/2],  # T2 (Front-Right)
        [-L/2, -L/2],  # T3 (Rear-Left)
        [ L/2, -L/2],  # T4 (Rear-Right)
    ])

    # Thrusters face diagonally (45°, 135°, -45°, -135°)
    angles = np.deg2rad([45, 135, -45, -135])

    # Build the allocation matrix B
    B = np.zeros((3, 4))
    for i, ((x, y), theta) in enumerate(zip(positions, angles)):
        B[0, i] = np.cos(theta)                  # contribution to Fx (Surge)
        B[1, i] = np.sin(theta)                  # contribution to Fy (Sway)
        B[2, i] = x * np.sin(theta) - y * np.cos(theta) # contribution to torque (Yaw)

    # Desired movement vector [Fx, Fy, Tau]
    v = np.array([x_input, y_input, yaw_input])

    # Compute least-squares solution using the pseudoinverse of B
    thruster_forces = np.linalg.pinv(B) @ v

    # Normalize forces so the max absolute value is 1 (if it exceeds 1)
    max_force = np.max(np.abs(thruster_forces))
    if max_force > 1:
        thruster_forces /= max_force

    return thruster_forces

# --- Drawing Functions ---
def draw_rov(screen, center_pos):
    """Draws the ROV body as a simple rectangle."""
    rov_rect = pygame.Rect(0, 0, ROV_WIDTH, ROV_HEIGHT)
    rov_rect.center = center_pos
    pygame.draw.rect(screen, GRAY, rov_rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, rov_rect, width=3, border_radius=10)
    
    # Draw an arrow indicating the front
    front_indicator_start = (center_pos[0], center_pos[1] - ROV_HEIGHT // 4)
    front_indicator_end = (center_pos[0], center_pos[1] - ROV_HEIGHT // 2)
    pygame.draw.line(screen, WHITE, front_indicator_start, front_indicator_end, 5)

def draw_thruster_vectors(screen, font, center_pos, forces):
    """Draws the thruster vectors and their values."""
    thruster_positions = [
        (center_pos[0] - ROV_WIDTH/2, center_pos[1] - ROV_HEIGHT/2), # T1 FL
        (center_pos[0] + ROV_WIDTH/2, center_pos[1] - ROV_HEIGHT/2), # T2 FR
        (center_pos[0] - ROV_WIDTH/2, center_pos[1] + ROV_HEIGHT/2), # T3 RL
        (center_pos[0] + ROV_WIDTH/2, center_pos[1] + ROV_HEIGHT/2)  # T4 RR
    ]
    angles_deg = [135, 45, -135, -45] # Drawing angles (0 is right)
    
    for i, (pos, angle_deg, force) in enumerate(zip(thruster_positions, angles_deg, forces)):
        angle_rad = math.radians(angle_deg)
        
        # Vector color depends on direction (positive/negative thrust)
        color = RED if force > 0 else BLUE
        
        # Calculate start and end points of the vector line
        start_x, start_y = pos
        end_x = start_x + (VECTOR_SCALE * force * math.cos(angle_rad))
        end_y = start_y - (VECTOR_SCALE * force * math.sin(angle_rad)) # Pygame Y is inverted
        
        if abs(force) > 0.05: # Only draw if thrust is significant
            pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), 5)
            # Draw arrowhead
            arrow_angle = math.atan2(start_y - end_y, end_x - start_x)
            p1 = (end_x - 10 * math.cos(arrow_angle - math.pi/6), end_y + 10 * math.sin(arrow_angle - math.pi/6))
            p2 = (end_x - 10 * math.cos(arrow_angle + math.pi/6), end_y + 10 * math.sin(arrow_angle + math.pi/6))
            pygame.draw.polygon(screen, color, [(end_x, end_y), p1, p2])

        # Draw text value
        text_surface = font.render(f"T{i+1}: {force:.2f}", True, WHITE)
        text_rect = text_surface.get_rect(center=(pos[0] + 40 * math.cos(angle_rad), pos[1] - 40 * math.sin(angle_rad)))
        screen.blit(text_surface, text_rect)

def draw_hud(screen, font, inputs):
    """Draws the Heads-Up Display for joystick inputs."""
    surge, sway, yaw = inputs
    lines = [
        f"Surge (Forward): {surge:.2f}",
        f"Sway (Right):    {sway:.2f}",
        f"Yaw (Turn):      {yaw:.2f}"
    ]
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, GREEN)
        screen.blit(text_surface, (10, 10 + i * 30))

# --- Main Simulation Function ---
def main():
    pygame.init()
    pygame.joystick.init()

    # --- Joystick Detection ---
    if pygame.joystick.get_count() == 0:
        print("Error: No joysticks detected.")
        pygame.quit()
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Joystick Detected: {joystick.get_name()}")

    # --- Screen and Clock Setup ---
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("ROV Thruster Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)
    
    # --- Main Loop ---
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.JOYBUTTONDOWN:
                print(f"Button {event.button} pressed.")

        # --- Get Joystick Input with Deadzone ---
        # Axis 1: Left stick vertical (forward/backward)
        # Axis 0: Left stick horizontal (strafe left/right)
        # Axis 2: Right stick horizontal (turn left/right)
        # Note: These may vary depending on your controller!
        
        # Surge (Forward/Backward) - Axis 1 is often inverted
        surge_input = -joystick.get_axis(1) 
        if abs(surge_input) < 0.1: surge_input = 0.0

        # Sway (Left/Right)
        sway_input = joystick.get_axis(0)
        if abs(sway_input) < 0.1: sway_input = 0.0
        
        # Yaw (Turning)
        yaw_input = joystick.get_axis(2)
        if abs(yaw_input) < 0.1: yaw_input = 0.0

        # --- Calculation ---
        thruster_forces = compute_thruster_forces(surge_input, sway_input, 0)
        
        # --- Printing to Console (as in original script) ---
        print(f"T1:{thruster_forces[0]:>6.2f} | T2:{thruster_forces[1]:>6.2f} | "
              f"T3:{thruster_forces[2]:>6.2f} | T4:{thruster_forces[3]:>6.2f}", end='\r')

        # --- Drawing ---
        screen.fill(BLACK)
        rov_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        draw_rov(screen, rov_center)
        draw_thruster_vectors(screen, font, rov_center, thruster_forces)
        draw_hud(screen, font, (surge_input, sway_input, yaw_input))
        
        pygame.display.flip()

        # Limit frame rate
        clock.tick(60)

    # --- Shutdown ---
    pygame.quit()
    print("\nSimulation exited.")

if __name__ == "__main__":
    main()