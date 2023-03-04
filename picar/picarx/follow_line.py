from controller import Controller
from sensor import Sensor
from interpreter import Interpreter
import time
from picarx_improved import Picarx


def follow_line(sensor, interpreter, controller):
    while True:
        gray_data = sensor.get_grayscale_data()
        edge_detect = interpreter.detect_edge(gray_data)
        controller.line_follow(edge_detect)
        time.sleep(0.1)


if __name__ == '__main__':
    px = Picarx()
    input_scale = float(input("Enter scaling factor: "))
    input_polarity = float(input("Enter polarity: "))
    sensor = Sensor()
    controller = Controller(px, input_scale)
    interpreter = Interpreter(0.0, input_polarity)
    
    follow_line(sensor, interpreter, controller)
