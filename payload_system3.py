import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.UART as UART
import gps
import BMP180
import LSM9DS0
import TGY6114MD
import datetime
import serial

from time import sleep
from sys import exit
import subprocess

from thread import start_new_thread, allocate_lock

import logging

#general needed values
CUTTER_PIN = "P9_12"
SERVO_PIN_L = "P8_13"
SERVO_PIN_R = "P8_19"
TRX_DEVICE = "/dev/ttyO1"
POWER_ON_ALT = 79   #altitude in meters of power on
CHUTE_DEPLOY = 330  #altitude to deploy main chute at
MIN_ALT	     = 800  #target minimum altitude before coming back down
ERROR_LOG = '/home/osu_rocketry/payload_error.log'
DATA_LOG = '/home/osu_rocketry/payload_data.log'
GPS_LOG = '/home/osu_rocketry/payload_gps.log'

DEST_LAT = 0
DEST_LONG = 0

logging.basicConfig(filename=ERROR_LOG,level=logging.DEBUG,)

#setup the gps and transmitter uart ports
UART.setup("UART1")
UART.setup("UART2")

#initialize the cutter pin, it is triggered on a high signal
GPIO.setup(CUTTER_PIN, GPIO.OUT)
GPIO.output(CUTTER_PIN, GPIO.LOW)

#init pwm pins
#TODO

dict = {'time': 0, 'agl': 0, 'temp': 0, 'a_x': 0, 'a_y': 0, 'a_z': 0, 'g_x': 0, 'g_y': 0, 'g_z': 0, 'gps_fix': 0, 'lat': 0, 'long': 0, 'arm_cut': 0, 'start_cut': 0, 'xbee_errors': 0}

gps_report = 0

error_trace = '' 

err_lock = allocate_lock()

def xbee_th():
  #xbee initialization
  xbee = serial.Serial('/dev/ttyO1', 19200);
  
  xbee.write("payload system started\n\r")

  while True:
    xbee.write(str(dict) + "\n\r")

    #if errors were noted, clear them after printing
    if dict['xbee_errors']:
      err_lock.acquire()
      xbee.write(error_trace + "\n\r")
      dict['xbee_errors'] = 0
      error_trace = ''
      err_lock.release()

    #tx 2 time per second
    sleep(.5)

  xbee.write("xbee transmission ending, not good!\n")
  xbee.close()

def gps_th():
  session = gps.gps("localhost", "2947")
  session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
  log = open(GPS_LOG, 'a')
  
  
  #this ensures that the gpsd service is running
  #the gpsd service provides the python gps module with input from the physical module
  #gpsd must be configured using "gpsd -n /dev/ttyO1 -F var/run/gpsd.sock"
  #prior to running this code 
  try: 
    subprocess.check_output(["pgrep", "gpsd"]) 
  except subprocess.CalledProcessError: 
    #gpsd isn't running yet, start it up 
    subprocess.check_output(["systemctl", "start", "gpsd.service"]) 
  
  while True:
    gps_report = session.next()
    if (session.fix.mode != 1):
      if (not dict['gps_fix'] == 1):
	dict['gps_fix'] = 1

      dict['lat'] = session.fix.latitude
      dict['long'] = session.fix.longitude
      dict['gps_time']  = session.fix.utc
      log.write(str(gps_report))
    else:
      if (not dict['gps_fix'] == 0):
	dict['gps_fix'] = 0
    
    sleep(1)
  
def nav_th():
  #activate the cutter
  GPIO.output(CUTTER_PIN, GPIO.HIGH)
  sleep(1) 
  GPIO.output(CUTTER_PIN, GPIO.LOW)

  #initialize servos
  servo_r = TGY6114MD.TGY6114MD_SERVO(SERVO_PIN_R)
  servo_l = TGY6114MD.TGY6114MD_SERVO(SERVO_PIN_L)

  #wait, and then start navigating the thing!
  sleep(2)

  #navigate based on dict: gps_fix, lat, long
  #navigate based on report: gps_report 
  while True:
    while (dict['gps_fix'] == 0):
      #do gps fix, so do something simple
      #want to stop as soon as the gps has a fix though
      pass
    #navigate based on destination gps
    pass

def log_th():
  #open a log file
  f_log = open(DATA_LOG, 'a')
  f_log.write("starting log\n\r")
  
  while True:
    f_log.write(str(dict) + "\n\r")
    
    #sleep(.05)

def poll_th():
  #data polling thread is main thread
  #setup gyro and altimeter
  alt = BMP180.BMP180(POWER_ON_ALT)
  #motion = LSM9DS0.LSM9DS0()
  gyro = LSM9DS0.LSM9DS0_GYRO(LSM9DS0.LSM9DS0_GYRODR_95HZ | LSM9DS0.LSM9DS0_GYRO_CUTOFF_1, LSM9DS0.LSM9DS0_GYROSCALE_2000DPS)
  accel = LSM9DS0.LSM9DS0_ACCEL()
  
  last_measure = POWER_ON_ALT
  
  #sensor are up, start the xbee and gps threads
  start_new_thread(xbee_th, ())
  start_new_thread(gps_th, ())
  
  while True:
    try:
      dict['time'] = datetime.datetime.utcnow()
      dict['agl'] = alt.read_agl()
      dict['temp'] = alt.read_temperature()
      
      #act on altimeter, in case accel fails in some way
      if (dict['agl'] > MIN_ALT) and (last_measure > MIN_ALT) and (not dict['arm_cut']):
        dict['arm_cut'] = 1
        f_log.write("armed cutter\n\r")
  
      if dict['arm_cut'] and (not dict['start_cut']):
        if dict['agl'] <= CHUTE_DEPLOY and last_measure <= CHUTE_DEPLOY:
          dict['start_cut'] = 1
	  start_new_thread(nav_th, ())
  
      last_measure = dict['agl']
      
      (x, y, z) = accel.read_accel()
      dict['a_x'] = x
      dict['a_y'] = y
      dict['a_z'] = z
  
      (x, y, z) = gyro.read()
      dict['g_x'] = x
      dict['g_y'] = y
      dict['g_z'] = z
  
  
    except IOError as e:
      try:
        logging.exception('Got I2C exception on main handler' + str(dict['time']))
        
        err_lock.aqcuire()
        dict['xbee_errors'] += 1
        error_trace += e + '\n\r'
        err_lock.release()
  
        alt = BMP180.BMP180(last_measure)
        accel = LSM9DS0.LSM9DS0_ACCEL()
        gyro = LSM9DS0.LSM9DS0_GYRO(LSM9DS0.LSM9DS0_GYRODR_95HZ | LSM9DS0.LSM9DS0_GYRO_CUTOFF_1, LSM9DS0.LSM9DS0_GYROSCALE_2000DPS)
      except:
        logging.exception('Gotexception on recovery attempt')
  
        err_lock.aqcuire()
        dict['xbee_errors'] += 1
        error_trace += 'error in recovery attempt of ' + e + '\n\r'
        err_lock.release()
  
    except:
      logging.exception('Got an exception on main handler')


#start the whole system
poll_th()

logging.debug('script exited, not expected!')
