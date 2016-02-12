import LSM9DS0
from time import sleep
from datetime.datetime import utcnow
import sys

gyro = LSM9DS0.LSM9DS0_GYRO(LSM9DS0_GYRO_95HZ | LSM9DS0_GYRO_CUTOFF_1, LSM9DS0_GYRO_SCALE_2000DPS)

while True:
  try:
    (x, y, z) = gyro.read()
    t = utcnow()

    print t + "x: " + x + " y: " + y + " z: " + z
  except KeyboardInterrupt:
    sys.exit()

