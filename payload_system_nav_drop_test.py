import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.UART as UART
import gps
import BMP180
import LSM9DS0
import TGY6114MD
import datetime
import serial
import time
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
POWER_ON_ALT = 79   #altitude in meters of power on
CHUTE_DEPLOY = 600  #altitude to deploy main chute at
MIN_ALT	     = 900  #target minimum altitude before coming back down
ERROR_LOG = '/home/osu_rocketry/payload_error.log'
DATA_LOG = '/home/osu_rocketry/payload_data.log'
GPS_LOG = '/home/osu_rocketry/payload_gps.log'

DEST_LAT = 0
DEST_LONG = 0

#states for nav
FIND_NORTH = 0
TURN = 1
STRAIGHT = 2
LANDING = 3

NORTH = 0
WEST = 1
SOUTH = 2
EAST = 3
NONE = 4
LEG_TIME = 7


logging.basicConfig(filename=ERROR_LOG,level=logging.WARNING,)

#setup the gps and transmitter uart ports
UART.setup("UART1")
UART.setup("UART2")

#initialize the cutter pin, it is triggered on a high signal
GPIO.setup(CUTTER_PIN, GPIO.OUT)
GPIO.output(CUTTER_PIN, GPIO.LOW)

#init pwm pins
#TODO

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
      #print "yaya"
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
   GPIO.output(CUTTER_PIN, GPIO.HIGH)
   sleep(1) 
   GPIO.output(CUTTER_PIN, GPIO.LOW)

   #wait, and then start navigating the thing!
   sleep(2)

   #initialize servos
   servo_r = TGY6114MD.TGY6114MD_SERVO(SERVO_PIN_R)
   servo_l = TGY6114MD.TGY6114MD_SERVO(SERVO_PIN_L)

   state = FIND_NORTH
   max_mag = dict['m_z']    #maximum magnetometer reading
   z_mag_array = [0] * 10     #array containing last 10 magnetometer readings in z-axis
   y_mag_array = [0] * 10     #array containing last 10 magnetometer readings in z-axis
   x_mag_array = [0] * X_MAG_ARR_LEN  #array containing last 2 seconds of x-axis magnetometer readings

   direction = NONE
   #navigate based on dict: gps_fix, lat, long
   #navigate based on report: gps_report 
   while True:
      #while (dict['gps_fix'] == 0):
      #servo_r.set_angle(1080)
      #sleep(5)
      #We need to figure out our orintation since strength of north changes everywhere
      dict['direction'] = direction
      dict['state'] = state
      if dict['agl'] < 90:
         state = LANDING
      #print dict['agl']
      if state == FIND_NORTH:
         #Left turn
         servo_l.set_angle(1170)
         if dict['new_dat_flag'] == 1:
            z_mag_array, y_mag_array = update_mag_array(z_mag_array, y_mag_array, x_mag_array)
            #Figure out if north of south
            #with a constant left turn, we will then see if we are east or west once we see a 0v
            count = 0
            #Use the last 10 datapoints to guaruntee we are north or south facing
            for j in range(10):
               if z_mag_array[j] > 0:
                  count += 1
               if z_mag_array[j] < 0:
                  count -= 1
            if count == 10:
               direction = SOUTH
               state = STRAIGHT
               #print "SOUTH-ISH"
            elif count == -10:
               direction = NORTH 
               state = STRAIGHT
               #print "NORTH-ISH"
      elif state == STRAIGHT:
         servo_l.set_angle(1080)
         #print "straight for 7 secs"
         #print "I think I am (0 north, 1 west, 2 south, 3 east):"
         #print direction
         #sleep(LEG_TIME)
         end = time.time() + 7
         r_angle = 1080
         l_angle = 1080
         while time.time() < end:
            #STRAIGHT CODE GOES HERE
            z_mag_array, y_mag_array = update_mag_array(z_mag_array, y_mag_array, x_mag_array)
            
            if direction == NORTH:
              
               if y_mag_array[9] < 0:
                  r_angle += 1
                  l_angle = 1080
               else
                  l_angle += 1
                  r_angle = 1080
                  
            elif direction == SOUTH:
               if y_mag_array[9] > 0:
                  r_angle += 1
                  l_angle = 1080
               else
                  l_angle += 1
                  r_angle = 1080
            elif direction == EAST:
               if z_mag_array[9] < 0:
                  r_angle -= 1
                  l_angle = 1080
               else
                  l_angle += 1
                  r_angle = 1080
            elif direction == WEST:
               if z_mag_array[9] > 0:
                  r_angle += 1
                  l_angle = 1080
               else
                  l_angle += 1
                  r_angle = 1080
                  
            if r_angle > 1170:
              r_angle = 1170
            if l_angle > 1170:
              l_angle = 1170
              
            servo_r.set_angle(r_angle)
            servo_l.set_angle(l_angle)
         state = TURN
      elif state == TURN:
         servo_l.set_angle(1170)
         z_mag_array, y_mag_array = update_mag_array(z_mag_array, y_mag_array, x_mag_array)
         count = 0
         if direction == SOUTH:
            for j in range(10):
               if z_mag_array[j] < 0:
                  count -= 1
            if count == -10:
               direction = EAST 
               state = STRAIGHT
         elif direction == NORTH:
            for j in range(10):
               if z_mag_array[j] > 0:
                  count += 1
            if count == 10:
               direction = WEST
               state = STRAIGHT
         elif direction == WEST:
            for j in range(10):
               if y_mag_array[j] < 0:
                  count += 1
            if count == 10:
             
            #new = mag_array[len(mag_array)/2:]
            #old = mag_array[:len(mag_array)/2]
            #if sum(new)/len(new) < sum(old)/len(old):
               #del mag_array[:]
               #mag_array = [0] * 20     #array containing last 10 magnetometer readings in z-axis
               direction = SOUTH
               state = STRAIGHT
         elif direction == EAST:
            for j in range(10):
               if y_mag_array[j] > 0:
                  count -= 1
            if count == -10:
             
            #new = mag_array[len(mag_array)/2:]
            #old = mag_array[:len(mag_array)/2]
            #if sum(new)/len(new) > sum(old)/len(old):
               #del mag_array[:]
               #mag_array = [0] * 20     #array containing last 10 magnetometer readings in z-axis
               direction = NORTH
               state = STRAIGHT   
      elif state == LANDING:
         servo_l.set_angle(1080)
         servo_r.set_angle(1080)
         #print "landing bitches"      
      #no gps fix, so do something simple
      #want to stop as soon as the gps has a fix though
      #pass
      #navigate based on destination gps
      pass

def update_mag_array(z_mag_array, y_mag_array, x_mag_array):
 #Fresh data
   if dict['new_dat_flag'] == 1: 
      #print "new data"
      #print dict['m_z']
      #print dict['m_y']
      dict['new_dat_flag'] = 0
      for i in range(1,X_MAG_ARR_LEN):
         x_mag_array[i-1] = x_mag_array[i]
         x_mag_array[X_MAG_ARR_LEN - 1] = dict['m_x']
      if check_data(x_mag_array):
         #max_mag = max(max_mag, dict['m_z'])
         #last 10 points of data
         #print "keeping data"
         for i in range(1,10):
            z_mag_array[i-1] = z_mag_array[i]
            z_mag_array[9] = dict['m_z']
            y_mag_array[i-1] = y_mag_array[i]
            y_mag_array[9] = dict['m_y']
   
   return z_mag_array, y_mag_array

def check_data(x_mag_array):
    x_avg = sum(x_mag_array)/len(x_mag_array)
    #print x_avg
    #print dict['m_x']
    if dict['m_x'] < x_avg * .92 and dict['m_x'] > x_avg * 1.08 and abs(dict['g_y']) < 70 and abs(dict['g_z']) < 70 and dict['g_x'] > -30:
        return True
    else:
        return False


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
      dict['agl'] = alt.read_agl()
      dict['temp'] = alt.read_temperature()
      
      #act on altimeter, in case accel fails in some way
      if (dict['agl'] > MIN_ALT) and (last_measure > MIN_ALT) and (not dict['arm_cut']):
        dict['arm_cut'] = 1
        f_log.write("armed cutter\n")
  
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

      (x, y, z) = accel.read_magnetometer()
      dict['m_x'] = x
      dict['m_y'] = y
      dict['m_z'] = z
      dict['new_dat_flag'] = 1
    
      f_log.write(str(dict) + "\n")

    except IOError as e:
      try:
        logging.exception('Got I2C exception on main handler' + str(dict['time']))
        
        err_lock.aqcuire()
        dict['xbee_errors'] += 1
        error_trace['error'] += e + '\n'
        err_lock.release()
  
        alt = BMP180.BMP180(last_measure)
        accel = LSM9DS0.LSM9DS0_ACCEL()
        gyro = LSM9DS0.LSM9DS0_GYRO(LSM9DS0.LSM9DS0_GYRODR_95HZ | LSM9DS0.LSM9DS0_GYRO_CUTOFF_1, LSM9DS0.LSM9DS0_GYROSCALE_2000DPS)
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
