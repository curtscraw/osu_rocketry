import gps
from time import sleep
from sys import exit
import subprocess


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
