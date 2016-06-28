#!/usr/bin/env python3
import sys
import datetime as dt
import time
import math
import argparse
from threading import Thread
import json
import queue

from quadcopterPi.motor import motor
from quadcopterPi.sensor import sensor
from quadcopterPi.loggingQ import setupLogger

from api import APIServer
from imu import SEN10724IMU
from imu import FakeIMU
from ahrs import AHRS

api_server = APIServer(port=8081)

#imu = SEN10724IMU()
imu = FakeIMU()
ahrs = AHRS(imu)

prop_x_l = motor('prop_x_l', 23, simulation=False)
prop_x_r = motor('prop_x_r', 21, simulation=False)
prop_y_l = motor('prop_y_l', 24, simulation=False)
prop_y_r = motor('prop_y_r', 17, simulation=False)
props = [prop_x_l, prop_x_r, prop_y_l, prop_y_r]
for prop in props:
	prop.start()
	prop.setW(0)
time.sleep(1)

i = 0
while True:
	(heading, pitch, roll) = (ahrs.heading, ahrs.pitch, ahrs.roll)
	if heading is not None and pitch is not None and roll is not None:
		#print("t = %s, accel = %s, gyro = %s, mag = %s, heading = %.0f, pitch = %.0f, roll = %.0f" % (start_time, accelerometer_values, gyroscope_values, magnetometer_values, round(heading, 0), round(pitch, 0), round(roll, 0)))
		#print("t = %s, heading = %.0f, pitch = %.0f, roll = %.0f" % (start_time, round(heading, 0), round(pitch, 0), round(roll, 0)))

		throttle = 10
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
		#if x % sensor_read_frequency == 0:
		#	print("props = %.0f, %.0f, %.0f, %.0f" % (prop_x_l_speed, prop_x_r_speed, prop_y_l_speed, prop_y_r_speed))

		# TODO: publish these metrics at 10Hz
		for client in APIServer.clients:
			message = {
				'heading': heading,
				'pitch': pitch,
				'roll': roll,
				'cam_image_uri': 'img/8FnqQTs.jpg',
				'cam_image_heading': -140,
				'cam_image_pitch': 0,
				'cam_image_roll': 0
			}
			client.sendMessageAsync(json.dumps(message))

		#print("accel = %s, gyro = %s, mag = %s" % (accelerometer_values, gyroscope_values, magnetometer_values))
		#print("%s, %s, %s, %s, %s, %s, %s, %s, %s" % (accelerometer_values[0], accelerometer_values[1], accelerometer_values[2], gyroscope_values[0], gyroscope_values[1], gyroscope_values[2], magnetometer_values[0], magnetometer_values[1], magnetometer_values[2]))
		print("heading = %.0f°, pitch = %.0f°, roll = %.0f°" % (round(heading, 0), round(pitch, 0), round(roll, 0)))
	time.sleep(1)
	i = i + 1

