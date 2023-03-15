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

    # Board.setBusServoPulse(id, pulse, movetime)
        # driver serial servo rotation to designation position
        # :param id: need to driver servo id
        # :pulse: position
        # :use_time: time required for rotation

    servo1 = 250 # Gripper: 0-full open, 500-close
    servo2 = 500 # Wrist: 500-horizontal, 
    servo3 = 500 # 500: straight out
    servo4 = 500
    servo5 = 500
    servo6 = 500
    Board.setBusServoPulse(1, servo1, 100)
    Board.setBusServoPulse(2, servo2, 100)
    Board.setBusServoPulse(3, servo3, 100)
    Board.setBusServoPulse(4, servo4, 100)
    Board.setBusServoPulse(5, servo5, 100)
    Board.setBusServoPulse(6, servo6, 100)


