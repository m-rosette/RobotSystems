from gray_sensor import GraySensor
import numpy as np


class Interpreter(object):
    def __init__(self, sensitivity=0, polarity=1):
        self.sensitivity = sensitivity
        self.polarity = polarity

    def __call__(self):
        gray_sens = GraySensor()
        return self.detect_edge(gray_sens)

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