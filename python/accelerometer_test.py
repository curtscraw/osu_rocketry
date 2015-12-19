#!/usr/bin/python

from sys import exit
from Adafruit_I2C import Adafruit_I2C
from time import sleep
import datetime
import math
import Adafruit_BMP.BMP085 as BMP085

CTRL_REG1_XM = 0x20
CTRL_REG2_XM = 0x21
WHO_AM_I_XM  = 0x0F

LSB_VAL = 0.732

accel = Adafruit_I2C(0x1D)
sensor = BMP085.BMP085()

INIT_ALT = 72
Po = sensor.read_sealevel_pressure(INIT_ALT) 	#must calibrate using a known itial state

#our altimeter function
def osu_aiaa_alt(s):
	alt = s.read_altitude(Po)
	alt -= INIT_ALT
	return alt

accel_in = accel.readU8(WHO_AM_I_XM);
if not (accel_in == 0x49):
	print "WHO_AM_I expected 0x49, got ", accel_in
	exit(1)

#setup
accel.write8(CTRL_REG1_XM, 0x57) #50 Hz
accel.write8(0x24, 0xF0)

accel_in = accel.readU8(CTRL_REG2_XM)
accel_in &= 0xC7
accel_in |= 0x20 #16g for now
accel.write8(CTRL_REG2_XM, accel_in)

while True:
	xlo = accel.readU8(0x28)
	xhi = accel.readU8(0x29)
	x = (xlo | xhi << 8)
	if x >= 32768:
		x -= 65536
	
	ylo = accel.readU8(0x2A)
	yhi = accel.readU8(0x2B)
	y = (ylo | yhi << 8)
	if y >= 32768:
		y -= 65536
	
	zlo = accel.readU8(0x2C)
	zhi = accel.readU8(0x2D)
	z = (zlo | zhi << 8)
	if z >= 32768:
		z -= 65536
	
	x_dat = (x * LSB_VAL) / 1000
	y_dat = (y * LSB_VAL) / 1000
	z_dat = (z * LSB_VAL) / 1000

	#for total magnitude/drop/impact tests
	vec_mag = math.sqrt(x_dat ** 2 + y_dat ** 2 + z_dat ** 2)
	print "Total G Magnitude: ", vec_mag
	#print 'Temp = {0:0.2f} *C'.format(sensor.read_temperature())
	#print 'Altitude = {0:0.2f} m'.format(osu_aiaa_alt(sensor))
	#print datetime.datetime.utcnow()
	print "x: ", x_dat, " y: ", y_dat, " z: ", z_dat
	print " "
	sleep(.1)		
