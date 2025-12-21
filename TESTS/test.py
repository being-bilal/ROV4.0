import pigpio
import numpy as np
import pygame
import time

class Controller(object):
    STICK_DEADBAND = .06

    def __init__(self, axis_map):
        self.joystick = None
        self.axis_map = axis_map  #different controllers have different key maps

    def update(self):
        pygame.event.pump()

    def getSway(self): # forward/backward movement (Y axis)
        return self._getAxis(0)

    def getSurge(self):
        return self._getAxis(1) # left/right movement (X axis)

    def getYaw(self):
        return self._getAxis(3) # rotation (Z axis)

    def _getAxis(self, k): #passed the key maps of the controller
        j = self.axis_map[k] # extract the value of the key from the tuple passed
        val = self.joystick.get_axis(abs(j)) 
        if abs(val) < Controller.STICK_DEADBAND:
            val = 0
        return (-1 if j < 0 else +1) * val

#___________________________________GameController______________________________
    
class _GameController(Controller):
    def __init__(self, axis_map, button_id):
        super().__init__(axis_map)
        self.button_id = button_id
        self.aux_state = 'OFF'       # Current toggle state
        self.prev_button = 0         # Previous button state

    def _getAuxValue(self):
        current_button = self.joystick.get_button(self.button_id)

        # Toggle logic: flip state only on button press
        if current_button == 1 and self.prev_button == 0:
            self.aux_state = 'ON' if self.aux_state == 'OFF' else 'OFF'

        self.prev_button = current_button
        return self.aux_state

    def getAux(self):
        return self._getAuxValue()
    
controllers = {
    'PS4 Controller': 
        _GameController((-1, 0, -3, 2), 6),

    'PowerA Spectra Infinity Controller':
        _GameController((-2, 3, -4, 0), 5),
}

def ControllerSetup():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No joystick detected.")
        exit()

    js = pygame.joystick.Joystick(0)
    js.init()
    name = js.get_name()
    print(f"Connected controller: {name}")

    if name in controllers:
        con = controllers[name]
        con.joystick = js
    else:
        print("Unsupported controller.")
        exit()

    print("Reading controller inputs... ")
    return con


    
def main():
    con = ControllerSetup()
    try:
    
        while True:
            con.update()
            sway = con.getSway()
            surge = con.getSurge()
            yaw = con.getYaw()
            aux = con.getAux()

            print(f"Y: {sway:.2f}  X: {surge:.2f}  Yaw: {yaw:.2f}  KillSwitch: {aux}")
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nExiting...")
        pygame.quit()
        
if __name__ == "__main__":
    main()