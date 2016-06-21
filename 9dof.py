#!/usr/bin/env python3
import sys
sys.path.append(r'/home/pi/git/quick2wire-python-api/')

from i2clibraries import i2c_hmc5883l
from i2clibraries import i2c_adxl345
from i2clibraries import i2c_itg3205
from fusion import fusion

print("accelerometer:")
accelerometer = i2c_adxl345.i2c_adxl345(0)
accelerometer.setScale(2)
accelerometer_axes = accelerometer.getAxes()
print(accelerometer_axes)

print("gyroscope:")
gyroscope = i2c_itg3205.i2c_itg3205(0, addr=0x68)
gyroscope_axes = gyroscope.getAxes()
print(gyroscope_axes)

print("magnetometer:")
magnetometer = i2c_hmc5883l.i2c_hmc5883l(0)
magnetometer.setContinuousMode()
magnetometer.setDeclination(1,43) # magnetic declination in degrees west (degrees, minute)
magnetometer_axes = magnetometer.getAxes()
print(magnetometer_axes)

fusion = fusion.Fusion()
fusion.update(accelerometer_axes, gyroscope_axes, magnetometer_axes)
print("heading="+str(fusion.heading))
print("pitch="+str(fusion.pitch))
print("roll="+str(fusion.roll))