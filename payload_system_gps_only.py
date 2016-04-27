import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.UART as UART
import gps
import BMP180
import LSM9DS0
import TGY6114MD
import datetime
import serial
import time
import math
from time import sleep
from sys import exit
import subprocess

from thread import start_new_thread, allocate_lock

import logging

#general needed values
X_MAG_ARR_LEN = 120
CUTTER_PIN = "P9_12"
SERVO_PIN_L = "P8_13"
SERVO_PIN_R = "P9_14"
TRX_DEVICE = "/dev/ttyO1"
#These are the important values to change for every flight!!
POWER_ON_ALT = 79   #altitude in meters of power on
#CHUTE_DEPLOY = 600  #altitude to deploy main chute at
#MIN_ALT	     = 900  #target minimum altitude before coming back down
CHUTE_DEPLOY = 100  #altitude to deploy main chute at
MIN_ALT	     = 200  #target minimum altitude before coming back down
DEST_LAT     = 44.5739
DEST_LONG    = -123.279277


ERROR_LOG = '/home/osu_rocketry/payload_error.log'
DATA_LOG = '/home/osu_rocketry/payload_data.log'
GPS_LOG = '/home/osu_rocketry/payload_gps.log'


#states for nav
ORIENT = 0
STRAIGHT = 1
TURN = 2
LANDING = 3

NORTH = 0
WEST = 1
SOUTH = 2
EAST = 3
NONE = 4


logging.basicConfig(filename=ERROR_LOG,level=logging.WARNING,)

#setup the gps and transmitter uart ports
UART.setup("UART1")
UART.setup("UART2")

#initialize the cutter pin, it is triggered on a high signal
GPIO.setup(CUTTER_PIN, GPIO.OUT)
GPIO.output(CUTTER_PIN, GPIO.LOW)


#Sorry Curtis
#I cant think of a more elegant way to add this flag
dict = {'time': 0, 'agl': 0, 'temp': 0, 'a_x': 0, 'a_y': 0, 'a_z': 0, 'g_x': 0, 'g_y': 0, 'g_z': 0, 'gps_fix': 0, 'lat': 0, 'long': 0, 'arm_cut': 0, 'start_cut': 0, 'xbee_errors': 0, 'm_x': 0, 'm_y': 0, 'm_z': 0, 'new_dat_flag': 0, 'direction': 0, 'state': 0}

error_trace = {'error': ' '}

global gps_report 

gps_report = 0

err_lock = allocate_lock()
  
subprocess.call("/home/osu_rocketry/gpsd_setup.sh", shell=True)
sleep(2)
subprocess.call("/home/osu_rocketry/gpsd_setup.sh", shell=True)

def xbee_th():
  #xbee initialization
  xbee = serial.Serial('/dev/ttyO1', 19200);
  
  xbee.write("payload system started\n")

  while True:
    xbee.write(str(dict) + "\n")

    #if errors were noted, clear them after printing
    if dict['xbee_errors']:
      err_lock.acquire()
      xbee.write(str(error_trace) + "\n")
      dict['xbee_errors'] = 0
      error_trace['error'] = ''
      err_lock.release()

    #tx 2 time per second
    sleep(.5)

  xbee.write("xbee transmission ending, not good!\n")
  xbee.close()

def gps_th():
  session = gps.gps("localhost", "2947")
  session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
  log = open(GPS_LOG, 'a')
  
  log.write("setup gps\n")
  
  #this ensures that the gpsd service is running
  #the gpsd service provides the python gps module with input from the physical module
  #gpsd must be configured using "gpsd -n /dev/ttyO2 -F var/run/gpsd.sock"
  #prior to running this code 
  try: 
    subprocess.check_output(["pgrep", "gpsd"]) 
  except subprocess.CalledProcessError: 
    #gpsd isn't running yet, start it up 
    subprocess.check_output(["systemctl", "start", "gpsd.service"]) 
  
  sleep(2)
  
  log.write("setup gpsd on uart2\n")
  subprocess.call("/home/osu_rocketry/gpsd_setup.sh", shell=True)
  sleep(2)
  subprocess.call("/home/osu_rocketry/gpsd_setup.sh", shell=True)
  sleep(2)
  subprocess.call("/home/osu_rocketry/gpsd_setup.sh", shell=True)
  sleep(2)
  
  err_lock.acquire()
  dict['xbee_errors'] += 1
  error_trace['error'] += 'gps started' + '\n'
  err_lock.release()
  
  while True:
    gps_report = session.next()
    #print "test"
    #log.write("test\n")
    if (session.fix.mode != 1):
      
      if (not dict['gps_fix'] == 1):
	dict['gps_fix'] = 1

      dict['lat'] = session.fix.latitude
      dict['long'] = session.fix.longitude
      dict['gps_time']  = session.fix.time
      log.write(str(gps_report) + "\n")
    else:
      if (not dict['gps_fix'] == 0):
	dict['gps_fix'] = 0
    
    sleep(1)
  
def nav_th():
   #activate the cutter
   #GPIO.output(CUTTER_PIN, GPIO.HIGH)
   #sleep(1) 
   #GPIO.output(CUTTER_PIN, GPIO.LOW)

   #wait, and then start navigating the thing!
   #sleep(2)

   #initialize servos
   #servo_r = TGY6114MD.TGY6114MD_SERVO(SERVO_PIN_R)
   #servo_l = TGY6114MD.TGY6114MD_SERVO(SERVO_PIN_L)
   #state and direction variables
   state = OREINT
   print state
   direction = NONE
   #servo angle set to midde
   r_angle = 1080
   l_angle = 1080
   #holds last 20 gps hits
   lat_array = []
   long_array = []
   long_dir = NONE
   lat_dir = NONE
   for i in range(20):
      lat_array.append = 0
      long_array.append = 0
   print 'starting nav'
   dict['direction'] = direction
   dict['state'] = state
   if dict['gps_fix'] == 1:
   #navigate based on dict: gps_fix, lat, long
   #navigate based on report: gps_report
      if dict['lat'] > DEST_LAT:
         go = NORTH
      else:
         go = SOUTH
         
      while True:
         #GPS UPDATING
        #if dict['agl'] < 30:
           # state = LANDING
           # l_angle = 1080
           # r_angle = 1080
         sleep(1)
         if lat_array != dict['lat'] or long_array != dict['long']:
            for i in range(19):
               lat_array[i+1] =lat_array[i]
               long_array[i+1] =long_array[i]
            lat_array[0] = dict['lat']
            long_array[0] = dict['long']
            sum_lat = 0
            sum_long = 0
            sum_lat2 = 0
            sum_long2 = 0
            for i in range(10):
               sum_lat += lat_array[i]
               sum_long += long_array[i]
               sum_lat2 += lat_array[i+10]
               sum_long2 += long_array[i+10]
            if sum_lat <= sum_lat2 and sum_long <= sum_long2:
               lat_dir = SOUTH
               long_dir = WEST
            elif sum_lat >= sum_lat2 and sum_long >= sum_long2:
               lat_dir = NORTH
               long_dir = EAST
            elif sum_lat > sum_lat2 and sum_long < sum_long2:
               lat_dir = NORTH
               long_dir = WEST
            elif sum_lat < sum_lat2 and sum_long > sum_long2:
               lat_dir = SOUTH
               long_dir = EAST
            
            
            if state == ORIENT:
               if lat_array[19] != 0:
                  if lat_dir == go:
                     state = STRAIGHT
                     long_hold = long_array[0]
                     print "going straight"
                     print go
                  else:
                     state = TURNAROUND
                     print "Turnaround"
                     
            elif state == STRAIGHT:
               if go == NORTH:
                  if long_hold < long_array[0]:
                     print "left"
                     l_angle += 5
                     r_angle -= 5
                  else:
                     print "right"
                     l_angle -= 5
                     r_angle += 5
               if go == SOUTH:
                  if long_hold > long_array[0]:
                     print "left"
                     l_angle += 5
                     r_angle -= 5
                  else:
                     print "right"
                     l_angle -= 5
                     r_angle += 5
                     
               if go == EAST:
                  if lat_hold > lat_array[0]:
                     print "left"
                     l_angle += 5
                     r_angle -= 5
                  else:
                     print "right"
                     l_angle -= 5
                     r_angle += 5
               if go == WEST:
                  if lat_hold < lat_array[0]:
                     print "left"
                     l_angle += 5
                     r_angle -= 5
                  else:
                     print "right"
                     l_angle -= 5
                     r_angle += 5
               if (go == NORTH or go == SOUTH) and abs(DEST_LAT - array_lat[0]) < .0001:
                  state = STRAIGHT
                  
                  if DEST_LONG - array_lat[0] > 0:
                     print "Time to go west"
                     go = WEST
                     hold_lat = DEST_LAT
                  else:
                     print "Time to go east"
                     go = EAST
                     hold_lat = DEST_LAT
               elif (go == EAST or go == WEST) and abs(DEST_LONG - array_long[0]) < .0001:
                  #SHOULD BE DONE...?
                  state = HOLDTURN
                  print "DONE...Hold turn"
                     
            elif state == TURNAROUND:
               if (go == NORTH and long_dir == EAST) or (go == SOUTH and long_dir == WEST):
                  r_angle = 1180
                  l_angle = 1080
                  print "right turn turnaround"
               else:
                  l_angle = 1180
                  r_angle = 1080
                  print "left turn turnaround"
               if go == lat_dir:
                  state = STRAIGHT
                  print "going straight from turnaround..."
                  print go
                  hold_long = long_array[0]
                  
         
            elif state == HOLDTURN:
               r_angle = 1080
               l_angle = 1180
            elif state == LANDING:
               if dict['agl'] < 15:
                  servo_l.set_angle(2160)
                  servo_r.set_angle(2160)
                  
            if r_angle > 1260:
                  r_angle = 1260
            if l_angle > 1260:
              l_angle = 1260
            if r_angle < 1080:
               r_angle = 1080
            if l_angle < 1080:
               l_angle = 1080
            #servo_l.set_angle(l_angle)
            #servo_r.set_angle(r_angle)
                  


def log_th():
  #open a log file
  f_log = open(DATA_LOG, 'a')
  f_log.write("starting log\n")
  
  while True:
    f_log.write(str(dict) + "\n")
    
    #sleep(.05)

def poll_th():
  #data polling thread is main thread
  #setup gyro and altimeter
  alt = BMP180.BMP180(POWER_ON_ALT)
  #motion = LSM9DS0.LSM9DS0()
  gyro = LSM9DS0.LSM9DS0_GYRO(LSM9DS0.LSM9DS0_GYRODR_95HZ | LSM9DS0.LSM9DS0_GYRO_CUTOFF_1, LSM9DS0.LSM9DS0_GYROSCALE_2000DPS)
  accel = LSM9DS0.LSM9DS0_ACCEL()
  
  f_log = open(DATA_LOG, 'a')
  f_log.write("starting log\n")
  
  last_measure = POWER_ON_ALT
  
  #sensor are up, start the xbee and gps threads
  start_new_thread(xbee_th, ())
  start_new_thread(gps_th, ())
  #start_new_thread(log_th, ())
  #for servo testing
  #remove this part after testing
  #TODO
  #start_new_thread(nav_th, ())
  
  while True:
    try:
      dict['time'] = datetime.datetime.utcnow()
      temp_agl = alt.read_agl()
      if abs(dict['agl'] - last_measure) < 60:
         dict['agl'] = temp_agl
      dict['temp'] = alt.read_temperature()
      
      #act on altimeter, in case accel fails in some way
      if (dict['agl'] > MIN_ALT) and (last_measure > MIN_ALT) and (not dict['arm_cut']):
        dict['arm_cut'] = 1
        f_log.write("armed cutter\n")
  
      if dict['arm_cut'] and (not dict['start_cut']):
        if dict['agl'] <= CHUTE_DEPLOY and last_measure <= CHUTE_DEPLOY:
          dict['start_cut'] = 1
	  start_new_thread(nav_th, ())
  
      last_measure = temp_agl
      
      (x, y, z) = accel.read_accel()
      dict['a_x'] = x
      dict['a_y'] = y
      dict['a_z'] = z
  
      (x, y, z) = gyro.read()
      dict['g_x'] = x
      dict['g_y'] = y
      dict['g_z'] = z

      (x, y, z) = accel.read_magnetometer()
      dict['m_x'] = x
      dict['m_y'] = y
      dict['m_z'] = z
      dict['new_dat_flag'] = 1
    
      f_log.write(str(dict) + "\n")

    except IOError as e:
      try:
        logging.exception('Got I2C exception on main handler' + str(dict['time']))
        
        err_lock.acquire()
        dict['xbee_errors'] += 1
        error_trace['error'] += e + '\n'
        err_lock.release()
  
        alt = BMP180.BMP180(last_measure)
        accel = LSM9DS0.LSM9DS0_ACCEL()
        gyro = LSM9DS0.LSM9DS0_GYRO()
      except:
        logging.exception('Gotexception on recovery attempt')
  
        err_lock.aqcuire()
        dict['xbee_errors'] += 1
        error_trace['error'] += 'error in recovery attempt of ' + e + '\n'
        err_lock.release()
    except KeyboardInterrupt:
      break
    except:
      logging.exception('Got an exception on main handler')


#start the whole system
poll_th()

logging.debug('script exited, not expected!')
