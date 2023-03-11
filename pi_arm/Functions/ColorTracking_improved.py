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


class ColorTracking:
    def __init__(self, AK, target_color):
        self.AK = AK
        self.__target_color = target_color

        self.range_rgb = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
        }

        # Colors block placement coordinates (x, y, z)
        self.coordinate = {
            'red':   (-15 + 0.5, 12 - 0.5, 1.5),
            'green': (-15 + 0.5, 6 - 0.5,  1.5),
            'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
        }
        
        # Closed gripper angle
        self.servo1 = 500

        # Various tracking variables
        self.count = 0
        self._stop = False
        self.track = False
        self.get_roi = False
        self.center_list = []
        self.first_move = True
        self.detect_color = 'None'           # ---------------------------------------WHEN DOES THIS VALUE GET SET?????????????????????????????????????????????////
        self.action_finish = True
        self.start_pick_up = False
        self.start_count_t1 = True
        self.is_running = False

        self.rect = None
        self.size = (640, 480)
        self.rotation_angle = 0
        self.unreachable = False
        self.world_X, self.world_Y = 0, 0
        self.world_x, self.world_y = 0, 0

        self.t1 = 0
        self.roi = ()
        self.last_x, self.last_y = 0, 0

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

    def initMove(self):
        """
        Move arm to initial position
        """
        print("ColorTracking Init")
        Board.setBusServoPulse(1, self.servo1 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

    def setBuzzer(self, timer):
        Board.setBuzzer(0)
        Board.setBuzzer(1)
        time.sleep(timer)
        Board.setBuzzer(0)

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

    def reset(self):  
        """
        Reset all variables
        """  
        self.count = 0
        self._stop = False
        self.track = False
        self.get_roi = False
        self.center_list = []
        self.first_move = True
        self.__target_color = self.target_color
        self.detect_color = 'None'
        self.action_finish = True
        self.start_pick_up = False
        self.start_count_t1 = True
        self.is_running = False

    def start(self):
        """
        Starts the movement of the arm
        """
        self.reset()
        self.is_running = True
        print("ColorTracking Start")

    def stop(self):
        """ 
        Starts the movement of the arm
        """
        self._stop = True
        self.is_running = False
        print("ColorTracking Stop")

    def exit(self):
        """
        Exit the movement
        """
        self._stop = True
        self.is_running = False
        print("ColorTracking Exit")

    def move(self):
        """
        ArmPi move thread
        """
        while True:
            if self.is_running:
                if self.first_move and self.start_pick_up: # when an object be detected for the first time                
                    self.action_finish = False
                    self.set_rgb(self.detect_color)
                    self.setBuzzer(0.1)               
                    result = self.AK.setPitchRangeMoving((self.world_X, self.world_Y - 2, 5), -90, -90, 0) # do not fill running time parameters,self-adaptive running time
                    if result == False:
                        self.unreachable = True
                    else:
                        self.unreachable = False

                    time.sleep(result[2]/1000) # the third item of return parameter is time 

                    # Update first move bool-flags
                    self.start_pick_up = False
                    self.first_move = False

                    # Specify the action has been completed
                    self.action_finish = True

                elif not self.first_move and not self.unreachable: # not the first time to detected object
                    self.set_rgb(self.detect_color)

                    if self.track: # if it is following state
                        if not self.is_running: # stop and exit flag detection
                            continue

                        self.AK.setPitchRangeMoving((self.world_x, self.world_y - 2, 5), -90, -90, 0, 20)
                        time.sleep(0.02)                    
                        self.track = False

                    if self.start_pick_up: # if it is detected that the block has not removed for a period of time, start to pick up
                        self.action_finish = False

                        if not self.is_running: # stop and exit flag detection
                            continue

                        Board.setBusServoPulse(1, self.servo1 - 280, 500)  # claw open

                        # calculate angle at that the clamper gripper needs to rotate
                        servo2_angle = getAngle(self.world_X, self.world_Y, self.rotation_angle)
                        Board.setBusServoPulse(2, servo2_angle, 500)
                        time.sleep(0.8)
                        
                        if not self.is_running:
                            continue
                        self.AK.setPitchRangeMoving((self.world_X, self.world_Y, 2), -90, -90, 0, 1000)  # reduce height
                        time.sleep(2)
                        
                        if not self.is_running:
                            continue
                        Board.setBusServoPulse(1, self.servo1, 500)  # claw colsed
                        time.sleep(1)
                        
                        if not self.is_running:
                            continue
                        Board.setBusServoPulse(2, 500, 500)
                        AK.setPitchRangeMoving((self.world_X, self.world_Y, 12), -90, -90, 0, 1000)  # Armpi robot arm up
                        time.sleep(1)
                        
                        if not self.is_running:
                            continue
                        # Sort and place different colored blocks 
                        result = self.AK.setPitchRangeMoving((self.coordinate[self.detect_color][0], self.coordinate[self.detect_color][1], 12), -90, -90, 0)   
                        time.sleep(result[2]/1000)
                        
                        if not self.is_running:
                            continue
                        servo2_angle = getAngle(self.coordinate[self.detect_color][0], self.coordinate[self.detect_color][1], -90)
                        Board.setBusServoPulse(2, servo2_angle, 500)
                        time.sleep(0.5)

                        if not self.is_running:
                            continue
                        self.AK.setPitchRangeMoving((self.coordinate[self.detect_color][0], self.coordinate[self.detect_color][1], self.coordinate[self.etect_color][2] + 3), -90, -90, 0, 500)
                        time.sleep(0.5)
                        
                        if not self.is_running:
                            continue
                        self.AK.setPitchRangeMoving((self.coordinate[self.detect_color]), -90, -90, 0, 1000)
                        time.sleep(0.8)
                        
                        if not self.is_running:
                            continue
                        Board.setBusServoPulse(1, self.servo1 - 200, 500)  # gripper open，put down object
                        time.sleep(0.8)
                        
                        if not self.is_running:
                            continue                    
                        self.AK.setPitchRangeMoving((self.coordinate[self.detect_color][0], self.coordinate[self.detect_color][1], 12), -90, -90, 0, 800)
                        time.sleep(0.8)

                        self.initMove()  # back to initial position 
                        time.sleep(1.5)

                        self.detect_color = 'None'
                        self.first_move = True
                        self.get_roi = False
                        self.action_finish = True
                        self.start_pick_up = False
                        self.set_rgb(self.detect_color)
                    else:
                        time.sleep(0.01)
            else:
                if self._stop:
                    self._stop = False
                    Board.setBusServoPulse(1, self.servo1 - 70, 300)
                    time.sleep(0.5)
                    Board.setBusServoPulse(2, 500, 500)
                    self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
                    time.sleep(1.5)
                time.sleep(0.01)

    def run_threading(self):
        """
        Running the Thread"""
        th = threading.Thread(target=self.move)
        th.setDaemon(True)
        th.start()

    def run(self, img):
        """
        Run the camera
        """

        # Make a copy of the input frame
        img_copy = img.copy()

        # Get the image dimensions
        img_h, img_w = img.shape[:2]

        # Draw crosshairs on image (+ overtop image)
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)
        
        if not self.is_running:
            return img
        
        # Verify image size matches that of camera
        frame_resize = cv2.resize(img_copy, self.size, interpolation=cv2.INTER_NEAREST)

        # Apply a blur to the image
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)

        # If it is detected with an area recognized object, the area will be detected until there is no object
        if self.get_roi and self.start_pick_up:
            self.get_roi = False
            frame_gb = getMaskROI(frame_gb, self.roi, self.size)    
        
        # Convert the image to LAB space
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  
        
        area_max = 0
        areaMaxContour = 0
        if not self.start_pick_up:
            for i in color_range:
                print(color_range)
                if i in self.__target_color:
                    detect_color = i
                    frame_mask = cv2.inRange(frame_lab, color_range[detect_color][0], color_range[detect_color][1])  # mathematical operation on the original image and mask
                    opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # Opening (morphology)
                    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # Closing (morphology)
                    contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # find countour
                    areaMaxContour, area_max = self.getAreaMaxContour(contours)  # find the maximum countour

            if area_max > 2500:  # find the maximum area
                rect = cv2.minAreaRect(areaMaxContour)
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


if __name__ == '__main__':
    if sys.version_info.major == 2:
        print('Please run this program with python3!')
        sys.exit(0)
    
    AK = ArmIK()
    tracking = ColorTracking(AK=AK)
    tracking.initMove()
    tracking.start()

    my_camera = Camera.Camera()
    my_camera.camera_open()
    
    while True:
        img = my_camera.frame
        if img is not None:
            frame = img.copy()
            Frame = tracking.run(frame)           
            cv2.imshow('Frame', Frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
    my_camera.camera_close()
    cv2.destroyAllWindows()




