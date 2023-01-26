#!/usr/bin/env python3

from picarx_improved import Picarx
from time import sleep
import atexit

px = Picarx()
px.set_grayscale_reference(1000)  
last_state = None
current_state = None
px_power = 10
offset = 20

def line_follower(reference):
    gm_val_list = px.get_grayscale_data()
    gm_state = px.get_line_status(gm_val_list)
    # print("gm_val_list: %s, %s"%(gm_val_list, gm_state))

    if gm_val_list[0] > reference and gm_val_list[1] > reference and gm_val_list[2] > reference:
        px.set_dir_servo_angle(0)
        px.stop()

    if gm_val_list[0] <= reference:
        px.set_dir_servo_angle(-offset)
        px.forward(px_power) 

    elif gm_val_list[2] <= reference:
        px.set_dir_servo_angle(offset)
        px.forward(px_power) 

    elif gm_val_list[1] <= reference:
        px.set_dir_servo_angle(0)
        px.forward(px_power) 



if __name__=='__main__':
    try:
        while True:
            reference = float(input("Enter grey scale reference value: "))
            px.set_grayscale_reference(reference)
            line_follower(reference)
    finally:
        px.stop()
        atexit.register(px.stop())