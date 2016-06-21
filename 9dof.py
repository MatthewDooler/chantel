#!/usr/bin/env python3
import sys
import datetime as dt
import time

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

frequency = 30 # Hz
duration = 60*10 # seconds
period = 1.0 / frequency

for x in range(0, frequency*duration):
	start_time = dt.datetime.now()
	accelerometer_values = accelerometer.getAxes()
	gyroscope_values = gyroscope.getAxes()
	magnetometer_values = magnetometer.getAxes()
	fusion.update(accelerometer_values, gyroscope_values, magnetometer_values)
	elapsed = fusion.elapsed_seconds(start_time)
	if x % frequency == 0:
		#print(accelerometer_values)
		#print(gyroscope_values)
		#print(magnetometer_values)
		degree = 72000
		#print("heading = %.0f°" % round(fusion.heading*degree, 0))
		#print("pitch="+str(fusion.pitch))
		#print("roll="+str(fusion.roll))
		#print("")
		print("heading = %.0f°, pitch = %.0f°, roll = %.0f°" % (round(fusion.heading*degree, 0), round(fusion.pitch*degree, 0), round(fusion.roll*degree, 0)))
	if elapsed > period:
		print("running slow (period="+str(period)+", elapsed="+str(elapsed)+")")
	else:
		extra = period - elapsed
		#print("running ok (period="+str(period)+", elapsed="+str(elapsed)+", extra="+str(extra)+")")
		time.sleep(extra)