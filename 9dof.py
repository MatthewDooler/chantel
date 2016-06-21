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

frequency = 50 # Hz
duration = 60 # seconds
period = 1.0 / frequency

for x in range(0, frequency*duration):
	start_time = dt.datetime.now()
	accelerometer_values = accelerometer.getAxes()
	gyroscope_values = gyroscope.getAxes()
	magnetometer_values = magnetometer.getAxes()
	fusion.update(accelerometer_values, gyroscope_values, magnetometer_values)
	elapsed = fusion.elapsed_seconds(start_time)
	if x % frequency == 0:
		print("heading="+str(fusion.heading))
		#print("pitch="+str(fusion.pitch))
		#print("roll="+str(fusion.roll))
		#print("")
	if elapsed > period:
		print("running slow (period="+str(period)+", elapsed="+str(elapsed)+")")
	else:
		extra = period - elapsed
		#print("running ok (period="+str(period)+", elapsed="+str(elapsed)+", extra="+str(extra)+")")
		time.sleep(extra)