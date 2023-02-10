import sys
sys.path.append(r'/home/marcus/RobotSystems/robot-hat/robot_hat')
from robot_hat import ADC
import picarx_improved as px
import logging
from logdecorator import log_on_start , log_on_end , log_on_error


logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO, datefmt ="%H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)


class GraySensor(object):
    def __init__(self):
        # Grayscale
        self.chn_0 = ADC("A0")
        self.chn_1 = ADC("A1")
        self.chn_2 = ADC("A2")

    def __call__(self):
        return self.get_grayscale_data()

    def get_grayscale_data(self):
        adc_value_list = []
        adc_value_list.append(self.chn_0.read())
        adc_value_list.append(self.chn_1.read())
        adc_value_list.append(self.chn_2.read())
        return adc_value_list