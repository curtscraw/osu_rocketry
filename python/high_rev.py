import time
import sys
from datetime.datetime import utcnow
import LSM9DS0

g = LSM9DS0.LSM9DS0_GYRO()

t_end = time.time() + 60 * 3	#run for 3 minutes

f_log = open('/home/osu_rocketry/python/high_rev.out', 'a')

#f_log.write("starting high revolution test")

while True:
  try:
    (x, y, z) = gyro.read()
    t = utcnow()
    data = ' ' + t + "x: " + x + " y: " + y + " z: " + z
    #f_log.write(data)
    print data
f_log.close()
