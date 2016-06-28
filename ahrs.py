from fusion import fusion
from threading import Thread
import datetime as dt
import time

# AHRS - Attitude and heading reference system
class AHRS(object):
	def __init__(self, imu):
		self.imu = imu
		self.heading = None
		self.pitch = None
		self.roll = None
		self.fusion = fusion.Fusion()

		self.fusion.magbias = (12.879999999999995, -93.38, -52.900000000000006)
		self.fusion.pitch_when_level = 0
		self.fusion.roll_when_level = 4  # TODO: this is awful just level the sensor or fully calibrate everything
		
		self.update_frequency = 70 # Hz
		self.update_period = 1.0 / self.update_frequency
		self.min_updates = 400
		self.updates = 0

		self.worker = Thread(target=self.worker_start)
		self.worker.daemon = True
		self.worker.start()
		print("AHRS initialised")

	def worker_start(self):
		while True:
			start_time = dt.datetime.now()
			self.update()
			elapsed = self.fusion.elapsed_seconds(start_time)
			if elapsed < self.update_period:
				extra = self.update_period - elapsed
				time.sleep(extra)

	# Read values from the IMU and do the fusion calculations to update the heading, pitch and roll	
	def update(self):
		acceleration = self.imu.acceleration
		rotation = self.imu.rotation
		magfield = self.imu.magfield
		if acceleration is not None and rotation is not None and magfield is not None:
			self.fusion.update(acceleration, rotation, magfield)
			# wait until fusion algorithm has enough readings before setting attitude
			if self.updates >= self.min_updates:
				self.heading = self.fusion.heading
				self.pitch = self.fusion.pitch
				self.roll = self.fusion.roll
			self.updates = self.updates + 1

	def calibrate(self):
		calibration_duration = 60 # seconds
		self.calibration_start_time = dt.datetime.now()
		print("Calibrating...")
		self.fusion.calibrate(self.imu.magfield, self.stop_calibration)
		print("Calibrated with the following magbias:")
		print(self.fusion.magbias)

	def stop_calibration(self):
		elapsed = self.fusion.elapsed_seconds(self.calibration_start_time)
		if elapsed >= calibration_duration:
			return True
		else:
			return False

