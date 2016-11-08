import robot
import moves as m

frindo = robot.Robot()

#print m.lige_gear_sensor_alt(frindo, 50)
print m.turn_baby_turn(180, 'right', frindo)
m.sleep(1)
#print m.lige_gear_sensor_alt(frindo, 50)
print m.turn_baby_turn(180, 'left', frindo)
m.sleep(1)
#print m.lige_gear_sensor_alt(frindo, 50)
print m.turn_baby_turn(180, 'right', frindo)
m.sleep(1)
#print m.lige_gear_sensor_alt(frindo, 50)
