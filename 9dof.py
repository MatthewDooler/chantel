#!/usr/bin/env python3
import sys
sys.path.append(r'/home/pi/git/quick2wire-python-api/')

from i2clibraries import i2c_hmc5883l
from i2clibraries import i2c_adxl345
from i2clibraries import i2c_itg3205

print("magnetometer:")
magnetometer = i2c_hmc5883l.i2c_hmc5883l(0)
magnetometer.setContinuousMode()
magnetometer.setDeclination(1,43) # magnetic declination in degrees west (degrees, minute)
print(magnetometer)

print("accelerometer:")
accelerometer = i2c_adxl345.i2c_adxl345(0)
accelerometer.setScale(2)
print(accelerometer)

print("gyroscope:")
gyroscope = i2c_itg3205.i2c_itg3205(0)
print(gyroscope)