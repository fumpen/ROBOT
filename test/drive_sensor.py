import sys
from time import sleep
sys.path.append('/home/pi/Robot/ROBOT')
import robot
import moves as mv
import sensor

frindo = robot.Robot()
BATTERY = 1

frindo.go_diff(112,133,1,1)

for x in range (100):
  sleep(0.15)
  print sensor.frontSensor(frindo)

frindo.stop()
