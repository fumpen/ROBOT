import datetime
import robot
from time import sleep
import sensor


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

SLEEP_SCALE    = 0.057
SLEEP_SCALE_NI = 0.043
OFF_SET        = 0.64


def pause():
    """ Ensures the robot does nothing prior to next action
    :return: nothing
    """
    sleep(1)

def forward(frindo, cm, BATTERY):
    """This makes the robot goe straight forward
    :param cm: the number of centimeters the robot must traverse
    :return: nothing
    """
    if BATTERY:

        frindo.go_diff(112,133,1,1)
        secToSleep = cm * SLEEP_SCALE
    else:

        frindo.go_diff(66,83,1,1)
        secToSleep = cm * SLEEP_SCALE_NI


    sleep(secToSleep)
    frindo.stop()
    pause()


def turn_right(frindo, degree, BATTERY):

    if BATTERY:

        frindo.go_diff(100,123,1,0)
        secToSleep = ((degree*OFF_SET)/82.0)
    else:

        frindo.go_diff(110,128,1,0)
        secToSleep = (float(degree)/(4.0*90.0))

    sleep(secToSleep)
    frindo.stop()
    pause()

def turn_left(frindo, degree, BATTERY):

    if BATTERY:

        frindo.go_diff(115,139,0,1)
        secToSleep = ((degree*0.85)/150)
    else:
        frindo.go_diff(65,78,0,1)
        secToSleep = (float(degree)/(134))

    sleep(secToSleep)
    frindo.stop()
    pause()

def forward_right(frindo, degree, BATTERY):

    if BATTERY:

        frindo.go_diff(68,68,1,1)
        secToSleep = degree
    else:

        frindo.go_diff(100,105,1,1)
        secToSleep = degree

    sleep(secToSleep)
    frindo.stop()
    pause()

def forward_left(frindo, degree, BATTERY):

    if BATTERY:

        frindo.go_diff(100,146,1,1)
        secToSleep = degree
    else:

        frindo.go_diff(100,146,1,1)
        secToSleep = degree

    sleep(secToSleep)
    frindo.stop()
    pause()


def forwardv2(frindo, cm, BATTERY):
    """This makes the robot goe straight forward
    :param cm: the number of centimeters the robot must traverse
    :return: nothing
    """
    if BATTERY:

        frindo.go_diff(112,133,1,1)
        secToSleep = cm * SLEEP_SCALE
    else:

        frindo.go_diff(66,83,1,1)
        secToSleep = cm * SLEEP_SCALE_NI
    
    x_1 = datetime.datetime.now()
    x_t = datetime.timedelta(seconds=secToSleep)
    x_2 = x_1 + x_t
    
    while x_1 < x_2 and sensor.frontSensor(frindo) < 300 and sensor.rightSensor(frindo) < 300 and sensor.leftSensor(frindo) < 300: 
      x_1 = datetime.datetime.now()

    frindo.stop()
    pause()




# ------------------------------------------#
# Toolbox for scalable movement starts here
# ------------------------------------------#
def force_break(frindo):
    frindo.go_diff(INNIT_SPEED_L, INNIT_SPEED_R, 0, 0)
    sleep(0.2)
    frindo.stop()

def select_scale_params(cm, BATTERY):
    return ['acc_interval', 'dcc_interval', 'speed_l', 'speed_r', 'acc_time',
            'dcc_time', 'rest_time']


INNIT_SPEED_L = 80
INNIT_SPEED_R = 100
# ---------------------------------------#
# Toolbox for scalable movement ends here
# ---------------------------------------#

def scale(cm, frindo, BATTERY):
    parameters = select_scale_params(cm, BATTERY)

    speed_l = INNIT_SPEED_L
    speed_r = INNIT_SPEED_R

    x = 0
    while x < parameters[0]:
        frindo.go_diff(speed_l, speed_r, 1, 1)
        x += 1
        speed_l += int((parameters[2] - INNIT_SPEED_L)/ parameters[0])
        speed_r += int((parameters[3] - INNIT_SPEED_R) / parameters[0])
        sleep(parameters[4])

    frindo.go_diff(speed_l, speed_r, 1, 1)
    sleep(parameters[6])

    x = 0
    while x < parameters[1]:
        x += 1
        speed_l -= int((parameters[2] - INNIT_SPEED_L)/ parameters[0])
        speed_r -= int((parameters[3] - INNIT_SPEED_R) / parameters[0])
        sleep(parameters[5])
    force_break()


def scale_test(cm, frindo, BATTERY):
    parameters = select_scale_params(cm, BATTERY)

    speed_l = INNIT_SPEED_L
    speed_r = INNIT_SPEED_R

    x = 0
    while x < parameters[0]:
        frindo.go_diff(speed_l, speed_r, 1, 1)
        x += 1
        speed_l += int((parameters[2] - INNIT_SPEED_L)/ parameters[0])
        speed_r += int((parameters[3] - INNIT_SPEED_R) / parameters[0])
        sleep(parameters[4])

    frindo.go_diff(speed_l, speed_r, 1, 1)
    sleep(parameters[6])
    force_break()


def lige_test(frindo, tid, venstre, hoejre):
    speed_l = INNIT_SPEED_L
    speed_r = INNIT_SPEED_R

    x = 0
    while x < 3:
        frindo.go_diff(speed_l, speed_r, 1, 1)
        x += 1
        speed_l += int((venstre - INNIT_SPEED_L) / 3)
        speed_r += int((hoejre - INNIT_SPEED_R) / 3)
        sleep(0.5)
    frindo.go_diff(venstre, hoejre, 1, 1)

    sleep(tid - 1.5)
    force_break()
