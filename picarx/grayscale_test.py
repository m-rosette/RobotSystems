#!/usr/bin/env python3


import picarx_improved as px
import time


if __name__ == '__main__':
    while 1:
        sensor = px()
        gray_data = px.Grayscale_Module.get_grayscale_data()
        print(gray_data)
        print(px.Grayscale_Module.get_line_status(gray_data))
        time.sleep(0.1)

