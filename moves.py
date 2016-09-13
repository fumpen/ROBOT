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
INTERVAL = 0.5

# moves for big batteri pack
off_set = 0.64


def pause():
	sleep(0.5)


def calculated_acceleration(left_w, right_w, left_dir, right_dir, time, 
			   interval):
	print '------------------------'
	print time
	print '------------------------'
	rounds = 0
	left_wheel = int(left_w / 3)
	right_wheel = int(right_w / 3)
	while time > (rounds + (3 * interval)):
		rounds += interval
		frindo.go_diff(left_wheel, right_wheel, left_dir, right_dir)
		if (left_wheel * 2) > left_w:
			left_wheel = left_w
		else:
			left_wheel = left_wheel * 2
		if (right_wheel * 2) > right_w:
			right_wheel = right_w
		else:
			right_wheel = right_wheel * 2
		sleep(interval)
	while time > rounds:
		rounds += INTERVAL
		left_wheel = int(left_wheel / 1.3)
		right_wheel = int(right_wheel / 1.3)
		frindo.go_diff(left_wheel, right_wheel, left_dir, right_dir)
		sleep(interval)
	frindo.stop()
	print 'reached stop!'

def alternate_forward(cm):
	NEW_SCALE = 0.06
	calculated_acceleration(160, 185, 1, 1, (cm * NEW_SCALE), INTERVAL)
	pause()

def alternate_turn(degree_turn):
	NEW_TURN_SCALE = 0.0188
	calculated_acceleration(100, 123, 1, 0, (NEW_TURN_SCALE * degree_turn),
				0.25)
	pause()	


def forward(cm):
	frindo.go_diff(80,103,1,1)
	
	movement = cm * SLEEP_SCALE
	sleep(movement)
	
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
