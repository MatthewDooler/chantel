from quadcopterPi.motor import motor
from quadcopterPi.sensor import sensor
from quadcopterPi.loggingQ import setupLogger
import time
from threading import Thread
import datetime as dt

class Props:
	def __init__(self, ahrs):
		self.ahrs = ahrs
		self.max_throttle = 100 # TODO: Danger! Danger! Set Me To 50!
		self.min_throttle = 0
		self.desired_throttle_prop_x_l = 0
		self.desired_throttle_prop_x_r = 0
		self.desired_throttle_prop_y_l = 0
		self.desired_throttle_prop_y_r = 0
		self.throttle_prop_x_l = 0
		self.throttle_prop_x_r = 0
		self.throttle_prop_y_l = 0
		self.throttle_prop_y_r = 0
		self.heading = None
		self.pitch = None
		self.roll = None
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
		while True:
			self._setAttitude(self.ahrs.heading, self.ahrs.pitch, self.ahrs.roll)
			time.sleep(self.update_period)

	def setDesiredThrottle(self, prop_x_l, prop_x_r, prop_y_l, prop_y_r):
		self.desired_throttle_prop_x_l = prop_x_l
		self.desired_throttle_prop_x_r = prop_x_r
		self.desired_throttle_prop_y_l = prop_y_l
		self.desired_throttle_prop_y_r = prop_y_r
		self._updateThrottle()

	def _setAttitude(self, heading, pitch, roll):
		self.heading = heading
		self.pitch = pitch
		self.roll = roll
		self._updateThrottle()

	def _updateThrottle(self):
		if self.heading is not None and self.pitch is not None and self.roll is not None:
			yaw_offset = 0 # TODO: make sure positive goes CW for sanity purposes
			
			if self.pitch <= -1:
				pitch_offset = 2
			elif self.pitch >= 1:
				pitch_offset = -2
			else:
				pitch_offset = 0

			if self.roll <= -1:
				roll_offset = 2
			elif self.roll >= 1:
				roll_offset = -2
			else:
				roll_offset = 0

			self.throttle_prop_x_l = self._normaliseThrottle(self.desired_throttle_prop_x_l - pitch_offset + yaw_offset)
			self.throttle_prop_x_r = self._normaliseThrottle(self.desired_throttle_prop_x_r + pitch_offset + yaw_offset)
			self.throttle_prop_y_l = self._normaliseThrottle(self.desired_throttle_prop_y_l - roll_offset - yaw_offset)
			self.throttle_prop_y_r = self._normaliseThrottle(self.desired_throttle_prop_y_r + roll_offset - yaw_offset)
			self.prop_x_l.setW(self.throttle_prop_x_l)
			self.prop_x_r.setW(self.throttle_prop_x_r)
			self.prop_y_l.setW(self.throttle_prop_y_l)
			self.prop_y_r.setW(self.throttle_prop_y_r)

	def _normaliseThrottle(self, throttle):
		return max(min(throttle, self.max_throttle), self.min_throttle)
