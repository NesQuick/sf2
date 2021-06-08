from pvlib import solarposition, tracking
import numpy as np
import datetime
import sys, tty, termios, time, signal
from prog_control import preactivate, move_forward, move_reverse
from rain_detection import rain
import RPi.GPIO as io
from wind_detection import windSpeed, temperature
# from pysolar.solar import *

# print(pytz.country_timezones('Europe'))

#tz = 'Europe/Moscow'
#lat, lon = 55.800195, 37.575226

tz = 'America/Los_Angeles'
lat, lon = 34.065197, -118.340106

update_freq = 3   # solar coords update freq
tolerance_angle = 1.125 # tolerance angle between panel and sun (8 * 0.140625)

reductor_point = 10

angle = 0
motor_angle = 0

preactivate() # only on raspberry

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
    date = datetime.datetime.now(datetime.timezone.utc).astimezone()
    solpos = solarposition.get_solarposition(date, lat, lon)
    rain_dtc = rain()
    wind_speed = None
    while wind_speed is None:
        try:
            wind_speed = windSpeed()
            print(wind_speed)
            time.sleep(0.5)
        except:
            pass

    if angle > 180:
        rain_angle = 189
    else:
        rain_angle = 171
    
    if rain_dtc == 0:
        if wind_speed <= 1.5:
            if angle > rain_angle:
                move_reverse(tolerance_angle * reductor_point * int((angle - rain_angle) / tolerance_angle))
                motor_angle = motor_angle - tolerance_angle * reductor_point * int((angle - rain_angle) / tolerance_angle)
                angle_difference = np.round(tolerance_angle * int((angle - rain_angle) / tolerance_angle), 6)
                angle = np.round(angle - angle_difference, 6)
                print("moved reverse: " + str(-tolerance_angle * reductor_point * int((angle - rain_angle) / tolerance_angle)))
                print("date: " + str(date))
                print("angle: " + str(angle))
                print("altitude: " + str(tracker_angle))
                print("motor angle: " + str(motor_angle))
                print("*****************")

            elif angle < rain_angle:
                move_forward(tolerance_angle * reductor_point * int((rain_angle - angle) / tolerance_angle))
                motor_angle = motor_angle + tolerance_angle * reductor_point * int((rain_angle - angle) / tolerance_angle)
                angle_difference = np.round(tolerance_angle * int((rain_angle - angle) / tolerance_angle), 6)
                angle = np.round(angle + angle_difference, 6)
                print("moved forward: " + str(tolerance_angle * reductor_point * int((rain_angle - angle) / tolerance_angle)))
                print("date: " + str(date))
                print("angle: " + str(angle))
                print("altitude: " + str(tracker_angle))
                print("motor angle: " + str(motor_angle))
                print("*****************")

    elif wind_speed > 1.5:
        if angle > 180:
            move_reverse(tolerance_angle * reductor_point * int((angle - 180) / tolerance_angle))
            motor_angle = motor_angle - tolerance_angle * reductor_point * int((angle - 180) / tolerance_angle)
            angle_difference = np.round(tolerance_angle * int((angle - 180) / tolerance_angle), 6)
            angle = np.round(angle - angle_difference, 6)
            print("moved reverse: " + str(-tolerance_angle * reductor_point * int((angle - 180) / tolerance_angle)))
            print("date: " + str(date))
            print("angle: " + str(angle))
            print("altitude: " + str(tracker_angle))
            print("motor_angle: " + str(motor_angle))
            print("*****************")

        elif angle < 180:
            move_forward(tolerance_angle * reductor_point * int((180 - angle) / tolerance_angle))
            motor_angle = motor_angle + tolerance_angle * reductor_point * int((180 - angle) / tolerance_angle)
            angle_difference = np.round(tolerance_angle * int((180 - angle) / tolerance_angle), 6)
            angle = np.round(angle + angle_difference, 6)
            print("moved forward: " + str(tolerance_angle * reductor_point * int((180 - angle) / tolerance_angle)))
            print("date: " + str(date))
            print("angle: " + str(angle))
            print("altitude: " + str(tracker_angle))
            print("motor_angle: " + str(motor_angle))
            print("*****************")
        elif angle == 0:
            pass

    else:
        truetracking_angles = tracking.singleaxis(
            apparent_zenith=solpos['apparent_zenith'],
            apparent_azimuth=solpos['azimuth'],
            axis_tilt=0,
            axis_azimuth=180,
            max_angle=90,
            backtrack=False,  # for true-tracking
            gcr=0.5)  # irrelevant for true-tracking

        tracker_angle = 180 + truetracking_angles.loc[date]['tracker_theta']

        if tracker_angle - angle > tolerance_angle:
            move_forward(tolerance_angle * reductor_point * int((tracker_angle - angle) / tolerance_angle))  # only on raspberry
            print("moved forward: " + str(tolerance_angle * reductor_point * int((tracker_angle - angle) / tolerance_angle)))
            print("date: " + str(date))
            motor_angle = motor_angle + tolerance_angle * reductor_point * int((tracker_angle - angle) / tolerance_angle)
            angle_difference = np.round(tolerance_angle * int((tracker_angle - angle) / tolerance_angle), 6)
            angle = np.round(angle + angle_difference, 6)
            print("angle: " + str(angle))
            print("altitude: " + str(tracker_angle))
            print("motor angle: " + str(motor_angle))
            print("*****************")

        if char == "x":
            move_reverse(angle * reductor_point)
            motor_angle = motor_angle - np.round(angle, 6) * reductor_point
            print("motor_angle: " + str(motor_angle))
            # Program will cease all GPIO activity before terminating
            io.cleanup()  #only on raspberry
            print("Program Ended")
            break

        char = ""
    wind_speed = None
