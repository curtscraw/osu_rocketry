#Python PWM class for the TGY-6114MD servo
#Based on code from Adafruit: https://learn.adafruit.com/downloads/pdf/controlling-a-servo-with-a-beaglebone-black.pdf

#dependencies of these classes
import Adafruit_BBIO.PWM as PWM

SERVO_PIN_L     = "P8_13"
SERVO_PIN_R     = "P8_19"
DUTY_MIN        = 3
DUTY_MAX        = 11.8
DUTY_SPAN       = DUTY_MAX - DUTY_MIN
INIT_ANGLE      = 1080

class TGY6114MD_SERVO:
    #setup the servo
    def __init__(self, dir=right):
        #Configure servo motor
        self._config_servo(dir)
        self.set()

    def _confiig_servo(self, dir):
        #detirmine side of servo
        if (dir == right):
            self._pin = SERVO_PIN_R
        elif (dir == left):
            self._pin = SERVO_PIN_L
        else:
            self._pin = -1

        if (self._pin != -1):
            PWM.start(self._pin, (100-DUTY_MIN), 60.0, 1)

    #set servo to specific angle
    #default to initial angle
    def set(self, angle=INIT_ANGLE):
        self._angle_f = float(angle)
        duty = -.0031224786 * self._angle_f + 94.91467692   #magic numbers for TGY-6114MD
        PWM.set_duty_cycle(self._pin, duty)                 #found by linear regression

    #reel the line in (for use in a negative feedback loop)
    def reel_in(self):
        self._angle_f = self._angle_f + 1.0
        duty = -.0031224786 * self._angle_f + 94.91467692   #magic numbers for TGY-6114MD
        PWM.set_duty_cycle(self._pin, duty)                 #found by linear regression

    #reel the line out (for use in a negative feedback loop)
    def reel_out(self):
        self._angle_f = self._angle_f - 1.0
        duty = -.0031224786 * self._angle_f + 94.91467692   #magic numbers for TGY-6114MD
        PWM.set_duty_cycle(self._pin, duty)                 #found by linear regression

    #stop servo and clean up
    def stop(self):
        PWM.stop(self._pin)
        PWM.cleanup()
