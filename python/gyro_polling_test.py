import LSM9DS0
from time import sleep
import sys
import datetime


f_log = open('/home/osu_rocketry/python/high_rev.out', 'r')

while True:
  try:
    gyro = LSM9DS0.LSM9DS0_GYRO(LSM9DS0.LSM9DS0_GYRODR_95HZ | LSM9DS0.LSM9DS0_GYRO_CUTOFF_1, LSM9DS0.LSM9DS0_GYROSCALE_2000DPS)
    (x, y, z) = gyro.read()
    accel = LSM9DS0.LSM9DS0_ACCEL(LSM9DS0.LSM9DS0_GYRODR_95HZ | LSM9DS0.LSM9DS0_GYRO_CUTOFF_1, LSM9DS0.LSM9DS0_GYROSCALE_2000DPS)
    (x_mag, y_mag, z_mag) = accel.read_magnetometer()
    t = datetime.datetime.utcnow()

    dat = str(t) + "x: " + str(x) + " y: " + str(y) + " z: " + str(z)
    dat_mag = str(t) + "x_mag:" + str(x_mag) + "y_mag:" + str(y_mag) + "z_mag:" + str(z_mag)
    print "Gyro:"
    print dat
    print "Magnetometer:"
    print dat_mag
    sleep(1)
    f_log.write(dat)
  except KeyboardInterrupt:
    f_log.close()
    sys.exit()
  except IOError:
    i = 1
