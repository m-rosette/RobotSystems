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
        self.sensor = Sensor()
        self.interpreter = Interpreter()
        self.controller = Controller(self.px)

        self.grayscale_bus = Bus([0, 0, 0], name="gray bus")
        self.ultrasonic_bus = Bus(20, name="ultrasonic bus")

        self.ultra_interp_bus = Bus(name="ultrasonic interpreter bus")
        self.interp_bus = Bus(name="interpreter bus")
        self.terminator_bus = Bus(name="termination bus")
        

    def execute(self):
        while True:
            timer = Timer(self.terminator_bus, 1, 0.01, self.terminator_bus)
            sensor_producer = Producer(self.sensor.get_grayscale_data, output_buses=self.grayscale_bus, delay=0.1, termination_buses=self.terminator_bus, name="sensor producer")
            interpreter_cons_prod = ConsumerProducer(self.interpreter.detect_edge, input_buses=self.grayscale_bus, output_buses=self.interp_bus, delay=0.1, termination_buses=self.terminator_bus, name="gray sensor consumer producer")
            controller_consumer = Consumer(self.controller.line_follow, input_buses=(self.interp_bus, self.ultra_interp_bus), delay=0.1, termination_buses=self.terminator_bus, name="sensor producer")

            ultra_producer = Producer(self.sensor.get_distance, output_buses=self.ultrasonic_bus, delay=0.1, termination_buses=self.terminator_bus, name="ultra producer")
            ultra_cons_prod = ConsumerProducer(self.interpreter.ultrasonic_stop, input_buses=self.ultrasonic_bus, output_buses=self.ultra_interp_bus, delay=0.1, termination_buses=self.terminator_bus, name="ultra sensor consumer producer")

            with concurrent.futures.ThreadPoolExecutor(max_workers = 6) as executor:
                eGrayscale = executor.submit(sensor_producer)
                eInterpreter = executor.submit(interpreter_cons_prod)
                eUltraSensor = executor.submit(ultra_producer)
                eUltraInterpreter = executor.submit(ultra_cons_prod)

                eController = executor.submit(controller_consumer)
                eTimer = executor.submit(timer)

            eGrayscale.result()
            eInterpreter.result()
            eController.result()
            eTimer.result()
            eUltraSensor.result()
            eUltraInterpreter.result()


if __name__ == '__main__':
    executor = RossROS_Exexute()
    executor.execute()






