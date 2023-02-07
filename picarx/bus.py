import concurrent.futures
from readerwriterlock import rwlock
from sensor import GrayscaleSensor
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
        self.sensor_bus = GrayscaleSensor()
        self.interpreter = Interpreter()
        self.controller = Controller(self.px)

    def executor(self):
        delay = 0.1

        with concurrent.futures.ThreadPoolExecutor(max_workers = 2) as executor:
            eSensor = executor.submit(self.sensor_bus.sensor_bus, self.grayscale_bus, delay)
            eInterpreter = executor.submit(self.interpreter.interpreter_bus, self.grayscale_bus, self.interpreter, delay)

        eSensor.result()
        eInterpreter.result()


if __name__ == '__main__':
    executor = Exexute()
    executor.executor()
