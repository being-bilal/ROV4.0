import pigpio
import pygame

pygame.init()
pygame.joystick.init()

con_count = pygame.joystick.get_count()
if con_count > 0:
	con = pygame.joystick.init(0)
	con.init()
	print(f"Controller Connected : {con}")
else:
	print("No controller connected!")


running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			print("Exiting...")
			running = False

		if event.type == pygame.JOYAXISMOTION:
			print(f"Axis : {event.axis} | value : {event.value}")


pygame.quit()