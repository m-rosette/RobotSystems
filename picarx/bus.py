import concurrent.futures
from readerwriterlock import rwlock
from sensor import Sensor
from interpreter import Interpreter
from controller import Controller
from picarx_improved import Picarx


class Bus():
    def __init__(self):
        self.message = None
        self.lock = rwlock.RWLockWriteD()

    def write(self, message):
        with self.lock.gen_wlock():
            self.message = message

    def read(self):
        with self.lock.gen_rlock():
            message = self.message
        return message

class Exexute():
    def __init__(self) -> None:
        self.px = Picarx()
        self.grayscale_bus = Bus()
        self.ultrasonic_bus = Bus()
        self.camera_bus = Bus()
        self.interp_bus = Bus()

        self.sensor = Sensor()
        self.interpreter = Interpreter()
        self.controller = Controller(self.px)

        self.px.forward(20)

    def executor(self):
        delay = 0.1
        while True:
            with concurrent.futures.ThreadPoolExecutor(max_workers = 3) as executor:
                eGrayscale = executor.submit(self.sensor.grayscale_bus, self.grayscale_bus, delay)
                # eUltrasonic = executor.submit(self.sensor.ultrasonic_bus, self.ultrasonic_bus, delay)
                # eCamera = executor.submit(self.sensor.camera_bus, self.camera_bus, delay)
                eInterpreter = executor.submit(self.interpreter.interpreter_bus, self.grayscale_bus, self.interp_bus, delay)
                eController = executor.submit(self.controller.controller_bus, self.interp_bus, delay)

            eGrayscale.result()
            # eUltrasonic.result()
            # eCamera.result()
            eInterpreter.result()
            eController.result()


if __name__ == '__main__':
    executor = Exexute()
    executor.executor()
