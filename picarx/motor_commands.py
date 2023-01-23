#!/usr/bin/env python3


import time
import os

import logging
from logdecorator import log_on_start , log_on_end , log_on_error

import atexit

try:
    from robot_hat import *
    from robot_hat import reset_mcu
    reset_mcu()
    time.sleep(0.01)
except ImportError :
    print (" This computer does not appear to be a PiCar - X system ( robot_hat is not present ) . Shadowing hardware calls with substitute functions ")
    from sim_robot_hat import *

# logging_format = "%(asctime)s: %(message)s"
# logging.basicConfig(format = logging_format, level = logging.INFO, datefmt ="%H:%M:%S")
# logging.getLogger().setLevel(logging.DEBUG)

# reset_mcu()
time.sleep(0.2)

# user and User home directory
User = os.popen('echo ${SUDO_USER:-$LOGNAME}').readline().strip()
UserHome = os.popen('getent passwd %s | cut -d: -f 6'%User).readline().strip()
# print(User)  # pi
# print(UserHome) # /home/pi
config_file = '%s/.config/picar-x/picar-x.conf'%UserHome


class Picarx:
    PERIOD = 4095
    PRESCALER = 10
    TIMEOUT = 0.02

    def __init__(self, 
                # servo_pins:list=['P0', 'P1', 'P2'], 
                # motor_pins:list=['D4', 'D5', 'P12', 'P13'],
                # grayscale_pins:list=['A0', 'A1', 'A2'],
                # ultrasonic_pins:list=['D2','D3'],
                # config:str=config_file,

                # cleanup:atexit.register(self.cleanup),
                motor_pins,
                cali_dir_value,
                config
                ):
        self.motor_pins = ['D4', 'D5', 'P12', 'P13']
        self.config = str(config_file)
        self.cali_dir_value = cali_dir_value

        # config_flie
        self.config_flie = fileDB(config, 774, User)

        # motors init
        self.left_rear_dir_pin = Pin(motor_pins[0])
        self.right_rear_dir_pin = Pin(motor_pins[1])
        self.left_rear_pwm_pin = PWM(motor_pins[2])
        self.right_rear_pwm_pin = PWM(motor_pins[3])
        self.motor_direction_pins = [self.left_rear_dir_pin, self.right_rear_dir_pin]
        self.motor_speed_pins = [self.left_rear_pwm_pin, self.right_rear_pwm_pin]

        cali_dir_value = self.config_flie.get("picarx_dir_motor", default_value="[1,1]")
        cali_dir_value = [int(i.strip()) for i in self.cali_dir_value.strip("[]").split(",")]
        
        self.cali_speed_value = [0, 0]
        self.dir_current_angle = 0
        for pin in self.motor_speed_pins:
            pin.period(self.PERIOD)


    @classmethod
    def set_motor_speed(cls, motor, speed):
        # global cali_speed_value,cali_dir_value
        motor -= 1
        if speed >= 0:
            direction = 1 * cali_dir_value[motor]
        elif speed < 0:
            direction = -1 * self.cali_dir_value[motor]
        speed = abs(speed)
        if speed != 0:
            speed = int(speed /2 ) + 50
        speed = speed - self.cali_speed_value[motor]
        if direction < 0:
            self.motor_direction_pins[motor].high()
            self.motor_speed_pins[motor].pulse_width_percent(speed)
        else:
            self.motor_direction_pins[motor].low()
            self.motor_speed_pins[motor].pulse_width_percent(speed)

    def motor_speed_calibration(cls, value):
        # global cali_speed_value,cali_dir_value
        self.cali_speed_value = value
        if value < 0:
            self.cali_speed_value[0] = 0
            self.cali_speed_value[1] = abs(self.cali_speed_value)
        else:
            self.cali_speed_value[0] = abs(self.cali_speed_value)
            self.cali_speed_value[1] = 0

    def motor_direction_calibration(cls, motor, value):
        # 1: positive direction
        # -1:negative direction
        motor -= 1
        # if value == 1:
        #     self.cali_dir_value[motor] = -1 * self.cali_dir_value[motor]
        # self.config_flie.set("picarx_dir_motor", self.cali_dir_value)
        if value == 1:
            self.cali_dir_value[motor] = 1
        elif value == -1:
            self.cali_dir_value[motor] = -1
        self.config_flie.set("picarx_dir_motor", self.cali_dir_value)

    def dir_servo_angle_calibration(cls, value):
        self.dir_cal_value = value
        self.config_flie.set("picarx_dir_servo", "%s"%value)
        self.dir_servo_pin.angle(value)

    def set_dir_servo_angle(self,value):
        self.dir_current_angle = value
        angle_value  = value + self.dir_cal_value
        self.dir_servo_pin.angle(angle_value)

    def set_wheel_vel_scale(cls, steering_angle):
        # PiCar measurements
        wheel_base = 11.6 # cm
        wheel_length = 9.5 # cm

        dist_center_rot = wheel_length * math.tan(((math.pi/2)-steering_angle)) + (wheel_base/2)
        wheel_vel_scaling = (dist_center_rot - (wheel_base/2)) / dist_center_rot
        return wheel_vel_scaling
        
    def backward(cls, speed):
        current_angle = self.dir_current_angle
        if current_angle != 0:
            abs_current_angle = abs(current_angle)
            # if abs_current_angle >= 0:
            if abs_current_angle > 40:
                abs_current_angle = 40
            # print("power_scale:",power_scale)
            if (current_angle / abs_current_angle) > 0:
                self.set_motor_speed(1, -1*speed * self.set_wheel_vel_scale(current_angle))
                self.set_motor_speed(2, speed)
            else:
                self.set_motor_speed(1, -1*speed)
                self.set_motor_speed(2, speed * self.set_wheel_vel_scale(current_angle))
        else:
            self.set_motor_speed(1, -1*speed)
            self.set_motor_speed(2, speed)  

    def forward(cls, speed):
        current_angle = self.dir_current_angle
        if current_angle != 0:
            abs_current_angle = abs(current_angle)
            # if abs_current_angle >= 0:
            if abs_current_angle > 40:
                abs_current_angle = 40

            # print("power_scale:",power_scale)
            if (current_angle / abs_current_angle) > 0:
                self.set_motor_speed(1, speed)
                self.set_motor_speed(2, -speed * self.set_wheel_vel_scale(current_angle)) 
                # print("current_speed: %s %s"%(1*speed * power_scale, -speed))
            else:
                self.set_motor_speed(1, speed * self.set_wheel_vel_scale(current_angle))
                self.set_motor_speed(2, -1*speed)
                # print("current_speed: %s %s"%(speed, -1*speed * power_scale))
        else:
            self.set_motor_speed(1, speed)
            self.set_motor_speed(2, -1*speed)                  

    def stop(cls):
        self.set_motor_speed(1, 0)
        self.set_motor_speed(2, 0)


if __name__ == "__main__":
    px = Picarx()
    px.forward(50)
    time.sleep(1)
    px.stop()