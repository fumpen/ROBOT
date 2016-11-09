import moves as m
import datetime
import robot
from time import sleep
frindo = robot.Robot()

for x in range(0, 3):
    sleep(0.2)
    m.turn_baby_turn(15, 'left', frindo)
