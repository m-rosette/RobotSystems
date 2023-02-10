from gray_sensor import GraySensor
from gray_interpreter import Interpreter
from picarx_improved import Picarx
import time



class Controller(object):
    def __init__(self, picar, scale=80):
        self.picar = picar
        self.scale = scale
    
    def __call__(self):
        interp = Interpreter()
        return self.line_follow(interp)
    
    def line_follow(self, direction):
        self.steering_angle = direction * self.scale
        self.picar.set_dir_servo_angle(self.steering_angle)
        # self.picar.forward(20)
        return self.steering_angle