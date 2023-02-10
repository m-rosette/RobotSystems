import sys
sys.path.append(r'/home/marcus/RobotSystems/RossROS')
from rossros import Bus, ConsumerProducer, Consumer, Producer, Timer
import logging
import time
import math
from sensor import Sensor
from interpreter import Interpreter
from controller import Controller
from picarx_improved import Picarx
import concurrent.futures
from readerwriterlock import rwlock


class RossROS_Exexute():
    def __init__(self) -> None:
        self.px = Picarx()
        
        # self.gray_sensor = self.sensor.grayscale_bus
        self.interpreter = Interpreter()
        self.controller = Controller(self.px)

        self.grayscale_bus = Bus(name="gray bus")
        self.ultrasonic_bus = Bus(name="ultrasonic bus")
        self.camera_bus = Bus("camera bus")
        self.interp_bus = Bus(name="interpreter bus")
        self.terminator_bus = Bus(name="termination bus")
        
        self.sensor = Sensor()
        self.gray_sensor = self.sensor.grayscale_bus(self.grayscale_bus, 0.1)
    def execute(self):
        while True:
            timer = Timer(self.terminator_bus, 1, 0.01, self.terminator_bus)
            sensor_producer = Producer(self.gray_sensor, output_buses=self.grayscale_bus, delay=0.1, termination_buses=self.terminator_bus, name="sensor producer")
            interpreter_cons_prod = ConsumerProducer(self.interpreter, input_buses=self.grayscale_bus, output_buses=self.interp_bus, delay=0.1, termination_buses=self.terminator_bus, name="interpreter consumer producer")
            controller_consumer = Consumer(self.controller, input_buses=(self.interp_bus, self.ultrasonic_bus), delay=0.1, termination_buses=self.terminator_bus, name="sensor producer")

            with concurrent.futures.ThreadPoolExecutor(max_workers = 3) as executor:
                eGrayscale = executor.submit(sensor_producer)
                eInterpreter = executor.submit(interpreter_cons_prod)
                eController = executor.submit(controller_consumer)
                eTimer = executor.submit(timer)

            eGrayscale.result()
            eInterpreter.result()
            eController.result()
            eTimer.result()


if __name__ == '__main__':
    executor = RossROS_Exexute()
    executor.execute()






