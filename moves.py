import robot
from time import sleep

frindo = robot.Robot()

frindo.set_speed(100)
frindo.set_turnspeed(130)
frindo.set_step_time(2000)
frindo.set_turn_time(1500)

sleep(1)

# Constants

SLEEP_SCALE = 0.059
SLEEP_SCALE_NI = 0.043
INTERVAL = 0.4

# moves for big batteri pack
off_set = 0.64


def pause():
	sleep(0.5)

def forward(cm):
	frindo.go_diff(80,97,1,1)
	
	# movement = cm * SLEEP_SCALE
	sleep(cm)
	
	frindo.stop()
        
	pause()

def turn_right(degree):
	frindo.go_diff(100,123,1,0)
	sleep((degree*off_set)/82.0)
	frindo.stop()
        pause()

def turn_left(degree):
        frindo.go_diff(100,123,0,1)
        sleep((degree*0.66)/90.0)
        frindo.stop()
        pause()

def forward_right(n):
	frindo.go_diff(68,68,1,1)
	sleep(n)
	frindo.stop()
        pause()

def forward_left(n):
	frindo.go_diff(100,146,1,1)
	sleep(n)
	frindo.stop()
        pause()

# moves ni V batteri

def go_forward_ni(cm):
	frindo.go_diff(66,83,1,1)

	movement = cm * SLEEP_SCALE_NI
	sleep(movement)

	frindo.stop()

def turn_right_ni(degree):
	frindo.go_diff(110,128,1,0)
	sleep(float(degree)/(4.0*90.0))
	frindo.stop()

def turn_left_ni(degree):
        frindo.go_diff(65,78,0,1)
        sleep(float(degree)/(134))
        frindo.stop()

def forward_right_ni(degree):
	frindo.go_diff(100,105,1,1)
	sleep(degree)
	frindo.stop()
	
def forward_left_ni(degree):
	frindo.go_diff(100,105,1,1)
        sleep(degree)
        frindo.stop()
