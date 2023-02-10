import logging
from picarx_improved import Picarx
import cv2
import datetime
import time
import math
import numpy as np
from lane_follower_helper import HandCodedLaneFollower
from sensor import Sensor, Camera
import sys
sys.path.append(r'/home/marcus/RobotSystems/robot-hat/robot_hat')
from robot_hat import ADC, Ultrasonic
from picamera.array import PiRGBArray
from picamera import PiCamera


class CameraLineFollow(object):
    def __init__(self):
        """ Init camera and wheels"""
        logging.info('Creating a CameraLineFollow...')

        self.px = Picarx()
        self.pi_camera = Camera()
        self.camera_output = None

        logging.debug('Set up camera')
        self.current_steer_angle = 0
        self.px.set_dir_servo_angle(0)
        time.sleep(0.5)

    def camera_line_follow(self):
        with PiCamera() as camera:
            camera.resolution = (640, 480)  
            camera.framerate = 24
            rawCapture = PiRGBArray(camera, size=camera.resolution)  
            time.sleep(2)
            self.px.forward(20)
            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                img = frame.array
                cv2.imshow("mask frame", img)  # OpenCV image show

                self.follow_lane(img)
                rawCapture.truncate(0)  # Release cache
                
                k = cv2.waitKey(1) & 0xFF
                if k == 27:
                    break

            print('quit ...') 
            cv2.destroyAllWindows()
            camera.close()  

    def follow_lane(self, frame):
        cv2.imshow("raw frame", frame)

        self.pi_camera.frame = frame
        lane_line, lane_image = self.pi_camera.image_processing()
        self.camera_output = lane_line

        final_frame = self.steer(lane_image, lane_line)

        return final_frame
    
    def steer(self, frame, lane_lines):
        logging.debug('steering...')
        if len(lane_lines) == 0:
            logging.error('No lane lines detected, nothing to do.')
            return frame

        new_steering_angle = self.compute_steering_angle(frame, lane_lines)
        self.curr_steering_angle = self.stabilize_steering_angle(self.current_steer_angle, new_steering_angle, len(lane_lines))
        print(self.current_steer_angle)
        if self.px is not None:
            self.px.set_dir_servo_angle(self.current_steer_angle)
        curr_heading_image = self.display_heading_line(frame, self.current_steer_angle)
        cv2.imshow("heading", curr_heading_image)
        return curr_heading_image

    def compute_steering_angle(frame, lane_lines):
        """ Find the steering angle based on lane line coordinate
            We assume that camera is calibrated to point to dead center
        """
        if len(lane_lines) == 0:
            logging.info('No lane lines detected, do nothing')
            return 0

        height, width, _ = frame.shape
        if len(lane_lines) == 1:
            logging.debug('Only detected one lane line, just follow it. %s' % lane_lines[0])
            x1, _, x2, _ = lane_lines[0][0]
            x_offset = x2 - x1
        else:
            _, _, left_x2, _ = lane_lines[0][0]
            _, _, right_x2, _ = lane_lines[1][0]
            camera_mid_offset_percent = 0.02 # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
            mid = int(width / 2 * (1 + camera_mid_offset_percent))
            x_offset = (left_x2 + right_x2) / 2 - mid

        # find the steering angle, which is angle between navigation direction to end of center line
        y_offset = int(height / 2)

        angle_to_mid_radian = math.atan(x_offset / y_offset)  # angle (in radian) to center vertical line
        angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)  # angle (in degrees) to center vertical line
        steering_angle = angle_to_mid_deg   # this is the steering angle needed by picar front wheel

        logging.debug('new steering angle: %s' % steering_angle)
        return steering_angle

    def stabilize_steering_angle(curr_steering_angle, new_steering_angle, num_of_lane_lines, max_angle_deviation_two_lines=5, max_angle_deviation_one_lane=1):
        """
        Using last steering angle to stabilize the steering angle
        This can be improved to use last N angles, etc
        if new angle is too different from current angle, only turn by max_angle_deviation degrees
        """
        if num_of_lane_lines == 2 :
            # if both lane lines detected, then we can deviate more
            max_angle_deviation = max_angle_deviation_two_lines
        else :
            # if only one lane detected, don't deviate too much
            max_angle_deviation = max_angle_deviation_one_lane
        
        angle_deviation = new_steering_angle - curr_steering_angle
        if abs(angle_deviation) > max_angle_deviation:
            stabilized_steering_angle = int(curr_steering_angle
                                            + max_angle_deviation * angle_deviation / abs(angle_deviation))
        else:
            stabilized_steering_angle = new_steering_angle
        logging.info('Proposed angle: %s, stabilized angle: %s' % (new_steering_angle, stabilized_steering_angle))
        return stabilized_steering_angle

    def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5, ):
        heading_image = np.zeros_like(frame)
        height, width, _ = frame.shape

        # figure out the heading line from steering angle
        # heading line (x1,y1) is always center bottom of the screen
        # (x2, y2) requires a bit of trigonometry

        # Note: the steering angle of:
        # 0-89 degree: turn left
        # 90 degree: going straight
        # 91-180 degree: turn right 
        steering_angle_radian = steering_angle / 180.0 * math.pi
        x1 = int(width / 2)
        y1 = height
        if steering_angle_radian == 0:
            steering_angle_radian = 0.001
        x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
        y2 = int(height / 2)

        cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
        heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

        return heading_image


if __name__ == '__main__':
    camera = CameraLineFollow()
    camera.camera_line_follow()