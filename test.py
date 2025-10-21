scale_factor = 200
base_pwm = 0

def joy_to_pwm(joy_x, joy_y, joy_theta):
    vm = vertical_motion(joy_y)       # returns list of 4 values
    hm = horizontal_motion(joy_x)     # returns list of 4 values
    y  = yaw(joy_theta)               # returns list of 4 values

    arr = [base_pwm] * 4
    threshold = 30

    for i in range(4):
        components = []
        
        if abs(vm[i]) > threshold:
            components.append(vm[i])
        if abs(hm[i]) > threshold:
            components.append(hm[i])
        if abs(y[i]) > threshold:
            components.append(y[i])
        
        if components:
            arr[i] += sum(components) / len(components)
    
    return arr




def vertical_motion(y): ## -1<y<1
    if (y > 1 or y < -1):
        raise ValueError("y must be bw -1 to 1")
    
    ret = [y*scale_factor, y*scale_factor, -y*scale_factor, -y*scale_factor]

    return ret


def horizontal_motion(x): ## -1<y<1
    if (x > 1 or x < -1):
        raise ValueError("y must be bw -1 to 1")
    
    ret = [x*scale_factor, -x*scale_factor, x*scale_factor, -x*scale_factor]


    return ret

def yaw(theta):
    if (theta > 1 or theta < -1):
        raise ValueError("angle Must be bw -1 and 1")

    ret = [theta*scale_factor, -theta*scale_factor, -theta*scale_factor, theta*scale_factor]
    return ret