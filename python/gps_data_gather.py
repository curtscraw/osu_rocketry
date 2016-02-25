import gps
import Adafruit_BBIO.UART as UART
from time import sleep
import subprocess
import sys

UART.setup("UART2")

session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)


#this ensures that the gpsd service is running
#the gpsd service provides the python gps module with input from the physical module
#gpsd must be configured using "gpsd -n /dev/ttyO1 -F var/run/gpsd.sock"
#prior to running this code 
try: 
    subprocess.check_output(["pgrep", "gpsd"]) 
except subprocess.CalledProcessError: 
    #gpsd isn't running yet, start it up 
    subprocess.check_output(["systemctl", "start", "gpsd.service"]) 

no_fix_count = 120
while True:
	try:
		report = session.next()
		if (session.fix.mode != 1):
			print "GPS fix time: ", session.fix.time
			print "  position: ", session.fix.latitude, ' ', session.fix.longitude
			print "  altitude: ", session.fix.altitude
			print "  tracked satelites: ", len(session.satellites)
			print "  "
			no_fix_count = 120		#reset fix miss count
		else:
			no_fix_count -= 1
			if no_fix_count <= 0:
				print "could not achieve a fix, stopping"
				sys.exit() 
			print "no fix, trying in 1 second"
			sleep(1)
			
		
	except KeyError:
		pass
	except KeyboardInterrupt:
		quit()
	except StopIteration:
		session = None
		print "GPSD has terminated"

			
