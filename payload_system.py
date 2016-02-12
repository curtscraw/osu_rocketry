import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.UART as UART
import BMP180

from time import sleep
from system import exit

#general needed values
CUTTER_PIN = "P9_12"
TRX_DEVICE = "/dev/ttyO1"
POWER_ON_ALT = 70   #altitude in meters of power on
CHUTE_DEPLOY = 160  #altitude to deploy main chute at
MIN_ALT	     = 300  #target minimum altitude before coming back down

#setup the gps and transmitter uart ports
UART.setup("UART1")
UART.setup("UART2")

#initialize the cutter pin, it is triggered on a high signal
GPIO.setup(CUTTER_PIN, GPIO.OUT)
GPIO.output(CUTTER_PIN, GPIO.LOW)

#setup gyro and altimeter
alt = BMP180.BMP180(POWER_ON_ALT)
motion = LSM9DS0.LSM9DS0()

#open a log file
f_log = open('/home/osu_rocketry/alt_log.out', 'a')

f_log.write("starting a full test")

start_cut = 0
arm_cutter = 0

while not start_cut:
  elev_agl = alt.read_agl()
  val = (elev_agl, arm_cutter, start_cut)
  s = str(val)
  f_log.write(s)
  if elev_agl > min_alt:
    arm_cutter = 1
  if arm_cutter and not start_cut:
    if elev_agl <= CHUTE_DEPLOY:
      start_cut = 1
      f_log.write("cutter going to fire")
      GPIO.output(CUTTER_PIN, GPIO.HIGH)
      f_log.write("output pin is high, waiting 2 second")
      sleep(2)


#make it keep printing data!!!!!!!!

GPIO.cleanup()
f_log.close()

exit()
