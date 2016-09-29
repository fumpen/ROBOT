import robot
import moves
import sensor
import camera
from time import sleep

frindo = robot.Robot()


BATTERY = 1



    
def evergreen():
	
	if sensor.frontSensor(frindo) < 300 and \
	sensor.rightSensor(frindo) < 300 and \
	sensor.leftSensor(frindo) < 300:

		x = camera.capture()
		sleep(5)
		if x:
			if x in range(368):
				if int(110/368) * x > 15:
					moves.turn_right(frindo, int(110/368) * x, BATTERY)
		    
			if x  not in range(368) and x in range(736):
				if int(110/368) * x > 15:
					moves.turn_left(frindo, int(110/368) * x, BATTERY)
		    
			moves.forwardv2(frindo, 15, BATTERY)
		else:
			moves.turn_left(frindo, 50, BATTERY)
		
		return evergreen()
	else:
		print('lolz')
		return 0



evergreen()
