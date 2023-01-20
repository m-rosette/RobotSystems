import time
import numpy as np
from picarx import Picarx

# marcus@picar14.engr.oregonstate.edu

def forward_to_backward(speed, steering_angle, action_time):
    movement = Picarx()
    movement.set_motor_speed(speed=speed)
    movement.set_wheel_vel_scale(steering_angle)
    movement.set_dir_servo_angle(steering_angle)

    end_time = time.time() + action_time

    while time.time() < end_time:
        movement.forward(speed)

    while time.time() < end_time:
        movement.backward(speed)


if __name__ == "__main__":
    try:
        forward_to_backward(30, 0, 2)
        time.sleep(0.5)

    finally:
        # px.forward(0)
        Picarx.stop()
        time.sleep(.2)