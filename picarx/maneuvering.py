import time
import numpy as np
from picarx_improved import Picarx

# marcus@picar14.engr.oregonstate.edu

def forward_to_backward(speed, steering_angle, action_time):
    movement = Picarx()
    movement.set_motor_speed(1, speed)
    movement.set_motor_speed(2, speed)
    # movement.motor_direction_calibration()
    movement.set_wheel_vel_scale(steering_angle)
    movement.set_dir_servo_angle(steering_angle)

    end_time = time.time() + action_time

    while time.time() < end_time:
        movement.forward(speed)

    # while time.time() < end_time:
    #     movement.backward(speed)

    movement.stop()

if __name__ == "__main__":
    forward_to_backward(30, 0, 2)

