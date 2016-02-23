import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.UART as UART
import gps
import BMP180
import LSM9DS0
import datetime
import serial

from time import sleep
from sys import exit
import subprocess

from thread import start_new_thread, allocate_lock

import logging

#general needed values
TRX_DEVICE = "/dev/ttyO1"
POWER_ON_ALT = 79   #altitude in meters of power on
ERROR_LOG = '/home/osu_rocketry/avionics_error.log'
DATA_LOG = '/home/osu_rocketry/avionics_data.log'
GPS_LOG = '/home/osu_rocketry/avionics_gps.log'

logging.basicConfig(filename=ERROR_LOG,level=logging.DEBUG,)

#setup the gps and transmitter uart ports
UART.setup("UART1")
UART.setup("UART2")

trx_data = {'time': 0, 'avionics': 1, 'agl': 0, 'temp': 0, 'a_x': 0, 'a_y': 0, 'a_z': 0, 'g_x': 0, 'g_y': 0, 'g_z': 0, 'gps_fix': 0, 'lat': 0, 'long': 0, 'xbee_errors': 0}

gps_report = 0

error_trace = '' 

err_lock = allocate_lock()

def xbee_th():
  #xbee initialization
  xbee = serial.Serial('/dev/ttyO1', 19200);
  
  xbee.write("avionics system started\n\r")

  while True:
    xbee.write(str(trx_data) + "\n\r")

    #if errors were noted, clear them after printing
    if trx_data['xbee_errors']:
      err_lock.acquire()
      xbee.write(error_trace + "\n\r")
      trx_data['xbee_errors'] = 0
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
      if (not trx_data['gps_fix'] == 1):
	trx_data['gps_fix'] = 1

      trx_data['lat'] = session.fix.latitude
      trx_data['long'] = session.fix.longitude
      trx_data['gps_time']  = session.fix.utc
      log.write(str(gps_report))
    else:
      if (not trx_data['gps_fix'] == 0):
	trx_data['gps_fix'] = 0
    
    sleep(1)
  
def log_th():
  #open a log file
  f_log = open(DATA_LOG, 'a')
  f_log.write("starting log\n\r")
  
  while True:
    f_log.write(str(trx_data) + "\n\r")
    
    #sleep(.05)

def poll_th():
  #data polling thread is main thread
  #setup gyro and altimeter
  alt = BMP180.BMP180(POWER_ON_ALT)
  #motion = LSM9DS0.LSM9DS0()
  gyro = LSM9DS0.LSM9DS0_GYRO(LSM9DS0.LSM9DS0_GYRODR_95HZ | LSM9DS0.LSM9DS0_GYRO_CUTOFF_1, LSM9DS0.LSM9DS0_GYROSCALE_2000DPS)
  accel = LSM9DS0.LSM9DS0_ACCEL()
  
  #sensor are up, start the xbee and gps threads
  start_new_thread(xbee_th, ())
  start_new_thread(gps_th, ())
  
  while True:
    try:
      trx_data['time'] = datetime.datetime.utcnow()
      trx_data['agl'] = alt.read_agl()
      trx_data['temp'] = alt.read_temperature()
      
      (x, y, z) = accel.read_accel()
      trx_data['a_x'] = x
      trx_data['a_y'] = y
      trx_data['a_z'] = z
  
      (x, y, z) = gyro.read()
      trx_data['g_x'] = x
      trx_data['g_y'] = y
      trx_data['g_z'] = z
  
  
    except IOError as e:
      try:
        logging.exception('Got I2C exception on main handler' + str(trx_data['time']))
        
        err_lock.aqcuire()
        trx_data['xbee_errors'] += 1
        error_trace += e + '\n\r'
        err_lock.release()
  
        alt = BMP180.BMP180(trx_data['agl'])
        accel = LSM9DS0.LSM9DS0_ACCEL()
        gyro = LSM9DS0.LSM9DS0_GYRO(LSM9DS0.LSM9DS0_GYRODR_95HZ | LSM9DS0.LSM9DS0_GYRO_CUTOFF_1, LSM9DS0.LSM9DS0_GYROSCALE_2000DPS)
      except:
        logging.exception('Gotexception on recovery attempt')
  
        err_lock.aqcuire()
        trx_data['xbee_errors'] += 1
        error_trace += 'error in recovery attempt of ' + e + '\n\r'
        err_lock.release()
  
    except:
      logging.exception('Got an exception on main handler')


#start the whole system
poll_th()

logging.debug('script exited, not expected!')
