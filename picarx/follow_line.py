from controller import Controller
from sensor import GrayscaleSensor
from interpreter import Interpreter
import time
from picarx_improved import Picarx


if __name__ == '__main__':
    px = Picarx()
    input_scale = float(input("Enter scaling factor: "))
    input_polarity = float(input("Enter polarity: "))
    sensor = GrayscaleSensor()
    controller = Controller(px, input_scale)
    interpreter = Interpreter(0.0, input_polarity)

    while True:
        gray_data = sensor.get_grayscale_data()
        edge_detect = interpreter.detect_edge(gray_data)
        angle_correction = controller.line_follow(edge_detect)

        time.sleep(0.1)

