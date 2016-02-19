import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.UART as UART
import BMP180
import LSM9DS0
import datetime
import serial

from time import sleep
from sys import exit

global dict = {'time': datetime.datetime.utcnow(), 'agl': 0, 'temp': 0, 'a_x': 0, 'a_y': 0, 'a_z': 0, 'g_x': 0, 'g_y': 0, 'g_z': 0, 'arm_cut': 0, 'start_cut': 0, 'xbee_errors': ' '};

#general needed values
CUTTER_PIN = "P9_12"
TRX_DEVICE = "/dev/ttyO1"
POWER_ON_ALT = 79   #altitude in meters of power on
CHUTE_DEPLOY = 330  #altitude to deploy main chute at
MIN_ALT	     = 800  #target minimum altitude before coming back down

#setup the gps and transmitter uart ports
UART.setup("UART1")
UART.setup("UART2")

#initialize the cutter pin, it is triggered on a high signal
GPIO.setup(CUTTER_PIN, GPIO.OUT)
GPIO.output(CUTTER_PIN, GPIO.LOW)

#setup gyro and altimeter
alt = BMP180.BMP180(POWER_ON_ALT)
#motion = LSM9DS0.LSM9DS0()
gyro = LSM9DS0.LSM9DS0_GYRO(LSM9DS0.LSM9DS0_GYRODR_95HZ | LSM9DS0.LSM9DS0_GYRO_CUTOFF_1, LSM9DS0.LSM9DS0_GYROSCALE_2000DPS)
accel = LSM9DS0.LSM9DS0_ACCEL()

#xbee initialization
xbee = serial.Serial('/dev/ttyO1', 19200);

xbee.write("payload system started\n")

#open a log file
f_log = open('/home/osu_rocketry/alt_log.out', 'a')
#f_log.seek(0)
f_log.write("\n")
f_log.write("starting a full test")

last_measure = POWER_ON_ALT

while True:
  try:
    dict['time'] = datetime.datetime.utcnow()
    dict['agl'] = alt.read_agl()
    dict['temp'] = alt.read_temperature()
    
    (x, y, z) = accel.read_accel()
    dict['a_x'] = x
    dict['a_y'] = y
    dict['a_z'] = z

    (x, y, z) = gyro.read()
    dict['g_x'] = x
    dict['g_y'] = y
    dict['g_z'] = z

    f_log.write(str(dict) + "\n")
    xbee.write(str(dict) + "\n")

    if dict['agl'] > MIN_ALT and last_measure > MIN_ALT:
      dict['arm_cut'] = 1
      f_log.write("armed cutter\n")
    if dict['arm_cut'] and not dict['start_cut']:
      if dict['agl'] <= CHUTE_DEPLOY and last_measure <= CHUTE_DEPLOY:
        dict['start_cut'] = 1
        f_log.write("cutter going to fire \n")
        GPIO.output(CUTTER_PIN, GPIO.HIGH)
        f_log.write("output pin is high, waiting 1 second\n")
        sleep(1) 
        GPIO.output(CUTTER_PIN, GPIO.LOW)
    last_measure = dict['agl']

    sleep(1)
    dict['xbee_errors'] = ""

  except IOError:
    try:
      f_log.write("io error raised\n")
      dict['xbee_errors'] += "io error raised\n"
      
      alt = BMP180.BMP180(last_measure)
      accel = LSM9DS0.LSM9DS0_ACCEL()
      gyro = LSM9DS0.LSM9DS0_GYRO(LSM9DS0.LSM9DS0_GYRODR_95HZ | LSM9DS0.LSM9DS0_GYRO_CUTOFF_1, LSM9DS0.LSM9DS0_GYROSCALE_2000DPS)
    except:
      f_log.write("sensor errors \n")
      dict['xbee_errors'] += "io error raised again\n"


f_log.write("Script exited\n")
xbee.write("script exited\n")

exit()
