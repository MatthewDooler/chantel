#!/usr/bin/env python3
import sys
import datetime as dt
import time
import math

sys.path.append(r'/home/pi/git/quick2wire-python-api/')
from i2clibraries import i2c_hmc5883l
from i2clibraries import i2c_adxl345
from i2clibraries import i2c_itg3205

from fusion import fusion

accelerometer = i2c_adxl345.i2c_adxl345(0)
accelerometer.setScale(2)

gyroscope = i2c_itg3205.i2c_itg3205(0, addr=0x68)

magnetometer = i2c_hmc5883l.i2c_hmc5883l(0)
magnetometer.setContinuousMode()
magnetometer.setDeclination(1,43) # magnetic declination in degrees west (degrees, minute)

fusion = fusion.Fusion()

calibration_duration = 60 # seconds
calibration_start_time = dt.datetime.now()
def stopCalibration():
	elapsed = fusion.elapsed_seconds(calibration_start_time)
	if elapsed >= calibration_duration:
		return True
	else:
		return False
print("Calibrating...")
#fusion.calibrate(magnetometer.getAxes, stopCalibration)
#fusion.magbias = (12.879999999999995, -93.38, -52.900000000000006)
print("Calibrated with the following magbias:")
print(fusion.magbias)
# static:
# (219.42, -69.92, -449.42)
# (218.50, -70.84, -448.50)
# (218.50, -70.38, -450.34)
# (217.58, -70.84, -449.88)
# (219.42, -71.30, -448.96)
# horrific rotation around all 3 axes:
# (12.879999999999995, -93.38, -52.900000000000006)

frequency = 50 # Hz
duration = 60*10 # seconds
period = 1.0 / frequency

for x in range(0, frequency*duration):
	start_time = dt.datetime.now()
	accelerometer_values = accelerometer.getAxes()
	gyroscope_values = gyroscope.getAxes()
	magnetometer_values = magnetometer.getAxes()
	fusion.update(accelerometer_values, gyroscope_values, magnetometer_values)
	#fusion.update_nomag(accelerometer_values, gyroscope_values)
	#fusion.update(accelerometer_values, (0,0,0), magnetometer_values)
	elapsed = fusion.elapsed_seconds(start_time)
	if x % frequency == 0:
		#print(accelerometer_values)
		#print(gyroscope_values)
		#print(magnetometer_values)
		#degree = 1
		#print("heading = %.0f°" % round(fusion.heading*degree, 0))
		#print("pitch="+str(fusion.pitch))
		#print("roll="+str(fusion.roll))
		#print("")
		#print("accel = %s, gyro = %s, mag = %s" % (accelerometer_values, gyroscope_values, magnetometer_values))
		print("heading = %.0f°, pitch = %.0f°, roll = %.0f°, t = %.0fms, f = %.0fHz" % (round(fusion.heading, 0), round(fusion.pitch, 0), round(fusion.roll, 0), elapsed*1000, round(1.0/elapsed, 0)))
		#accelerationX = accelerometer_values[0] * 3.9;
		#accelerationY = accelerometer_values[1] * 3.9;
		#accelerationZ = accelerometer_values[2] * 3.9;
		#pitch = 180 * math.atan (accelerationX/math.sqrt(accelerationY*accelerationY + accelerationZ*accelerationZ))/math.pi
		#roll = 180 * math.atan (accelerationY/math.sqrt(accelerationX*accelerationX + accelerationZ*accelerationZ))/math.pi
		#yaw = 180 * math.atan (accelerationZ/math.sqrt(accelerationX*accelerationX + accelerationZ*accelerationZ))/math.pi
		#print("$ heading = %.0f°, pitch = %.0f°, roll = %.0f°" % (round(yaw, 0), round(pitch, 0), round(roll, 0)))
	if elapsed < period:
		extra = period - elapsed
		time.sleep(extra)