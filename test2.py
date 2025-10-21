import pygame
from pyxboxcontroller import XboxController
from vector import joy_to_pwm


# --- Initialize pygame window ---
pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Xbox Controller PWM Display")

font = pygame.font.SysFont(None, 40)
clock = pygame.time.Clock()

# --- Initialize Xbox Controller ---
controller = XboxController(0)
# controller.start()  
# print("controller.values keys:", list(controller.values.keys()))

# Main loop
running = True
while running:
    # Handle quit event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read joystick values

    # These are attributes in v0.7.3
    state = controller.state
    left_x = state.l_thumb_x
    left_y = state.l_thumb_y
    right_x = state.r_thumb_x
    right_y = state.r_thumb_y


    # Convert to PWM
    array = joy_to_pwm(left_x, left_y, right_x)
    array = [round(x) for x in array]

    # Clear screen
    screen.fill((20, 20, 30))

    # Display the values
    labels = [
        f"{array}",
    ]

    for i, text in enumerate(labels):
        img = font.render(text, True, (255, 255, 255))
        screen.blit(img, (40, 60 + i * 60))

    pygame.display.flip()
    clock.tick(30)  # Limit to 30 FPS

pygame.quit()