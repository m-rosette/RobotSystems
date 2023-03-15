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


class Perception():
    def __init__(self, AK, target_color=('red',)):
        self.AK = AK
        self.__target_color = target_color

        self.frame_size = (640, 480)
        self.roi = ()
        self.get_roi = False
        self.start_pick_up = False

        self.range_rgb = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
        }
    
    def set_rgb(self, color):
        """
        Set the RGB light color of the expansion board to match the color to be tracked
        """
        if color == "red":
            Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
            Board.RGB.show()
        elif color == "green":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
            Board.RGB.show()
        elif color == "blue":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
            Board.RGB.show()
        else:
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
            Board.RGB.show()

    def getAreaMaxContour(self, contours):
        """
        Find the maximum area contour. Comparing a list of contours
        return: max area contour 
        """
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None

        for c in contours:  # traversal all the contours 
            contour_area_temp = math.fabs(cv2.contourArea(c))  # calculate the countour area
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 300:  # only when the area is greater than 300, the contour of the maximum area is effective to filter interference
                    area_max_contour = c

        return area_max_contour, contour_area_max  # return the maximum area countour

    def outline_object(self, frame_lab):
            if self.__target_color in color_range:
                target_range = color_range[self.__target_color]
                frame_mask = cv2.inRange(frame_lab, tuple(target_range['min']), tuple(target_range['max']))  # mathematical operation on the original image and mask
                opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # Opening (morphology)
                closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # Closing (morphology)
                contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # find countour
                area_max_contour, area_max = self.getAreaMaxContour(contours)  # find the maximum countour
            else:    
                area_max_contour = 0
                area_max = 0

            return area_max_contour, area_max
    
    def draw_crosshairs(self, img, img_h, img_w):
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)

    def process_frame(self, img):
        # Verify image size matches that of camera
        frame_resize = cv2.resize(img, self.size, interpolation=cv2.INTER_NEAREST)

        # Apply a blur to the image
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)

        # If it is detected with an area recognized object, the area will be detected until there is no object
        if self.get_roi and self.start_pick_up:
            self.get_roi = False
            frame_gb = getMaskROI(frame_gb, self.roi, self.frame_size)    
        
        # Convert the image to LAB space
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  
        return frame_lab
    

class Motion():
    def __init__(self, AK, perception, is_running) -> None:
        self.AK = AK
        self.perception = perception
        self.is_running = is_running

        self.start_move = True

        # Colors block placement coordinates (x, y, z)
        self.coordinate = {
            'red':   (-15 + 0.5, 12 - 0.5, 1.5),
            'green': (-15 + 0.5, 6 - 0.5,  1.5),
            'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
        }

        # Closed gripper angle
        self.servo1 = 500

    def initMove(self):
        """
        Move arm to initial position
        """
        print("ColorTracking Init")
        Board.setBusServoPulse(1, self.servo1 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

    def run(self, img):
        """
        Run the camera
        """
        # Get the image dimensions
        img_h, img_w = img.shape[:2]

        # Draw crosshairs on image (+ overtop image)
        self.perception.draw_crosshairs(img, img_h, img_w)

        # Make a copy of the input frame
        img_copy = img.copy()

        frame_lab = self.perception.process_frame(img_copy) 

        area_max_contour, area_max = self.perception.outline_object(frame_lab)

        if area_max > 2500:  # find the maximum area
            rect = cv2.minAreaRect(area_max_contour)
            box = np.int0(cv2.boxPoints(rect))

            self.roi = getROI(box) # get roi zone
            self.get_roi = True

            img_centerx, img_centery = getCenter(self.rect, self.roi, self.size, square_length)  # get the center coordinates of block
            self.world_x, self.world_y = convertCoordinate(img_centerx, img_centery, self.size) # convert to world coordinates
            
            cv2.drawContours(img, [box], -1, self.range_rgb[self.detect_color], 2)
            cv2.putText(img, '(' + str(self.world_x) + ',' + str(self.world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.range_rgb[self.detect_color], 1) # draw center position
            distance = math.sqrt(pow(self.world_x - self.last_x, 2) + pow(self.world_y - self.last_y, 2)) # compare the last coordinate to determine whether to move
            self.last_x, self.last_y = self.world_x, self.world_y
            self.track = True

            # cumulative judgment
            if self.action_finish:
                if distance < 0.3:
                    self.center_list.extend((self.world_x, self.world_y))
                    self.count += 1
                    if self.start_count_t1:
                        self.start_count_t1 = False
                        self.t1 = time.time()
                    if time.time() - self.t1 > 1.5:
                        self.rotation_angle = rect[2]
                        self.start_count_t1 = True
                        self.world_X,self. world_Y = np.mean(np.array(self.center_list).reshape(self.count, 2), axis=0)
                        self.count = 0
                        self.center_list = []
                        self.start_pick_up = True
                else:
                    self.t1 = time.time()
                    self.start_count_t1 = True
                    self.ount = 0
                    self.center_list = []
        return img