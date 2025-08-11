import pigpio
import pygame 

pygame.init()
pygame.joystick.init()

con = pygame.joystick.Joystick(0)
con.init()

thruster_1 = 0
thruster_2 = 0
thruster_3 = 0
thruster_4 = 0

thruster_pins = [thruster_1,thruster_2,thruster_3,thruster_4]

pi = pigpio.pi()
for i in thruster_pins:
    pi.set_servo_pulsewidth(item,1500) # Arming the Thrusters


def map_values(value):
    if value < -1 or value > 1:
        return None 
    elif value == 0:
        return 1500
    else: 
        return int(1500 + (value * 300))


print("Controller & thrusters ready.")

try: 
    while True: 
        # UP and DOWN Movement 
        if con.get_button(BUTTON_Y):
            value = map_values(1)
        elif con.get_button(BUTTON_A): 
            value = map_values(-1)
        else:
            value = 1500

        pi.set_servo_pulsewidth(thruster_pins[0], pwm_val)
        pi.set_servo_pulsewidth(thruster_pins[1], pwm_val)


        # X-Y Movement 
        forward = -con.get_axis(4)  
        turn = con.get_axis(3)      

        if abs(forward) < 0.1: forward = 0
        if abs(turn) < 0.1: turn = 0

        
        left_thruster = forward + turn
        right_thruster = forward - turn

        left_thruster = max(min(left_thruster, 1), -1)
        right_thruster = max(min(right_thruster, 1), -1)

        pi.set_servo_pulsewidth(thruster_pins[2], map_values(left_thruster))
        pi.set_servo_pulsewidth(thruster_pins[3], map_values(right_thruster))

        time.sleep(0.02) 

except KeyboardInterrupt:
    print("Stopping...")

finally:
    for pin in thruster_pins:
        pi.set_servo_pulsewidth(pin, 1500)
    pi.stop()



