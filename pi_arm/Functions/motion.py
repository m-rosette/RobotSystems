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

    Board.setBusServoPulse(1, 10, 10)
    Board.setBusServoPulse(2, 500, 500)
    arm_kinematics.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
