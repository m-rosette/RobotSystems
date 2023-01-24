#!/usr/bin/env python3


import picarx_improved as picar
import time


if __name__ == '__main__':
    while 1:
        print(picar.Grayscale_Module.get_grayscale_data())
        print(picar.Grayscale_Module.get_line_status())
        time.sleep(0.1)

