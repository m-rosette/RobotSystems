#!/usr/bin/env python3

import time
import numpy as np
import picarx_improved as picar

def forward_to_backward(speed, steering_angle, action_time):
    movement = picar.Picarx()
    movement.set_motor_speed(speed)
    movement.set_wheel_vel_scale(steering_angle)
    movement.set_dir_servo_angle(steering_angle)

    end_time = time.time() + action_time

    while time.time() < end_time:
        movement.forward(speed)

    while time.time() < end_time:
        movement.backward(speed)
