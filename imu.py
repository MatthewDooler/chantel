from i2clibraries import i2c_hmc5883l
from i2clibraries import i2c_adxl345
from i2clibraries import i2c_itg3205

# IMU - Inertial measurement unit

# This interfaces with the SparkFun 9 Degrees of Freedom Sensor Stick
# https://www.sparkfun.com/products/10724
class SEN10724IMU(object):
	def __init__(self):
		i2c_port = 0  # different versions of the pi use different ports
		self.accelerometer = i2c_adxl345.i2c_adxl345(i2c_port)
		self.accelerometer.setScale(2)
		self.gyroscope = i2c_itg3205.i2c_itg3205(i2c_port, addr=0x68)
		self.magnetometer = i2c_hmc5883l.i2c_hmc5883l(i2c_port)
		self.magnetometer.setContinuousMode()
		self.magnetometer.setDeclination(1,43)  # magnetic declination in degrees west (degrees, minute)

	@property
	def acceleration(self):
		try:
			return self.accelerometer.getAxes()
		except OSError as e:
			print(e)
			return None

	@property
	def rotation(self):
		try:
			return self.gyroscope.getDegPerSecAxes()
		except OSError as e:
			print(e)
			return None

	@property
	def magfield(self):
		try:
			return self.magnetometer.getAxes()
		except OSError as e:
			print(e)
			return None


class FakeIMU(object):
	@property
	def acceleration(self):
		return (0,0,0)

	@property
	def rotation(self):
		return (0,0,0)

	@property
	def magfield(self):
		return (0,0,0)
