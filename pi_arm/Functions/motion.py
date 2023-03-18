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


if __name__ == '__main__':
    # Board.setBusServoPulse(id, pulse, movetime)
        # driver serial servo rotation to designation position
        # :param id: need to driver servo id
        # :pulse: position
        # :use_time: time required for rotation

    time_response = 250
    servo1 = 500 # Gripper: 0-full open, 500-close
    servo2 = 50 # Wrist: 500-horizontal, 
    servo3 = 250 # 500: straight out
    servo4 = 250 # 500: straight out
    servo5 = 250 # 500: straight up
    servo6 = 100 # Base: 500-centered
    Board.setBusServoPulse(1, servo1, time_response)
    Board.setBusServoPulse(2, servo2, time_response)
    Board.setBusServoPulse(3, servo3, time_response)
    Board.setBusServoPulse(4, servo4, time_response)
    Board.setBusServoPulse(5, servo5, 100)
    Board.setBusServoPulse(6, servo6, 100)


