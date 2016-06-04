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

#DETERMINES if payload or nosecone
PAYLOAD = 1

#general needed values
X_MAG_ARR_LEN = 120
CUTTER_PIN = "P9_12"
SERVO_PIN_L = "P8_13"
SERVO_PIN_R = "P9_14"
TRX_DEVICE = "/dev/ttyO1"
#These are the important values to change for every flight!!
POWER_ON_ALT = 1414   #altitude in meters of power on
CHUTE_DEPLOY = 1350  #altitude to deploy main chute at
MIN_ALT	     = 2100  #target minimum altitude before coming back down
DEST_LAT     = 43.79558
DEST_LONG    = -120.6501


ERROR_LOG = '/home/osu_rocketry/payload_error.log'
DATA_LOG = '/home/osu_rocketry/payload_data.log'
GPS_LOG = '/home/osu_rocketry/payload_gps.log'


#states for nav
STRAIGHT = 1
TURNLEFT = 2
TURNRIGHT = 3
LANDING = 4

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
dict = {'time': 0, 'agl': 0, 'temp': 0, 'a_x': 0, 'a_y': 0, 'a_z': 0, 'g_x': 0, 'g_y': 0, 'g_z': 0, 'gps_fix': 0, 'lat': 0, 'long': 0, 'arm_cut': 0, 'start_cut': 0, 'xbee_errors': 0, 'm_x': 0, 'm_y': 0, 'm_z': 0, 'state': 0, 'track': 0, 'speed': 0, 'agl_avg': 0}

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
      dict['track'] = session.fix.track
      dict['speed'] = session.fix.speed
      dict['gps_time']  = session.fix.time
      log.write(str(gps_report) + "\n")
    else:
      if (not dict['gps_fix'] == 0):
	dict['gps_fix'] = 0
    
    sleep(1)
  
def nav_th():
   #activate the cutter
   GPIO.output(CUTTER_PIN, GPIO.HIGH)
   sleep(1) 
   GPIO.output(CUTTER_PIN, GPIO.LOW)

   #wait, and then start navigating the thing!
   sleep(2)

   #initialize servos
   servo_r = TGY6114MD.TGY6114MD_SERVO(SERVO_PIN_R)
   servo_l = TGY6114MD.TGY6114MD_SERVO(SERVO_PIN_L)
   #state and direction variables
   state = STRAIGHT
   #servo angle set to midde
   r_angle = 1080
   l_angle = 1080
   #holds last 20 gps hits
   left_flag = 0
   right_flag = 0
   for i in range(40):
      lat_array.append(0)
      long_array.append(0)
   #print 'starting nav'
   #dict['direction'] = direction
   dict['state'] = state
   while True:
      if dict['gps_fix'] == 1:
         #print "We have a fix!"     
         while True:
            #GPS UPDATING
            dict['state'] = state
            if dict['agl_avg'] < 45:
               state = LANDING
               l_angle = 1080
               r_angle = 1080

            long_sub = dict['long']-DEST_LONG
            lat_sub = dict['lat']-DEST_LAT
            angle_to_dest = math.tan(lat_sub/long_sub)
            if (state != LANDING)
               #QUAD 1
               if(lat_sub > 0 and long_sub > 0):
                  if(dict['track'] < angle_to_dest or dict['track'] > (angle_to_dest + 180)):
                     state = TURNLEFT
                  else:
                     state = TURNRIGHT
               #QUAD 2
               elif(lat_sub < 0 and long_sub > 0):
                  if(dict['track'] < (180 - angle_to_dest) or dict['track'] > (360 - angle_to_dest)):
                     state = TURNRIGHT
                  else:
                     state = TURNLEFT

               #QUAD 3
               elif(lat_sub < 0 and long_sub < 0):
                  if(dict['track'] < angle_to_dest or dict['track'] > (angle_to_dest + 180)):
                     state = TURNRIGHT
                  else:
                     state = TURNLEFT

               #QUAD 4
               elif(lat_sub > 0 and long_sub < 0):
                  if(dict['track'] < (180 - angle_to_dest) or dict['track'] > (360 - angle_to_dest)):
                     state = TURNLEFT
                  else:
                     state = TURNRIGHT

            if state == TURNLEFT:
               if left_flag == 0:
                  right_flag = 0
                  left_flag = 1
                  l_angle += 30
                  r_angle -= 30
                  end = time.time() + 2
               if time.time() > end:
                  end = time.time() + 2
                  l_angle += 30
                  r_angle -= 30
                  #print "more left"
               

            elif state == TURNRIGHT:
               if right_flag == 0:
                  right_flag = 1
                  left_flag = 0
                  r_angle += 30
                  l_angle -= 30
                  end = time.time() + 2
               if time.time() > end:
                  end = time.time() + 2
                  r_angle += 30
                  l_angle -= 30
                  #print "MORE RIGHT"
                  
            elif state == STRAIGHT:
               r_angle = 1080
               l_angle = 1080
                     
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
            servo_l.set_angle(l_angle)
            servo_r.set_angle(r_angle)
                  


#def log_th():
  #open a log file
  #f_log = open(DATA_LOG, 'a')
  #f_log.write("starting log\n")
  
  #while True:
    #f_log.write(str(dict) + "\n")
    
    #sleep(.05)

def poll_th():
  #data polling thread is main thread
  #setup gyro and altimeter
  alt = BMP180.BMP180(POWER_ON_ALT)
  gyro = LSM9DS0.LSM9DS0_GYRO(LSM9DS0.LSM9DS0_GYRODR_95HZ | LSM9DS0.LSM9DS0_GYRO_CUTOFF_1, LSM9DS0.LSM9DS0_GYROSCALE_2000DPS)
  accel = LSM9DS0.LSM9DS0_ACCEL()
  
  f_log = open(DATA_LOG, 'a')
  f_log.write("starting log\n")
  
  agl_arr = [0] * 10
  i = 0
  
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
      dict['agl'] = round(alt.read_agl(), 2)
      dict['temp'] = alt.read_temperature()
      
      #act on altimeter, in case accel fails in some way
      agl_arr[i] = dict['agl']
      agl_avg = sum(agl_arr)/10
      dict['agl_avg'] = agl_avg
      i += 1
      if i == 10:
        i = 0

      if PAYLOAD == 1:
         if (agl_avg > MIN_ALT) and (not dict['arm_cut']):
           dict['arm_cut'] = 1
           f_log.write("armed cutter\n")
         if dict['arm_cut'] and (not dict['start_cut']):
           if agl_avg <= CHUTE_DEPLOY:
             dict['start_cut'] = 1
             start_new_thread(nav_th, ())
     
      (x, y, z) = accel.read_accel()
      dict['a_x'] = round(x, 5)
      dict['a_y'] = round(y, 5)
      dict['a_z'] = round(z, 5)
  
      (x, y, z) = gyro.read()
      dict['g_x'] = round(x, 5)
      dict['g_y'] = round(y, 5)
      dict['g_z'] = round(z, 5)

      (x, y, z) = accel.read_magnetometer()
      dict['m_x'] = round(x, 5)
      dict['m_y'] = round(y, 5)
      dict['m_z'] = round(z, 5)
      #dict['new_dat_flag'] = 1
    
      f_log.write(str(dict) + "\n")
      #f_log.write("track:" + str(dict['track']) + "   speed:" + str(dict['speed']) + "\n")

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
