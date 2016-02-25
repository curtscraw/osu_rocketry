#Python PWM class for the TGY-6114MD servo
#Based on code from Adafruit: 
#https://learn.adafruit.com/downloads/pdf/controlling-a-servo-with-a-beaglebone-black.pdf

#dependencies of these classes
import Adafruit_BBIO.PWM as PWM
from math import pi 

DUTY_MIN            = 3
DUTY_MAX            = 11.8
DUTY_SPAN           = DUTY_MAX - DUTY_MIN
INIT_ANGLE          = 1080
ANGLE_MAX           = 2160
ANGLE_MIN           = 0
PULLEY_DIAMETER_IN  = 1.0
INIT_LENGTH         = INIT_ANGLE/360 * PULLEY_DIAMETER_IN * pi

class TGY6114MD_SERVO:
    #setup the servo
    def __init__(self, pin=-1):
        #Configure servo motor
        self._config_servo(pin)
        if (self._pin_set == True):
            self.set_angle()

    def _confiig_servo(self, pin):
        #detirmine side of servo
        if (pin != -1):
            self._pin = pin
            self._pin_set = True
            duty = -.0031224786 * INIT_ANGLE + 94.91467692   #magic numbers for TGY-6114MD
            PWM.start(self._pin, duty, 60.0, 1)
        else:
            self._pin = -1
            self._pin_set = False

    #set servo to specific angle
    #default to initial angle
    def set_angle(self, angle=INIT_ANGLE):
        if (angle < ANGLE_MAX and angle > ANGLE_MIN):
            self._angle = angle
            self._angle_f = float(angle)
            duty = -.0031224786 * self._angle_f + 94.91467692   #magic numbers for TGY-6114MD
            PWM.set_duty_cycle(self._pin, duty)                 #found by linear regression

    #set servo to specific length
    #default to initial length
    def set_length(self, length=INIT_LENGTH):
        angle = length/(PULLEY_DIAMETER_IN * pi) * 360
        self.set_angle(angle)

    #reel the line in (for use in a negative feedback loop)
    def reel_in(self, angle):
        if (self._angle + angle < ANGLE_MAX):
            self.set_angle(self._angle + angle)

    #reel the line out (for use in a negative feedback loop)
    def reel_out(self, angle):
        if (self._angle - angle > ANGLE_MIN):
            self.set_angle(self._angle - angle)

    #stop servo and clean up
    def stop(self):
        PWM.stop(self._pin)
        PWM.cleanup()
