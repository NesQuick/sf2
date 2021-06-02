from prog_control import preactivate, move_forward, move_reverse
import RPi.GPIO as io
from pysolar.solar import *
import datetime
import sys, tty, termios, time, signal
import numpy as np

latitude = 55.800195
longitude = 37.575226
# latitude = 33.704334  #somewhere in USA
# longitude = -111.519322
update_freq = 3   # solar coords update freq
tolerance_angle = 0.140625 # tolerance angle between panel and sun (1 * 0.1125)

tracker_type = "1-axis-altitude"    # "1-axis-azimuth" or "2-axis"

reductor_point = 10

angle = 0
motor_angle = 0

preactivate() # only on raspberry
move_forward(90 * reductor_point) # only on raspberry

# The getch method can determine which key has been pressed
# by the user on the keyboard by accessing the system files
# It will then return the pressed key as a variable
class Timeout():
  """Timeout class using ALARM signal"""
  class Timeout(Exception): pass

  def __init__(self, sec):
    self.sec = sec

  def __enter__(self):
    signal.signal(signal.SIGALRM, self.raise_timeout)
    signal.setitimer(signal.ITIMER_REAL, self.sec, 0.1)

  def __exit__(self, *args):
    signal.alarm(0) # disable alarm

  def raise_timeout(self, *args):
    raise Timeout.Timeout()

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        with Timeout(update_freq):
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
    except Timeout.Timeout:
        ch = "no_char"
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


while True:
    char = getch()
    # print("input: " + str(char))
    date = datetime.datetime.now(datetime.timezone.utc).astimezone()
    altitude_deg = get_altitude(latitude, longitude, date)
    azimuth_deg = get_azimuth(latitude, longitude, date)

    solar_radiation = radiation.get_radiation_direct(date, altitude_deg)
    # print("motor angle: " + str(motor_angle))
    # print("alt: " + str(altitude_deg))
    # print("*****************")
    if tracker_type == "1-axis-altitude":
        if altitude_deg >= 0:
            if altitude_deg - angle > tolerance_angle:
                move_forward(tolerance_angle * reductor_point * int((altitude_deg - angle) / tolerance_angle)) # only on raspberry
                print("moved forward: " + str(tolerance_angle * reductor_point * int((altitude_deg - angle) / tolerance_angle)))
                print("date: " + str(date))
                motor_angle = motor_angle + tolerance_angle * reductor_point * int((altitude_deg - angle) / tolerance_angle)
                angle_difference = np.round(tolerance_angle * int((altitude_deg - angle) / tolerance_angle), 4)
                print("moved: " + str(tolerance_angle * reductor_point * int((altitude_deg - angle) / tolerance_angle)))
                angle = np.round(angle + angle_difference, 4)
                print("angle: " + str(angle))
                print("altitude: " + str(altitude_deg))
                print("motor angle: " + str(motor_angle))
                print("*****************")
            elif altitude_deg - angle < -tolerance_angle:
                move_reverse(tolerance_angle * reductor_point * int((angle - altitude_deg) / tolerance_angle)) # only on raspberry
                print("moved reverse: " + str(tolerance_angle * reductor_point * int((angle - altitude_deg) / tolerance_angle)))
                print("date: " + str(date))
                motor_angle = motor_angle - tolerance_angle * reductor_point * int((angle - altitude_deg) / tolerance_angle)
                angle_difference = np.round(tolerance_angle * int((angle - altitude_deg) / tolerance_angle), 4)
                print("moved: " + str(-tolerance_angle * reductor_point * int((angle - altitude_deg) / tolerance_angle)))
                angle = np.round(angle - angle_difference, 4)
                print("angle: " + str(angle))
                print("altitude: " + str(altitude_deg))
                print("motor angle: " + str(motor_angle))
                print("*****************")

    if char == "x":
        move_reverse(angle * reductor_point)
        motor_angle = motor_angle - np.round(angle, 4) * reductor_point
        print("motor_angle: " + str(motor_angle))
        move_reverse(90 * reductor_point) # only on raspberry
        # # Program will cease all GPIO activity before terminating
        io.cleanup()  #only on raspberry
        print("Program Ended")
        break

    char = ""
