from sensor import GrayscaleSensor
import time
import numpy as np


class Interpreter(object):
    def __init__(self, sensitivity=0, polarity=1):
        self.sensitivity = sensitivity
        self.polarity = polarity


    def detect_edge(self, grayscale_list):
        # Normalize incoming grayscale data
        gray_norm = [float(gray_val) / max(grayscale_list) for gray_val in grayscale_list]

        # Find the range of normalized values
        grayscale_diff = max(gray_norm) - min(gray_norm)

        # Test range relative to senor sensitivity
        if grayscale_diff > self.sensitivity:
            direction = gray_norm[0] - gray_norm[2]
            print(direction)

            if self.polarity == 1:
                correction_scale = (max(gray_norm) - np.mean(gray_norm)) * (2/3)
            elif self.polarity == -1:
                correction_scale = (min(gray_norm) - np.mean(gray_norm)) * (2/3)

            correction = self.polarity * correction_scale * direction
        else:
            correction = 0
        
        return correction

    
    def interpreter_bus(self, sensor_bus, interpret_bus, delay):
        while True:
            gray_list = sensor_bus.read()
            correction_dir = self.detect_edge(gray_list)
            interpret_bus.write(correction_dir)
            time.sleep(delay)


if __name__ == '__main__':
    sensor = GrayscaleSensor()
    interpretor = Interpreter(0.0, -1)

    while True:
        list = sensor.get_grayscale_data()
        print(list)
        rel_dir = interpretor.edge_detect(list)
        print("{:.3f}".format(rel_dir))
        time.sleep(1)