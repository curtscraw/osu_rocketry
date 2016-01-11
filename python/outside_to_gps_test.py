#!/usr/bin/python

from gps import *      #interface with gpsd
import subprocess     #allows for starting the gpsd service
import time      #for sleep timing 
import sys      #for exiting when there is no fix
import Adafruit_BBIO.UART as UART #Adafruit BeagleBobe UART libraries
 
UART.setup("UART1")    #initialize the SERIAL1 or UART1 interface pins
#TODO: Setup gps on uart2 instead of uart1

#this ensures that the gpsd service is running
#the gpsd service provides the python gps module with input from the physical module
#gpsd must be configured using "gpsd -n /dev/ttyO1 -F var/run/gpsd.sock"
#prior to running this code 
try: 
    subprocess.check_output(["pgrep", "gpsd"]) 
except subprocess.CalledProcessError: 
    #gpsd isn't running yet, start it up 
    subprocess.check_output(["systemctl", "start", "gpsd.service"]) 

gps_in = gps(mode=WATCH_ENABLE) 	#read data in from the gpsd interface library
no_fix_count = 5     #limit the time spent waiting for a fix in this test 
  
while True: #run until a keyboard-interupt 
    gps_in.next()
    print "fix mode: ", gps_in.fix.mode
    if (gps_in.fix.mode != 1):   #a fix.mode value of 1 indicated no gps fix
        #have a gps fix, print the data or make it available in a global data structure
        print "time: ", gps_in.fix.time, "latitude: ", gps_in.fix.latitude, ", longitude: ", gps_in.longitude, "altitude: ", gps_in.fix.altitude
        print "total number of satellites tracked: ", len(gps_in.satellites)
        print " "
        no_fix_count = 5   #reset no_fix_count 
    else:
	time.sleep(1)
