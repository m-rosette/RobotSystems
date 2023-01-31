from sensor import GrayscaleSensor
from interpreter import Interpreter
from picarx_improved import Picarx
import time
import numpy as np


class Controller(object):
    def __init__(self, picar, scale=1):
        self.picar = picar
        self.scale = scale
    
    def line_follow(self, direction):
        self.steering_angle = direction * self.scale
        self.picar.set_dir_servo_angle(self.steering_angle)

        return self.steering_angle
    
    def controller_com(self, communication, delay):
        while True:
            rel_dir = communication.read()
            self.line_follow(rel_dir)
            time.sleep(delay)


if __name__ == '__main__':
    picar = Picarx()
    sensor = GrayscaleSensor()
    controller = Controller(picar, 50)
    interpreter = Interpreter(0.0, 1)

    while True:
        sensor_data = sensor.get_grayscale_data()
        interp_direction = interpreter.detect_edge(sensor_data)
        angle = controller.line_follow(interp_direction)
        time.sleep(0.5)