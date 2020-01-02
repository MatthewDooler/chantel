#!/usr/bin/env python3
import sys
import datetime as dt
import time
import math
import argparse
import json

from api import APIServer
from imu import SEN10724IMU
from imu import FakeIMU
from ahrs import AHRS
from props import Props

if len(sys.argv) >= 2 and sys.argv[1] == "local":
	imu = FakeIMU()
else:
	imu = SEN10724IMU()
ahrs = AHRS(imu)

props = Props(ahrs)
api_server = APIServer(port=8081, props=props)

publish_frequency = 5 # Hz
publish_period = 1.0 / publish_frequency
i = 0
while True:
	(heading, pitch, roll) = (ahrs.attitude.heading, ahrs.attitude.pitch, ahrs.attitude.roll)
	if heading is not None and pitch is not None and roll is not None:
		if i % publish_frequency == 0:
			#print("t = %s, accel = %s, gyro = %s, mag = %s, heading = %.0f, pitch = %.0f, roll = %.0f" % (start_time, accelerometer_values, gyroscope_values, magnetometer_values, round(heading, 0), round(pitch, 0), round(roll, 0)))
			#print("t = %s, heading = %.0f, pitch = %.0f, roll = %.0f" % (start_time, round(heading, 0), round(pitch, 0), round(roll, 0)))
			#print("props = %.0f, %.0f, %.0f, %.0f" % (prop_x_l_speed, prop_x_r_speed, prop_y_l_speed, prop_y_r_speed))
			#print("accel = %s, gyro = %s, mag = %s" % (accelerometer_values, gyroscope_values, magnetometer_values))
			#print("%s, %s, %s, %s, %s, %s, %s, %s, %s" % (accelerometer_values[0], accelerometer_values[1], accelerometer_values[2], gyroscope_values[0], gyroscope_values[1], gyroscope_values[2], magnetometer_values[0], magnetometer_values[1], magnetometer_values[2]))
			print("heading = %.0f, pitch = %.0f, roll = %.0f, prop_x_l = %.0f, prop_x_r = %.0f, prop_y_l = %.0f, prop_y_r = %.0f" % (round(heading, 0), round(pitch, 0), round(roll, 0), round(props.throttle_prop_x_l, 1), round(props.throttle_prop_x_r, 1), round(props.throttle_prop_y_l, 1), round(props.throttle_prop_y_r, 1)))

		for client in api_server.clients:
			message = {
				'heading': heading,
				'pitch': pitch,
				'roll': roll,
				'cam_image_uri': 'img/8FnqQTs.jpg',
				'cam_image_heading': -140,
				'cam_image_pitch': 0,
				'cam_image_roll': 0,
				'throttle': {
					'0': props.throttle_prop_x_l,
					'1': props.throttle_prop_x_r,
					'2': props.throttle_prop_y_l,
					'3': props.throttle_prop_y_r
				}
			}
			client.sendMessage(json.dumps(message))
	time.sleep(publish_period)
	i = i + 1

