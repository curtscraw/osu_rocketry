#!/usr/bin/python

import Adafruit_BBIO.UART as u
import serial
import time
import sys

u.setup("UART1")

time.sleep(1)

ser = serial.Serial('/dev/ttyO1', 19200);

i = 0

while True:
	string = "Hello world: " + str(i) + "\n"
	i = i + 1

	try:
		ser.write(string)
		print string
		time.sleep(1)
	except:
		print "done"
		sys.exit()

