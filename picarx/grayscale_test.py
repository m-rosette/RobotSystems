#!/usr/bin/env python3


from picarx_improved import Picarx
import time
import numpy as np


if __name__ == '__main__':
    while 1:
        sensor = Picarx()
        gray_data = sensor.get_grayscale_data()
        np_array = np.array(gray_data)
        normalized = np.linalg.norm(np_array)
        print(round(np_array / normalized, 3))
        # print(sensor.get_line_status(gray_data))
        time.sleep(0.5)

