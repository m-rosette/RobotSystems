#!/usr/bin/python3
"""
This file demonstrates the basic operation of a RossROS program.

First, it defines two signal-generator functions (a +/-1 square wave and a saw-tooth wave) and a
function for multiplying two scalar values together.

Second, it generates buses to hold the most-recently sampled values for the signal-generator functions,
the product of the two signals, and a countdown timer determining how long the program should run

Third, it wraps the signal-generator functions into RossROS Producer objects, and the multiplication
function into a RossROS Consumer-Producer object.

Fourth, it creates a RossROS Printer object to periodically display the current bus values, and a RossROS Timer
object to terminate the program after a fixed number of seconds

Fifth and finally, it makes a list of all of the RossROS objects and sends them to the runConcurrently function
for simultaneous execution
"""

import sys
sys.path.append(r'/home/marcus/RobotSystems/RossROS')
import rossros as rr
from sensor import Sensor
from interpreter import Interpreter
from controller import Controller
from picarx_improved import Picarx


""" First Part: Signal generation and processing functions """
picar = Picarx()
controller = Controller(picar)
sensor = Sensor()
interpreter = Interpreter()


""" Second Part: Create buses for passing data """

# Initiate data and termination busses
grayscale_bus = rr.Bus([0, 0, 0], name="gray bus")
ultrasonic_bus = rr.Bus(0, name="ultrasonic bus")
camera_bus = rr.Bus(0, "camera bus")

interp_bus = rr.Bus(0, name="interpreter bus")
controller_bus = rr.Bus(0, name="controller bus")
terminator_bus = rr.Bus(0, name="termination bus")

delay = 0.05

""" Third Part: Wrap signal generation and processing functions into RossROS objects """

# Wrap the grayscale sensor into a producer
read_grayscale = rr.Producer(
    sensor.get_grayscale_data,  # function that will generate data
    grayscale_bus,  # output data bus
    delay,  # delay between data generation cycles
    terminator_bus,  # bus to watch for termination signal
    "Read grayscale data")

# Wrap the ultrasonic sensor into a producer
read_ultrasonic = rr.Producer(
    sensor.get_distance,  # function that will generate data
    ultrasonic_bus,  # output data bus
    delay,  # delay between data generation cycles
    terminator_bus,  # bus to watch for termination signal
    "Read ultrasonic data")

# Wrap the ultrasonic sensor into a producer
read_camera = rr.Producer(
    sensor.live_camera,  # function that will generate data
    camera_bus,  # output data bus
    delay,  # delay between data generation cycles
    terminator_bus,  # bus to watch for termination signal
    "Read camera data")

# Wrap the multiplier function into a consumer-producer
interp_grayscale = rr.ConsumerProducer(
    interpreter.detect_edge,  # function that will process data
    grayscale_bus,  # input data buses
    interp_bus,  # output data bus
    delay,  # delay between data control cycles
    terminator_bus,  # bus to watch for termination signal
    "Interpret grayscale data")

car_controller = rr.Consumer(
    controller.line_follow,
    interp_bus,
    delay,
    terminator_bus,
    "Process interp data"
)

""" Fourth Part: Create RossROS Printer and Timer objects """

# Make a printer that returns the most recent wave and product values
print_buses = rr.Printer(
    (grayscale_bus, camera_bus, interp_bus, controller_bus),  # input data buses
    # bMultiplied,      # input data buses
    0.25,  # delay between printing cycles
    terminator_bus,  # bus to watch for termination signal
    "Print raw and derived data",  # Name of printer
    "Data bus readings are: ")  # Prefix for output

# Make a timer (a special kind of producer) that turns on the termination
# bus when it triggers
termination_timer = rr.Timer(
    terminator_bus,  # Output data bus
    10,  # Duration
    0.01,  # Delay between checking for termination time
    terminator_bus,  # Bus to check for termination signal
    "Termination timer")  # Name of this timer


""" Fifth Part: Concurrent execution """

# Create a list of producer-consumers to execute concurrently
producer_consumer_list = [read_grayscale,
                          read_ultrasonic,
                          read_camera,
                          interp_grayscale,
                          car_controller,
                          termination_timer]

# Execute the list of producer-consumers concurrently
rr.runConcurrently(producer_consumer_list)