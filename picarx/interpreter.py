from sensor import Sensor
import time
import numpy as np


class Interpreter(object):
    def __init__(self, sensitivity=0, polarity=1, ultrasonic_scale=2):
        self.sensitivity = sensitivity
        self.polarity = polarity

        self.ultrasonic_scale = ultrasonic_scale

        self.camera_output = None


    def detect_edge(self, grayscale_list):
        # Normalize incoming grayscale data
        gray_norm = [float(gray_val) / max(grayscale_list) for gray_val in grayscale_list]

        # Find the range of normalized values
        grayscale_diff = max(gray_norm) - min(gray_norm)

        # Test range relative to senor sensitivity
        if grayscale_diff > self.sensitivity:
            direction = gray_norm[0] - gray_norm[2]
            # print(direction)

            if self.polarity == 1:
                correction_scale = (max(gray_norm) - np.mean(gray_norm)) * (2/3)
            elif self.polarity == -1:
                correction_scale = (min(gray_norm) - np.mean(gray_norm)) * (2/3)

            correction = self.polarity * correction_scale * direction
        else:
            correction = 0
        
        return correction

    def image_processing(self):
        x1, y1, x2, y2 = self.camera_output

    def ultrasonic_stop(self, sens_dist):
        scale_factor = np.tanh(sens_dist/self.ultrasonic_scale)
        return scale_factor
    
    def interpreter_bus(self, grayscale_bus, interpret_bus, delay):
        while True:
            gray_list = grayscale_bus.read()

            # camera_output = camera_bus.read() # WHERE DO I WRITE THIS INFORMATION TO...? <<<<<<<<<<<<<----------------------

            correction_dir = self.detect_edge(gray_list)
            interpret_bus.write(correction_dir)
            # interpret_bus.write(camera_output)
            time.sleep(delay)


if __name__ == '__main__':
    sensor = Sensor()
    interpretor = Interpreter()

    while True:
        list = sensor.get_grayscale_data()
        # print(list)
        correction_dir = interpretor.detect_edge(list)
        print("{:.3f}".format(correction_dir))
        time.sleep(1)