from sensor import Sensor
from interpreter import Interpreter
from picarx_improved import Picarx
import time
import numpy as np


class Controller(object):
    def __init__(self, picar, scale=80):
        self.picar = picar
        self.scale = scale
    
    def line_follow(self, direction):
        self.steering_angle = direction * self.scale
        self.picar.set_dir_servo_angle(self.steering_angle)
        self.picar.forward(20)
        return self.steering_angle
    
    def controller_bus(self, bus, delay):
        while True:
            correction_dir = bus.read()
            self.line_follow(correction_dir)
            time.sleep(delay)


if __name__ == '__main__':
    picar = Picarx()
    controller = Controller(picar)
    sensor = Sensor()
    interpreter = Interpreter(0.0, 1)

    while True:
        sensor_data = sensor.get_grayscale_data()
        correction_direction = interpreter.detect_edge(sensor_data)
        angle = controller.line_follow(correction_direction)
        time.sleep(0.5)