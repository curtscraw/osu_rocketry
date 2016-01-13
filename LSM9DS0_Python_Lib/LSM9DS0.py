#Python I2C class for the ST LSM9DS0 Accel/Gyro/Mag/Temp sensor
#based on Adafruit C++ class for the LSM9DS0: https://github.com/adafruit/Adafruit_LSM9DS0_Library

#Dependencies of these classes
import Adafruit_GPIO.I2C as i2c
import sys

#I2C addresses for the device
LSM9DS0_ACCEL_ADDR      = 0x1D;
LSM9DS0_GYRO_ADDR       = 0x6B;

#Internal Registers
#Accelerometer ones
LSM9DS0_REG_TEMP_OUT_L_XM           = 0x05
LSM9DS0_REG_TEMP_OUT_H_XM           = 0x06
LSM9DS0_REG_STATUS_REG_M            = 0x07
LSM9DS0_REG_OUT_X_L_M               = 0x08
LSM9DS0_REG_OUT_X_H_M               = 0x09
LSM9DS0_REG_OUT_Y_L_M               = 0x0A
LSM9DS0_REG_OUT_Y_H_M               = 0x0B
LSM9DS0_REG_OUT_Z_L_M               = 0x0C
LSM9DS0_REG_OUT_Z_H_M               = 0x0D
LSM9DS0_REG_WHO_AM_I_XM             = 0x0F
LSM9DS0_REG_INT_CTRL_REG_M          = 0x12
LSM9DS0_REG_INT_SRC_REG_M           = 0x13
LSM9DS0_REG_CTRL_REG1_XM            = 0x20
LSM9DS0_REG_CTRL_REG2_XM            = 0x21
LSM9DS0_REG_CTRL_REG5_XM            = 0x24
LSM9DS0_REG_CTRL_REG6_XM            = 0x25
LSM9DS0_REG_CTRL_REG7_XM            = 0x26
LSM9DS0_REG_OUT_X_L_A               = 0x28
LSM9DS0_REG_OUT_X_H_A               = 0x29
LSM9DS0_REG_OUT_Y_L_A               = 0x2A
LSM9DS0_REG_OUT_Y_H_A               = 0x2B
LSM9DS0_REG_OUT_Z_L_A               = 0x2C
LSM9DS0_REG_OUT_Z_H_A               = 0x2D


#gyro ones
LSM9DS0_REG_WHO_AM_I_G              = 0x0F
LSM9DS0_REG_CTRL_REG1_G             = 0x20
LSM9DS0_REG_CTRL_REG3_G             = 0x22
LSM9DS0_REG_CTRL_REG4_G             = 0x23
LSM9DS0_REG_OUT_X_L_G               = 0x28
LSM9DS0_REG_OUT_X_H_G               = 0x29
LSM9DS0_REG_OUT_Y_L_G               = 0x2A
LSM9DS0_REG_OUT_Y_H_G               = 0x2B
LSM9DS0_REG_OUT_Z_L_G               = 0x2C
LSM9DS0_REG_OUT_Z_H_G               = 0x2D

#value defines for scale of data registers
#accel/mag
LSM9DS0_ACCEL_LSB_2G                = 0.061
LSM9DS0_ACCEL_LSB_4G                = 0.122
LSM9DS0_ACCEL_LSB_6G                = 0.183
LSM9DS0_ACCEL_LSB_8G                = 0.244
LSM9DS0_ACCEL_LSB_16G               = 0.732


LSM9DS0_MAG_MGAUSS_2                = 0.08
LSM9DS0_MAG_MGAUSS_4                = 0.16
LSM9DS0_MAG_MGAUSS_8                = 0.32
LSM9DS0_MAG_MGAUSS_12               = 0.48

#gyro
LSM9DS0_GYRO_245DPS                 = 0.00875
LSM9DS0_GYRO_500DPS                 = 0.01750
LSM9DS0_GYRO_2000DPS                = 0.07000

#gyro data rate settings and cutoff bandwith
#TODO add more variety
LSM9DS0_GYRODR_95HZ                 = (0b00 << 6)
LSM9DS0_GYRODR_190HZ                = (0b01 << 6)
LSM9DS0_GYRODR_380HZ                = (0b10 << 6)
LSM9DS0_GYRODR_760HZ                = (0b11 << 6)

#bandwith selection bits                           DR:   90    190   380   760
LSM9DS0_GYRO_CUTOFF_1               = (0b00 << 4)  #     12.5  12.5  20    30
LSM9DS0_GYRO_CUTOFF_2               = (0b01 << 4)  #     25    25    25    25
LSM9DS0_GYRO_CUTOFF_3               = (0b10 << 4)  #     25    50    50    50
LSM9DS0_GYRO_CUTOFF_4               = (0b11 << 4)  #     25    70    100   100

#configuration register values
#accelerometer range setting
LSM9DS0_ACCELRANGE_2G               = (0b000 << 3)
LSM9DS0_ACCELRANGE_4G               = (0b001 << 3)
LSM9DS0_ACCELRANGE_6G               = (0b010 << 3)
LSM9DS0_ACCELRANGE_8G               = (0b011 << 3)
LSM9DS0_ACCELRANGE_16G              = (0b100 << 3)

#acceleration data rate
LSM9DS0_ACCELDR_POWERDOWN           = (0b0000 << 4)
LSM9DS0_ACCELDR_3_125HZ             = (0b0001 << 4)
LSM9DS0_ACCELDR_6_25HZ              = (0b0010 << 4)
LSM9DS0_ACCELDR_12_5HZ              = (0b0011 << 4)
LSM9DS0_ACCELDR_25HZ                = (0b0100 << 4)
LSM9DS0_ACCELDR_50HZ                = (0b0101 << 4)
LSM9DS0_ACCELDR_100HZ               = (0b0110 << 4)
LSM9DS0_ACCELDR_200HZ               = (0b0111 << 4)
LSM9DS0_ACCELDR_400HZ               = (0b1000 << 4)
LSM9DS0_ACCELDR_800HZ               = (0b1001 << 4)
LSM9DS0_ACCELDR_1600HZ              = (0b1010 << 4)

#mag range setting 
LSM9DS0_MAGGAIN_2GAUSS              = (0b00 << 5)    # +/- 2 gauss
LSM9DS0_MAGGAIN_4GAUSS              = (0b01 << 5)    # +/- 4 gauss
LSM9DS0_MAGGAIN_8GAUSS              = (0b10 << 5)    # +/- 8 gauss
LSM9DS0_MAGGAIN_12GAUSS             = (0b11 << 5)    # +/- 12 gauss

#mag data rate    
LSM9DS0_MAGDR_3_125HZ               = (0b000 << 2)
LSM9DS0_MAGDR_6_25HZ                = (0b001 << 2)
LSM9DS0_MAGDR_12_5HZ                = (0b010 << 2)
LSM9DS0_MAGDR_25HZ                  = (0b011 << 2)
LSM9DS0_MAGDR_50HZ                  = (0b100 << 2)
LSM9DS0_MAGDR_100HZ                 = (0b101 << 2)

#gyro scale
LSM9DS0_GYROSCALE_245DPS            = (0b00 << 4)    # +/- 245 degrees per second rotation
LSM9DS0_GYROSCALE_500DPS            = (0b01 << 4)    # +/- 500 degrees per second rotation
LSM9DS0_GYROSCALE_2000DPS           = (0b10 << 4)    # +/- 2000 degrees per second rotation

#ID register info
LSM9DS0_GYRO_ID                     = 0b11010100
LSM9DS0_ACCEL_ID                    = 0b01001001

#TODO
#gyro specific code
class LSM9DS0_GYRO:
   #setup the gyro TODO
   def __init__(self, gyro_dr=(LSM9DS0_GYRODR_95HZ | LSM9DS0_GYRO_CUTOFF_1), gyro_scale=LSM9DS0_GYROSCALE_245DPS, gyro_addr=LSM9DS0_GYRO_ADDR):
      """looks for the lsm9dso on i2c bus, and performs register configuration on it"""
      self._sensor = i2c.get_i2c_device(gyro_addr)
      
      #verify initialization by checking the who_am_i register
      if not (self._sensor.readU8(LSM9DS0_REG_WHO_AM_I_G) == LSM9DS0_GYRO_ID):
         #not the right device!
         print "Could not initialize the gyro!"
         #sys.exit()

      self.start_capture()
      self._config_gyro(gyro_scale, gyro_dr)
  
   def _config_gyro(self, scale, gyro_dr):
      """perform configuration based on the mode passed in"""
      #data aquisition rate
      temp_reg = self._sensor.readU8(LSM9DS0_REG_CTRL_REG1_G)
      temp_reg &= 0x0F
      temp_reg |= gyro_dr
      self._sensor.write8(LSM9DS0_REG_CTRL_REG1_G, temp_reg)

      #set scale
      temp_reg = self._sensor.readU8(LSM9DS0_REG_CTRL_REG4_G)
      temp_reg &= 0xFC
      temp_reg |= scale
      self._sensor.write8(LSM9DS0_REG_CTRL_REG4_G, temp_reg)

      #record the scale for computations
      if (scale == LSM9DS0_GYROSCALE_245DPS):
         self._gyro_dps = LSM9DS0_GYRO_245DPS
      elif (scale == LSM9DS0_GYROSCALE_500DPS):
         self._gyro_dps = LSM9DS0_GYRO_500DPS
      elif (scale == LSM9DS0_GYROSCALE_2000DPS):
         self._gyro_dps = LSM9DS0_GYRO_2000DPS
      
      
   def start_capture(self):
      """start data logging on the sensor"""
      temp_reg = self._sensor.readU8(LSM9DS0_REG_CTRL_REG1_G)
      temp_reg |= 0x0F           #enable all 3 axis, and put into normal mode
      self._sensor.write8(LSM9DS0_REG_CTRL_REG1_G, temp_reg)

   def stop_capture(self):
      """stop data capture, puts it into low power mode"""
      temp_reg = self._sensor.readU8(LSM9DS0_REG_CTRL_REG1_G)
      temp_reg &= 0xF7           #put it into power down mode
      self._sensor.write8(LSM9DS0_REG_CTRL_REG1_G, temp_reg)
   
   def _parse_raw(self, raw_gyro):
      """takes raw gyro 16 bit data in, parses it and normalizes per manual"""
      #normalize the gyro range
      if (raw_gyro >= 32768):
         raw_gyro -= 65536

      return raw_gyro * self._gyro_dps

   def read_x(self):
      """read the x data, then parse it and return"""
      d_lo = self._sensor.readU8(LSM9DS0_REG_OUT_X_L_G)
      d_hi = self._sensor.readU8(LSM9DS0_REG_OUT_X_H_G)

      axis = (d_lo | d_hi << 8)

      return self._parse_raw(axis)
   
   def read_y(self):
      """read the y data, parse, and return"""
      d_lo = self._sensor.readU8(LSM9DS0_REG_OUT_Y_L_G)
      d_hi = self._sensor.readU8(LSM9DS0_REG_OUT_Y_H_G)

      axis = (d_lo | d_hi << 8)

      return self._parse_raw(axis)
   
   def read_z(self):
      """read the z data, parse, and then return"""
      d_lo = self._sensor.readU8(LSM9DS0_REG_OUT_Z_L_G)
      d_hi = self._sensor.readU8(LSM9DS0_REG_OUT_Z_H_G)

      axis = (d_lo | d_hi << 8)

      return self._parse_raw(axis)
   
   def read(self):
      """return the x, y, and z gyro readings"""
      x = self.read_x()
      y = self.read_y()
      z = self.read_z()
      return (x, y, z)

#accelerometer and magnetometer specific code
class LSM9DS0_ACCEL:
   """TODO Docstring"""
   #setup the accel based on mode for precision, rate, etc
   def __init__(self, accel_dr=LSM9DS0_ACCELDR_50HZ, mag_dr=LSM9DS0_MAGDR_50HZ, accel_range=LSM9DS0_ACCELRANGE_16G, mag_gain=LSM9DS0_MAGGAIN_2GAUSS, addr=LSM9DS0_ACCEL_ADDR):
      """setup for the accelerometer portion of the lsm9ds0"""
      self._sensor = i2c.get_i2c_device(addr)
      
      #verify initialization by checking the who_am_i register
      if not (self._sensor.readU8(LSM9DS0_REG_WHO_AM_I_XM) == 0x49):
         #not the right device!
         print "Could not initialize the accelerometer!"
         #sys.exit()

      #turn on the 3 axis for both ones
      self.start_capture() 
      
      #set read frequency
      self._config_accel(accel_dr, accel_range)
      self._config_magnetometer(mag_dr, mag_gain)

   def _config_accel(self, datarate, g_range):
      """setup accelerometer control registers"""
      #frequency
      temp_reg = self._sensor.readU8(LSM9DS0_REG_CTRL_REG1_XM)
      temp_reg &= 0x0F
      temp_reg |= datarate
      self._sensor.write8(LSM9DS0_REG_CTRL_REG1_XM, temp_reg)

      #data range
      temp_reg = self._sensor.readU8(LSM9DS0_REG_CTRL_REG2_XM)
      temp_reg &= 0xC7
      temp_reg |= g_range
      self._sensor.write8(LSM9DS0_REG_CTRL_REG2_XM, temp_reg)
   
      if (g_range == LSM9DS0_ACCELRANGE_16G):
         self._accel_lsb = LSM9DS0_ACCEL_LSB_16G
      elif (g_range == LSM9DS0_ACCELRANGE_8G):
         self._accel_lsb = LSM9DS0_ACCEL_LSB_8G
      elif (g_range == LSM9DS0_ACCELRANGE_6G):
         self._accel_lsb = LSM9DS0_ACCEL_LSB_6G
      elif (g_range == LSM9DS0_ACCELRANGE_4G):
         self._accel_lsb = LSM9DS0_ACCEL_LSB_4G
      elif (g_range == LSM9DS0_ACCELRANGE_2G):
         self._accel_lsb = LSM9DS0_ACCEL_LSB_2G
      else:
         self._accel_lsb = 0

   def _config_magnetometer(self, datarate, gain):
      """setup magnetometer control registers"""
      #setup the magnetometer datarate
      temp_reg = self._sensor.readU8(LSM9DS0_REG_CTRL_REG5_XM)
      temp_reg &= 0xE3
      temp_reg |= datarate
      self._sensor.write8(LSM9DS0_REG_CTRL_REG5_XM, temp_reg)

      #setup magnetometer gauss gain
      self._sensor.write8(LSM9DS0_REG_CTRL_REG6_XM, gain)      #only two bits that aren't zero
      
      if (gain == LSM9DS0_MAGGAIN_2GAUSS):
         self._mag_lsb = LSM9DS0_MAG_MGAUSS_2
      elif (gain == LSM9DS0_MAGGAIN_4GAUSS):
         self._mag_lsb = LSM9DS0_MAG_MGAUSS_4
      elif (gain == LSM9DS0_MAGGAIN_8GAUSS):
         self._mag_lsb = LSM9DS0_MAG_MGAUSS_8
      elif (gain == LSM9DS0_MAGGAIN_12GAUSS):
         self._mag_lsb = LSM9DS0_MAG_MGAUSS_12
      else:
         self._mag_lsb = 0
 
   def start_capture(self):
      """enable magnetometer and accelerometer data if it has been disabled"""
      #AXEN, AZEN, and AYEN all set to 1
      temp_reg = self._sensor.readU8(LSM9DS0_REG_CTRL_REG1_XM)
      temp_reg |= 0x7
      self._sensor.write8(LSM9DS0_REG_CTRL_REG1_XM, temp_reg)

      #set magnetometer mode to continuous mode
      temp_reg = self._sensor.readU8(LSM9DS0_REG_CTRL_REG7_XM)
      temp_reg &= 0xFC
      self._sensor.write8(LSM9DS0_REG_CTRL_REG7_XM, temp_reg)

   def stop_capture(self):
      """sets the Accelerometer and Magnetometer both to low power modes"""
      #AXEN, AZEN, and AYEN all set to 0
      temp_reg = self._sensor.readU8(LSM9DS0_REG_CTRL_REG1_XM)
      temp_reg &= 0xF8
      self._sensor.write8(LSM9DS0_REG_CTRL_REG1_XM, temp_reg)

      #set magnetometer mode to off
      temp_reg = self._sensor.readU8(LSM9DS0_REG_CTRL_REG7_XM)
      temp_reg |= 0x03
      self._sensor.write8(LSM9DS0_REG_CTRL_REG7_XM, temp_reg)
   
   def _parse_accel(self, raw_accel):
      """takes raw accelrometer data, and interperates it"""
      if raw_accel >= 32768:
         raw_accel -= 65536

      #1000 is a constant to get to G's on earth
      parsed = (raw_accel * self._accel_lsb) / 1000
   
      return parsed
   
   def _parse_mag(self, raw_mag):
      """parses the raw magnetometer data"""
      if raw_mag >= 32768:
         raw_mag -= 65536

      parsed = (raw_mag * self._mag_lsb) / 1000

      return parsed

   def accel_x(self):
      """read accelerometer x data"""
      xlo = self._sensor.readU8(LSM9DS0_REG_OUT_X_L_A)
      xhi = self._sensor.readU8(LSM9DS0_REG_OUT_X_H_A)
      x = (xlo | xhi << 8)
      
      return self._parse_accel(x)

   def accel_y(self):
      """read accelerometer y data"""
      ylo = self._sensor.readU8(LSM9DS0_REG_OUT_Y_L_A)
      yhi = self._sensor.readU8(LSM9DS0_REG_OUT_Y_H_A)
      y = (ylo | yhi << 8)
      return self._parse_accel(y)

   def accel_z(self):
      """read accelerometer z data"""
      zlo = self._sensor.readU8(LSM9DS0_REG_OUT_Z_L_A)
      zhi = self._sensor.readU8(LSM9DS0_REG_OUT_Z_H_A)
      z = (zlo | zhi << 8)
      return self._parse_accel(z)
   
   def mag_x(self):
      """read magnetometer x data"""
      xlo = self._sensor.readU8(LSM9DS0_REG_OUT_X_L_M)
      xhi = self._sensor.readU8(LSM9DS0_REG_OUT_X_H_M)
      x = (xlo | xhi << 8)
      
      return self._parse_mag(x)

   def mag_y(self):
      """read magnetometer y data"""
      ylo = self._sensor.readU8(LSM9DS0_REG_OUT_Y_L_M)
      yhi = self._sensor.readU8(LSM9DS0_REG_OUT_Y_H_M)
      y = (ylo | yhi << 8)
      return self._parse_mag(y)

   def mag_z(self):
      """read magnetometer z data"""
      zlo = self._sensor.readU8(LSM9DS0_REG_OUT_Z_L_M)
      zhi = self._sensor.readU8(LSM9DS0_REG_OUT_Z_H_M)
      z = (zlo | zhi << 8)
      return self._parse_mag(z)

   
   def read_accel(self):
      """read all x, y, and z acceleration data"""
      #reads in acceleration from the LSM9DS0 accelerometer device
      #i2c read of all the x, y, z hi and lo registers
      x = self.accel_x()
      y = self.accel_y()
      z = self.accel_z()
      return (x, y, z)

   def read_magnetometer(self):
      """reads all 3 magnetometer axis"""
      x = self.mag_x()
      y = self.mag_y()
      z = self.mag_z()
      return (x, y, z)

class LSM9DS0:
   #include a default value for modes
   def __init__(self):
      self.gyro   = LSM9DS0_GYRO()
      self.accel  = LSM9DS0_ACCEL()

   def start_gyro():
      self.gyro.start_capture()

   def start_accel():
      self.accel.start_capture()

   def stop_gyro():
      self.gyro.stop_capture()

   def stop_accel():
      self.gyro.stop_capture()

   def read_accel(self):
      return self.accel.read_accel()

   def read_gyro(self):
      return self.gyro.read()

   def read_mag(self):
      return self.accel.read_magnetometer()

