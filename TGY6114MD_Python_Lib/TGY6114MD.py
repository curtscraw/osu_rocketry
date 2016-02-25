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
        if (self.pin_set == True):
            self.set_angle()

    def _confiig_servo(self, pin):
        #detirmine side of servo
        if (pin != -1):
            self._pin = pin
            self.pin_set = True
            PWM.start(self._pin, (100-DUTY_MIN), 60.0, 1)
        else:
            self._pin = -1
            self.pin_set = False

    #set servo to specific angle
    #default to initial angle
    def set_angle(self, angle=INIT_ANGLE):
        if (angle < ANGLE_MAX and angle > ANGLE_MIN):
            self._angle_f = float(angle)
            duty = -.0031224786 * self._angle_f + 94.91467692   #magic numbers for TGY-6114MD
            PWM.start(self._pin, (100-DUTY_MIN), 60.0, 1)
            PWM.set_duty_cycle(self._pin, duty)                 #found by linear regression

    def set_length(self, length=INIT_LENGTH):
        angle = length/(PULLEY_DIAMETER_IN * pi) * 360
        if (angle < ANGLE_MAX and angle > ANGLE_MIN):
            self._angle_f = float(angle)
            duty = -.0031224786 * self._angle_f + 94.91467692   #magic numbers for TGY-6114MD
            PWM.set_duty_cycle(self._pin, duty)                 #found by linear regression


    #reel the line in (for use in a negative feedback loop)
    def reel_in(self):
        if (self._angle_f < ANGLE_MAX):
            self._angle_f = self._angle_f + 1.0
            duty = -.0031224786 * self._angle_f + 94.91467692   #magic numbers for TGY-6114MD
            PWM.set_duty_cycle(self._pin, duty)                 #found by linear regression

    #reel the line out (for use in a negative feedback loop)
    def reel_out(self):
        if (self._angle_f > ANGLE_MIN):
            self._angle_f = self._angle_f - 1.0
            duty = -.0031224786 * self._angle_f + 94.91467692   #magic numbers for TGY-6114MD
            PWM.set_duty_cycle(self._pin, duty)                 #found by linear regression

    #stop servo and clean up
    def stop(self):
        PWM.stop(self._pin)
        PWM.cleanup()
