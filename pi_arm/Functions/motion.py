#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import Camera
import threading
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *


# class Motion():
#     def __init__(self, AK):
#         self.AK = AK
    
#     def move()


if __name__ == '__main__':
    arm_kinematics = ArmIK()

    # for i 
    # coordinates = (x, y, z)

    # Board.setBusServoPulse(id, pulse, movetime)
        # driver serial servo rotation to designation position
        # :param id: need to driver servo id
        # :pulse: position
        # :use_time: time required for rotation

    servo1 = 50 # Gripper: 0-full open, 500-close
    servo2 = 50 # Wrist: 500-horizontal, 
    servo3 = 50
    Board.setBusServoPulse(1, 20, 100)
    Board.setBusServoPulse(2, 20, 100)
    Board.setBusServoPulse(3, 250, 100)
    # arm_kinematics.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
