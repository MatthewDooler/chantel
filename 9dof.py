import sys
sys.path.append(r'/home/pi/git/quick2wire-python-api/')

from i2clibraries import i2c_hmc5883l
hmc5883l = i2c_hmc5883l.i2c_hmc5883l(0)
hmc5883l.setContinuousMode()
hmc5883l.setDeclination(1,43) #  magnetic declination in degrees west (degrees, minute)
print(hmc5883l)