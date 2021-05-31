import RPi.GPIO as io
io.setmode(io.BCM)
import sys, tty, termios, time


# This blocks of code defines the three GPIO
# pins used for the stepper motor
motor_enable_pin = 17
motor_direction_pin = 27
motor_step_pin = 22
delay = 3E-004              # By playing with this delay you can influence the rotational speed
# This can be configured on the driver using the DIP-switches 
pulses_per_rev = 50          # gives angle = 1.40625 per rev 
pulses_360 = 12800          # actual pulses on driver

def preactivate():
    io.setup(motor_enable_pin, io.OUT)
    io.setup(motor_direction_pin, io.OUT)
    io.setup(motor_step_pin, io.OUT)

    # Setting the stepper pins to false so the motors will not move
    # until the program gives input
    io.output(motor_enable_pin, False)
    io.output(motor_step_pin, False)

# This section of code defines the methods used to determine
# whether the stepper motor needs to spin forward or backwards. 
# Different directions are acheived by setting the
# direction GPIO pin to true or to false. 
# My driver required:
#   DIR must be ahead of PUL effective edge by 5 micro-s to ensure correct direction;
#   Pulse width not less than 2.5 micro-s;
#   Pulse low-level width not less than 2.5 micro-s.

def stepper_enable():
    io.output(motor_enable_pin, False)

def stepper_disable():
    io.output(motor_enable_pin, True)

def step_once():
    io.output(motor_step_pin, True)
    time.sleep(delay)
    io.output(motor_step_pin, False)
    time.sleep(delay)

def step_forward():
    io.output(motor_direction_pin, True)
    time.sleep(delay)
    step_once()

def step_reverse():
    io.output(motor_direction_pin, False)
    time.sleep(delay)
    step_once()
    
def move_forward(angle): # angle must be multiple to 0.140625
    stepper_enable()
    revs = angle/1.40625
    for y in range(0, int(revs)):
        for x in range(0, pulses_per_rev):
            step_forward()
    stepper_disable()

def move_reverse(angle): # angle must be multiple to 0.140625
    stepper_enable()
    revs = angle/1.40625
    for y in range(0, int(revs)):
        for x in range(0, pulses_per_rev):
            step_reverse()
    stepper_disable()


