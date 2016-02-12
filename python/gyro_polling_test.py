import LSM9DS0
from time import sleep
import sys
import datetime

gyro = LSM9DS0.LSM9DS0_GYRO(LSM9DS0.LSM9DS0_GYRODR_95HZ | LSM9DS0.LSM9DS0_GYRO_CUTOFF_1, LSM9DS0.LSM9DS0_GYROSCALE_2000DPS)

while True:
  try:
    (x, y, z) = gyro.read()
    t = datetime.datetime.utcnow()

    print str(t) + "x: " + str(x) + " y: " + str(y) + " z: " + str(z)
  except KeyboardInterrupt:
    sys.exit()

