import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.UART as UART
import BMP180
import LSM9DS0
import datetime
import serial

from time import sleep
from sys import exit

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

start_cut = 0
arm_cutter = 0
last_measure = 0
i = 0

while True:
  try:
    s = str(datetime.datetime.utcnow()) + str(i) + "\n"
    f_log.write(s)
    xbee.write(s)

    elev_agl = alt.read_agl()
    s = "alt agl\n"
    f_log.write(s)
    xbee.write(s)

    s = str(elev_agl) + "\n"
    f_log.write(s)
    xbee.write(s)
    val = (arm_cutter, start_cut)
    s = str(val) + "\n"
    f_log.write(s)
    xbee.write(s)

    (a_x, a_y, a_z) = accel.read_accel()
    f_log.write("accel data\n")
    xbee.write("accel data\n")
    f_log.write("x " + str(a_x) + "\n")
    f_log.write("y " + str(a_y) + "\n")
    f_log.write("z " + str(a_z) + "\n")
    xbee.write("x " + str(a_x) + "\n")
    xbee.write("y " + str(a_y) + "\n")
    xbee.write("z " + str(a_z) + "\n")

    (g_x, g_y, g_z) = gyro.read()
    f_log.write("gyro data \n")
    f_log.write("x " + str(g_x) + "\n")
    f_log.write("y " + str(g_y) + "\n")
    f_log.write("z " + str(g_z) + "\n")
    xbee.write("gyro data \n")
    xbee.write("x " + str(g_x) + "\n")
    xbee.write("y " + str(g_y) + "\n")
    xbee.write("z " + str(g_z) + "\n")

    f_log.write("temp \n")
    s = str(alt.read_temperature()) + "\n"
    f_log.write(s)
    xbee.write("temp \n")
    xbee.write(s)


    if elev_agl > MIN_ALT and last_measure > MIN_ALT:
      arm_cutter = 1
      f_log.write("armed cutter\n")
      xbee.write("armed cutter\n")
    if arm_cutter and not start_cut:
      if elev_agl <= CHUTE_DEPLOY and last_measure <= CHUTE_DEPLOY:
        start_cut = 1
        f_log.write("cutter going to fire \n")
        xbee.write("cutter going to fire \n")
        GPIO.output(CUTTER_PIN, GPIO.HIGH)
        f_log.write("output pin is high, waiting 1 second\n")
        xbee.write("output pin is high, waiting 1 second\n")
        sleep(1) 
        GPIO.output(CUTTER_PIN, GPIO.LOW)
    last_measure = elev_agl
    i += 1
    f_log.write("\n")
    f_log.write("\n")
    xbee.write("\n")
    xbee.write("\n")

    sleep(0.1)

  except IOError:
    try:
      f_log.write("io error raised\n")
      xbee.write("io error raised\n")
      alt = BMP180.BMP180(last_measure)
      accel = LSM9DS0.LSM9DS0_ACCEL()
      gyro = LSM9DS0.LSM9DS0_GYRO(LSM9DS0.LSM9DS0_GYRODR_95HZ | LSM9DS0.LSM9DS0_GYRO_CUTOFF_1, LSM9DS0.LSM9DS0_GYROSCALE_2000DPS)
    except:
      f_log.write("sensor errors \n")
      xbee.write("sensor errors \n")


f_log.write("Script exited\n")
xbee.write("script exited\n")

exit()
