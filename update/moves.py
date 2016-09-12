import robot
from time import sleep

frindo = robot.Robot()

sleep(1)


# -------------------------------------#
#               CONSTANTS              #
# -------------------------------------#
#                                      #
#                                      #
#   Description:                       #
#                                      #
#   BATTERY     - 0 (9v battery)       #
#               - 1 (Big battery pack) #
#                                      #
#   SLEEP_SCALE    - Scalar to sleep   #
#   SLEEP_SCALE_NI - Scalar to 9v      #
#                                      #
#   OFF_SET - Scalar to rotation       #
# -------------------------------------#

BATTERY        = 1
SLEEP_SCALE    = 0.059
SLEEP_SCALE_NI = 0.043
OFF_SET        = 0.64



# -------------------------------------#
#               PAUSE                  #
# -------------------------------------#
#                                      #
#                                      #
#   Description:                       #
#                                      #
#   Pause is used to give the motor    #
#   some time to get ready, before     #
#   a new instruction.                 #
# -------------------------------------#

def pause():
	sleep(0.5)


# -------------------------------------#
#           ROBOT MOVEMENT             #
# -------------------------------------#
#                                      #
#                                      #
#   Description:                       #
#                                      #
#   forward(cm) - Moves the given      #
#               - amount of cm.        #
#                                      #
#   turn_right(degree) - rotate right  #
#   turn_left(degree)  - rotate left   #
#                                      #
#                                      #
#   forward_right(degree) - curv right #
#   forward_left(degree)  - curv left  #
#                                      #
#                                      #
# -------------------------------------#

def forward(cm):
        
        if BATTERY:

	    frindo.go_diff(80,103,1,1)
            secToSleep = cm * SLEEP_SCALE
        else:

            frindo.go_diff(66,83,1,1)
	    secToSleep = cm * SLEEP_SCALE_NI
	
        
        sleep(secToSleep)
        frindo.stop()
	pause()


def turn_right(degree):

    if BATTERY:
        
        frindo.go_diff(100,123,1,0)
	secToSleep = ((degree*OFF_SET)/82.0)
    else:

	frindo.go_diff(110,128,1,0)
	secToSleep = (float(degree)/(4.0*90.0))

    sleep(secToSleep)
    frindo.stop()
    pause()

def turn_left(degree):

    if BATTERY:

        frindo.go_diff(100,123,0,1)
        secToSleep = ((degree*0.66)/90.0)
    else:
        frindo.go_diff(65,78,0,1)
        secToSleep = (float(degree)/(134))
        
    sleep(secToSleep)
    frindo.stop()
    pause()

def forward_right(degree):
    
    if BATTERY:
        
        frindo.go_diff(68,68,1,1)
	secToSleep = degree
    else:

	frindo.go_diff(100,105,1,1)
        secToSleep = degree
        
    sleep(secToSleep)
    frindo.stop()
    pause()

def forward_left(degree):

    if BATTERY:
	
        frindo.go_diff(100,146,1,1)
	secToSleep = degree
    else:
        
        frindo.go_diff(100,146,1,1)
	secToSleep = degree
    
    sleep(secToSleep)
    frindo.stop()
    pause()

