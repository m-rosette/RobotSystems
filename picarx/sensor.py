import sys
sys.path.append(r'/home/marcus/RobotSystems/robot-hat/robot_hat')
from robot_hat import ADC, Ultrasonic
from picamera.array import PiRGBArray
from picamera import PiCamera
import picarx_improved as px
import numpy as np
import time
import math
import cv2
import logging
from logdecorator import log_on_start , log_on_end , log_on_error


logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO, datefmt ="%H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)


class Sensor(object):
    def __init__(self):
        # Ultrasonic
        self.trig = px.Pin("D2")
        self.echo = px.Pin("D3")
        self.ultrasonic = Ultrasonic(self.trig, self.echo)

        # Grayscale
        self.chn_0 = ADC("A0")
        self.chn_1 = ADC("A1")
        self.chn_2 = ADC("A2")

        # Camera
        self.camera_output = None
        self.pi_camera = Camera()

    ######## SENSOR BUSSES
    def ultrasonic_bus(self, bus, delay):
        while True:
            sonar_dist = self.get_distance()
            bus.write(sonar_dist)
            time.sleep(delay)

    def grayscale_bus(self, bus, delay):
        while True:
            gray_list = self.get_grayscale_data()
            bus.write(gray_list)
            time.sleep(delay)

    def camera_bus(self, bus, delay):
        while True:
            self.live_camera()
            bus.write(self.camera_output)
            time.sleep(delay)

    ######## ULTRASONIC ########
    def get_distance(self):
        return self.ultrasonic.read()

    ######## GRAYSCALE ########
    def get_grayscale_data(self):
        adc_value_list = []
        adc_value_list.append(self.chn_0.read())
        adc_value_list.append(self.chn_1.read())
        adc_value_list.append(self.chn_2.read())
        return adc_value_list

    ######## CAMERA ########
    @log_on_start(logging.DEBUG, "Starting camera ('esc' to quit)")
    @log_on_end(logging.DEBUG, "Quitting camera")
    def live_camera(self):
        with PiCamera() as camera:
            camera.resolution = (640, 480)  
            camera.framerate = 24
            rawCapture = PiRGBArray(camera, size=camera.resolution)  
            time.sleep(2)

            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                img = frame.array
                cv2.imshow("raw image", img)
                self.pi_camera.frame = img

                lane_line, lane_image = self.pi_camera.image_processing()
                self.camera_output = lane_line

                # cv2.imshow("mask frame", lane_image)  # OpenCV image show
                rawCapture.truncate(0)  # Release cache
                
                k = cv2.waitKey(1) & 0xFF
                if k == 27:
                    break

            print('quit ...') 
            cv2.destroyAllWindows()
            camera.close()  


class Camera():
    def __init__(self) -> None:
        self.frame = None

    def mask_generation(self):
        # filter for blue lane lines
        hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([30, 40, 0])
        upper_blue = np.array([150, 255, 255])

        return cv2.inRange(hsv, lower_blue, upper_blue)
    
    def detect_edge(self, frame):
        # detect edges
        edges = cv2.Canny(frame, 200, 400)
        return edges

    def region_of_interest(self, canny):
        height, width = canny.shape
        mask = np.zeros_like(canny)

        # only focus bottom half of the screen
        polygon = np.array([[
            (0, height * 1 / 2),
            (width, height * 1 / 2),
            (width, height),
            (0, height),
        ]], np.int32)

        cv2.fillPoly(mask, polygon, 255)
        # cv2.imshow("mask", mask)
        masked_image = cv2.bitwise_and(canny, mask)
        return masked_image

    def detect_line_segments(self, cropped_edges):
        # tuning min_threshold, minLineLength, maxLineGap is a trial and error process by hand
        rho = 1  # precision in pixel, i.e. 1 pixel
        angle = np.pi / 180  # degree in radian, i.e. 1 degree
        min_threshold = 10  # minimal of votes
        line_segments = cv2.HoughLinesP(cropped_edges, rho, angle, min_threshold, np.array([]), minLineLength=8,
                                        maxLineGap=4)
        if line_segments is not None:
            for line_segment in line_segments:
                logging.debug('detected line_segment:')
                logging.debug("%s of length %s" % (line_segment, self.length_of_line_segment(line_segment[0])))
        return line_segments

    def length_of_line_segment(self, line):
        x1, y1, x2, y2 = line
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def make_points(self, frame, line):
        height, width, _ = frame.shape
        slope, intercept = line
        y1 = height  # bottom of the frame
        y2 = int(y1 * 1 / 2)  # make points from middle of the frame down

        # bound the coordinates within the frame
        x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
        x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
        return [[x1, y1, x2, y2]]

    def find_line(self, line_segments):
        # Combines line segments into one lane (blue tape line)
        line_fit = []
        lane_line = []
        if line_segments is None:
            logging.info('No line_segment segments detected')
            return lane_line

        for line_segment in line_segments:
            for x1, y1, x2, y2 in line_segment:
                if x1 == x2:
                    logging.info('skipping vertical line segment (slope=inf): %s' % line_segment)
                    continue
                fit = np.polyfit((x1, x2), (y1, y2), 1)
                slope = fit[0]
                intercept = fit[1]
                line_fit.append((slope, intercept))

        line_fit_average = np.average(line_fit, axis=0)
        if len(line_fit) > 0:
            lane_line.append(self.make_points(self.frame, line_fit_average))

        return lane_line

    def display_lines(self, lines, line_color=(0, 255, 0), line_width=2):
        line_image = np.zeros_like(self.frame)
        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
        line_image = cv2.addWeighted(self.frame, 0.8, line_image, 1, 1)
        return line_image

    def image_processing(self):
        mask = self.mask_generation()
        line_edge = self.detect_edge(mask)
        cropped_line_edge = self.region_of_interest(line_edge)
        line_segments = self.detect_line_segments(cropped_line_edge)
        lane_line = self.find_line(line_segments)
        lane_image = self.display_lines(lane_line)
        return lane_line, lane_image


if __name__ == '__main__':
    sensor = Sensor()
    sensor.live_camera()
