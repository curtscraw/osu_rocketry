import Adafruit_BBIO.GPIO as GPIO
from time import sleep
#from system import exit

CUTTER_PIN = "P9_12"
cutter_delay = 10

GPIO.setup(CUTTER_PIN, GPIO.OUT)
GPIO.output(CUTTER_PIN, GPIO.LOW)

while cutter_delay > 0:
  print "cutting in: " + str(cutter_delay)
  cutter_delay -= 1
  sleep(1)
print "Starting the cut"
GPIO.output(CUTTER_PIN, GPIO.HIGH)
print "Finished setting cut pin to \"high\""

sleep(2)

print "did it cut?"
GPIO.output(CUTTER_PIN, GPIO.LOW)

GPIO.cleanup()

exit()
