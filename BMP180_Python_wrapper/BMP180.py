import Adafruit_BMP.BMP085 as BMP085

class BMP180:
   """Wrapper for Adafruit BMP085 class to use our altitude functions
   Does direct pass through for all other functions"""

   def __init__(self, alt_init):
      self._sensor = BMP085.BMP085()
      self._base_alt = alt_init
      self._p0 = self._sensor.read_sealevel_pressure(self._base_alt)


   def read_raw_temp(self):
      """Reads the raw (uncompensated) temperature from the sensor."""
      return self._sensor.read_raw_temp()

   def read_raw_pressure(self):
      """Reads the raw (uncompensated) pressure level from the sensor."""
      return self._sensor.read_raw_pressure()

   def read_temperature(self):
      """Gets the compensated temperature in degrees Celsius."""
      return self._sensor.read_temperature()

   def read_pressure(self):
      """Gets the compensated pressure in Pascals."""
      return self._sensor.read_pressure()

   def read_altitude(self, sealevel_pa=101325.0):
      """Calculates the altitude in meters"""
      return self._sensor.read_altitude(sealevel_pa)

   def read_agl(self):
      """Calculates the altitude in meters. Returns AGL altitude """
      raw_alt = self._sensor.read_altitude(self._p0)
      alt = raw_alt - self._base_alt
      return alt

   def read_sealevel_pressure(self, altitude_m=0.0):
      """Calculates the pressure at sealevel when given a known altitude in
      meters. Returns a value in Pascals."""
      return self._sensor.read_sealevel_pressure(altitude_m)
