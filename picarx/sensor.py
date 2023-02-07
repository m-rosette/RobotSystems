import sys
sys.path.append(r'/home/marcus/RobotSystems/robot-hat/robot_hat')
from robot_hat import ADC
import picarx_improved as px
from picarx_improved import Grayscale_Module
import time


class GrayscaleSensor(object):
    def __init__(self):
        self.chn_0 = ADC("A0")
        self.chn_1 = ADC("A1")
        self.chn_2 = ADC("A2")

    def get_grayscale_data(self):
        adc_value_list = []
        adc_value_list.append(self.chn_0.read())
        adc_value_list.append(self.chn_1.read())
        adc_value_list.append(self.chn_2.read())
        return adc_value_list

    def sensor_bus(self, bus, delay):
        while True:
            gray_list = self.get_grayscale_data()
            bus.write(gray_list)
            time.sleep(delay)