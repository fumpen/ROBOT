import robot
import moves
import sensor
import camera
import numpy as np
from time import sleep

frindo = robot.Robot()


BATTERY = 1

    
def evergreen():
	y = 0
	if sensor.frontSensor(frindo) < 300 and \
		sensor.rightSensor(frindo) < 300 and \
		sensor.leftSensor(frindo) < 300:
		x = camera.capture("img" + str(y), "out" + str(y))
		sleep(1.5)
		if x:
			if x < 368:
				z = np.divide(50, 368.) * (368 - x)
				print('z er: ' + str(z) + ' og x er: ' + str(x))
				if int(z) > 15:
					print("left")
					moves.turn_left(frindo, int(z), BATTERY)

			if 368 < x:
				z = np.divide(50, 368.) * (x-368)
				print('z er: ' + str(z) + ' og x er: ' + str(x))
				if z > 15:
					print("right")
					moves.turn_right(frindo, int(z), BATTERY)

			moves.forwardv2(frindo, 25, BATTERY)
		else:
			moves.turn_left(frindo, 50, BATTERY)
			y + 1
			return evergreen()

	else:
		print('lolz')
		return 0



evergreen()
