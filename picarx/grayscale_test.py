#!/usr/bin/env python3


from picarx_improved import Picarx
import time


if __name__ == '__main__':
    while 1:
        sensor = Picarx()
        gray_data = sensor.Picarx.get_grayscale_data()
        print(gray_data)
        print(sensor.get_line_status(gray_data))
        time.sleep(0.1)

