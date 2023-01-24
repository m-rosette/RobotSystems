#!/usr/bin/env python3

import maneuvering as move
import time


if __name__ == "__main__":
    while 1:
        choice = int(input("Choose PiCar movement type: (1) Forward to Backward, (2) Parallel Parking, (3) K-turn, (4) Calibration: "))
        if choice == 1:
            print("Forward to Backward:")
            speed = int(input("Enter 'speed': "))
            steering_angle = int(input("Enter 'steering_angle': "))
            move.forward_to_backward(speed, steering_angle)
            print("Movement sequence completed")
        elif choice == 2:
            print("Parallel Parking:")
            speed = int(input("Enter 'speed': "))
            steering_angle = int(input("Enter 'steering_angle': "))
            move.parallel_park(speed, steering_angle)
            print("Movement sequence completed")
        elif choice == 3:
            print("K-turn - Three point turn:")
            speed = int(input("Enter 'speed': "))
            steering_angle = int(input("Enter 'steering_angle': "))
            move.k_turn(speed, steering_angle)
            print("Movement sequence completed")
        else:
            print("Calibration:")
            move.calibrate_steering(input("Enter steering angle calibration value: "))
            print("Calibration sequence completed")
