#!/usr/bin/env python3
import sys
import datetime as dt
import time
import math
import argparse

from quadcopterPi.motor import motor
from quadcopterPi.sensor import sensor
from quadcopterPi.loggingQ import setupLogger

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

prop_x_l = motor('prop_x_l', 23, simulation=False)
prop_x_r = motor('prop_x_r', 21, simulation=False)
prop_y_l = motor('prop_y_l', 24, simulation=False)
prop_y_r = motor('prop_y_r', 17, simulation=False)
props = [prop_x_l, prop_x_r, prop_y_l, prop_y_r]
for prop in props:
	prop.start()
	prop.setW(0)
time.sleep(1)

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
fusion.magbias = (12.879999999999995, -93.38, -52.900000000000006)
fusion.pitch_when_level = 0.85
fusion.roll_when_level = 9.95 # starts rolled because of sensor slope
# TODO: might be better/easier to do this calibration on the raw data - see how this goes first
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


frequency = 70 # Hz
duration = 60*10 # seconds
period = 1.0 / frequency

for x in range(0, frequency*duration):
	try:
		start_time = dt.datetime.now()
		accelerometer_values = accelerometer.getAxes()
		gyroscope_values = gyroscope.getAxes()
		# TODO: handle exceptions in general.. don't want to crash on an unexpected exception
		magnetometer_values = magnetometer.getAxes()
		fusion.update(accelerometer_values, gyroscope_values, magnetometer_values)
		heading = fusion.heading
		pitch = fusion.pitch
		roll = fusion.roll
		#fusion.update_nomag(accelerometer_values, gyroscope_values)
		#fusion.update(accelerometer_values, (0,0,0), magnetometer_values)

		throttle = 80
		yaw_offset = 0 # TODO: make sure positive goes CW for sanity purposes
		
		if pitch <= -1:
			pitch_offset = 2
		elif pitch >= 1:
			pitch_offset = -2
		else:
			pitch_offset = 0

		if roll <= -1:
			roll_offset = 2
		elif roll >= 1:
			roll_offset = -2
		else:
			roll_offset = 0

		prop_x_l_speed = throttle - pitch_offset + yaw_offset
		prop_x_r_speed = throttle + pitch_offset + yaw_offset
		prop_y_l_speed = throttle - roll_offset - yaw_offset
		prop_y_r_speed = throttle + roll_offset - yaw_offset
		prop_x_l.setW(prop_x_l_speed)
		prop_x_r.setW(prop_x_r_speed)
		prop_y_l.setW(prop_y_l_speed)
		prop_y_r.setW(prop_y_r_speed)
		if x % frequency == 0:
			print("props = %.0f, %.0f, %.0f, %.0f" % (prop_x_l_speed, prop_x_r_speed, prop_y_l_speed, prop_y_r_speed))

		elapsed = fusion.elapsed_seconds(start_time)
		if x % frequency == 0:
			#print("accel = %s, gyro = %s, mag = %s" % (accelerometer_values, gyroscope_values, magnetometer_values))
			#print("%s, %s, %s, %s, %s, %s, %s, %s, %s" % (accelerometer_values[0], accelerometer_values[1], accelerometer_values[2], gyroscope_values[0], gyroscope_values[1], gyroscope_values[2], magnetometer_values[0], magnetometer_values[1], magnetometer_values[2]))
			print("heading = %.0f°, pitch = %.0f°, roll = %.0f°, t = %.0fms, f = %.0fHz" % (round(heading, 0), round(pitch, 0), round(roll, 0), elapsed*1000, round(1.0/elapsed, 0)))
		if elapsed < period:
			extra = period - elapsed
			time.sleep(extra)
	except OSError as e:
		print(e)