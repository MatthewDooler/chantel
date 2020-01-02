from quadcopterPi.motor import motor
from quadcopterPi.sensor import sensor
from quadcopterPi.loggingQ import setupLogger
from ahrs import Attitude
import time
from threading import Thread
import datetime as dt

class Props:
	def __init__(self, ahrs):
		self.ahrs = ahrs
		self.max_throttle = 100
		self.min_throttle = 0
		self.desired_throttle_prop_x_l = 0
		self.desired_throttle_prop_x_r = 0
		self.desired_throttle_prop_y_l = 0
		self.desired_throttle_prop_y_r = 0
		self.throttle_prop_x_l = 0
		self.throttle_prop_x_r = 0
		self.throttle_prop_y_l = 0
		self.throttle_prop_y_r = 0
		self.actual_attitude = None
		self.desired_attitude = Attitude()
		self.update_frequency = 10 # Hz
		self.update_period = 1.0 / self.update_frequency
		self.worker = Thread(target=self.worker_start)
		self.worker.daemon = True
		self.worker.start()

	def worker_start(self):
		self.prop_x_l = motor('prop_x_l', 23, simulation=False)
		self.prop_x_r = motor('prop_x_r', 21, simulation=False)
		self.prop_y_l = motor('prop_y_l', 24, simulation=False)
		self.prop_y_r = motor('prop_y_r', 17, simulation=False)
		self.props = [self.prop_x_l, self.prop_x_r, self.prop_y_l, self.prop_y_r]
		for prop in self.props:
			prop.start()
			prop.setW(0)
		time.sleep(1) # all hell breaks loose if we don't wait before setting a new throttle
		print("Props initialised")
		self.actual_attitude = self.ahrs.attitude
		while True:
			if not self.desired_attitude.available():
				self.setDefaultDesiredAttitude()
			self._updateThrottle()
			time.sleep(self.update_period)

	def setDefaultDesiredAttitude(self):
		# Default to current heading but a stable pitch and roll
		# e.g., takeoff behaviour from a slope would be to get level but stay facing the same direction
		self.desired_attitude.heading = self.ahrs.attitude.heading
		self.desired_attitude.pitch = 0
		self.desired_attitude.roll = 0

	def setDesiredThrottle(self, prop_x_l, prop_x_r, prop_y_l, prop_y_r):
		self.desired_throttle_prop_x_l = prop_x_l
		self.desired_throttle_prop_x_r = prop_x_r
		self.desired_throttle_prop_y_l = prop_y_l
		self.desired_throttle_prop_y_r = prop_y_r
		self._updateThrottle()

	def setDesiredAttitude(self, heading, pitch, roll):
		self.desired_attitude.heading = heading
		self.desired_attitude.pitch = pitch
		self.desired_attitude.roll = roll
		self._updateThrottle()

	def _updateThrottle(self):
		if self.actual_attitude.available() and self.desired_attitude.available():
			yaw_offset = 0 # TODO: make sure positive goes CW for sanity purposes
			
			pitch_offset_degrees = self.desired_attitude.pitch - self.actual_attitude.pitch
			# pitch_offset = self._prOffset(pitch_offset_degrees)
			pitch_offset = 0
	
			roll_offset_degrees = self.desired_attitude.roll - self.actual_attitude.roll
			roll_offset = self._prOffset(roll_offset_degrees)
			# print(roll_offset)
			# roll_offset = 0

			# TODO Part 1 - Aim to quickly reach intended attitude (which is initially <heading>,0,0)
			# TODO Part 2 maybe somewhere else - Stay at this attitude until destination is reached (e.g., key no longer held), then stabalise

			self.throttle_prop_x_l = self._normaliseThrottle(self.desired_throttle_prop_x_l - pitch_offset + yaw_offset)
			self.throttle_prop_x_r = self._normaliseThrottle(self.desired_throttle_prop_x_r + pitch_offset + yaw_offset)
			self.throttle_prop_y_l = self._normaliseThrottle(self.desired_throttle_prop_y_l - roll_offset - yaw_offset)
			self.throttle_prop_y_r = self._normaliseThrottle(self.desired_throttle_prop_y_r + roll_offset - yaw_offset)

			self.prop_x_l.setW(self.throttle_prop_x_l)
			self.prop_x_r.setW(self.throttle_prop_x_r)
			self.prop_y_l.setW(self.throttle_prop_y_l)
			self.prop_y_r.setW(self.throttle_prop_y_r)

	def _prOffset(self, degrees):
		max_offset = 5
		return max(min(-(degrees / 10.0), max_offset), -max_offset)

	def _normaliseThrottle(self, throttle):
		return max(min(throttle, self.max_throttle), self.min_throttle)
