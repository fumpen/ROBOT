import numpy as np
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

TURN_SPEED = {1: 53.57,
              2: 111.57}

GEAR = {1: [80, 100],
        2: [100, 120],
        3: [120, 148],
        4: [140, 168],
        5: [160, 190],
        6: [180, 208],
        7: [200, 230]}

GEAR_SPEED = {1: 16.74,
              2: 22.3,
              3: 26.99,
              4: 35.35,
              5: 35.83,
              6: 38.67,
              7: 39.89}

BREAK = {1: [100, 110],
         2: [100, 120],
         3: [120, 140],
         4: [140, 160],
         5: [160, 190],
         6: [180, 208],
         7: [200, 230]}

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
def force_break(frindo, gear):
    frindo.go_diff(BREAK[gear][0], BREAK[gear][1], 0, 0)
    sleep(0.1)
    frindo.stop()

def select_scale_params(cm, BATTERY):
    return ['acc_interval', 'dcc_interval', 'speed_l', 'speed_r', 'acc_time',
            'dcc_time', 'rest_time']


INNIT_SPEED_L = 80
INNIT_SPEED_R = 100
# ---------------------------------------#
# Toolbox for scalable movement ends here
# ---------------------------------------#


def lige_test_gear(frindo, tid, gear):
    x = 1
    while x < gear:
        y = GEAR[x]
        frindo.go_diff(y[0], y[1], 1, 1)
        x += 1
        sleep(0.5)
    frindo.go_diff(GEAR[gear][0], GEAR[gear][1], 1, 1)
    sleep(abs(tid - (float(x) * 0.5)))
    force_break()


def turn_break(direction, frindo):
    if direction == 'right':
        frindo.go_diff(GEAR[1][0] + 18, GEAR[1][1] + 13, 0, 1)
        sleep(0.03)
    else:
        frindo.go_diff(GEAR[1][0] + 20, GEAR[1][1] + 30, 1, 0)
        sleep(0.03)



"""
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
"""

def choose_gear(dist):
    if dist < 14.93:
        return 1, 0.0
    elif 14.93 <= dist < 28.43:
        return 2, 14.93
    elif 28.43 <= dist < 46.1:
        return 3, 28.43
    elif 46.1 <= dist < 64.02:
        return 4, 46.1
    elif 64.02 <= dist < 83.35:
        return 5, 64.02
    elif 83.35 <= dist < 103.3:
        return 6, 83.35
    elif 103.3 <= dist:
        return 7, 103.3

def lige_gear(frindo, dist):
    g, d = choose_gear(dist)
    x = 1
    while x < g:
        y = GEAR[x]
        frindo.go_diff(y[0], y[1], 1, 1)
        x += 1
        sleep(0.5)
    frindo.go_diff(GEAR[g][0], GEAR[g][1], 1, 1)
    sleep(abs(np.divide((dist - d), GEAR_SPEED[g])))
    force_break(frindo, g)


def dist_at_time(current_gear, time):
    dist = 0.0
    x = 0
    y = time
    while x < current_gear:
        x += 1
        if y <= 0.5:
            dist += GEAR_SPEED[x] * y
        else:
            dist += GEAR_SPEED[x] * 0.5
            y -= 0.5
    dist += GEAR_SPEED[current_gear] * y
    return dist

def ret_gear(original_dist, theta_time, observed_dist):
    origin_gear = choose_gear(original_dist)
    dist_theta_time = ret_gear(origin_gear, theta_time)
    return dist_theta_time - observed_dist



def ret_degrees(original_degrees, time):
    degrees_turned = 0.0
    if original_degrees <= 22.5 and 0.42 <= time:
        degrees_turned += TURN_SPEED[1] * time
    elif 22.5 < original_degrees <= 360.0 and 0.42 < time < 3.46:
        degrees_turned += TURN_SPEED[1] * 0.42
        degrees_turned += TURN_SPEED[2] * (time - 0.42)
    else:
        print "ERROR IN RET_DEGREES"
        raise
    return degrees_turned


def turn_test(degrees, direction, frindo):
    if direction == 'right':
        frindo.go_diff(GEAR[1][0] + 20, GEAR[1][1] + 15, 1, 0)
        sleep(degrees)
    else:
        frindo.go_diff(GEAR[1][0] + 10, GEAR[1][1] + 10, 0, 1)
        sleep(degrees)
    turn_break(direction, frindo)
    frindo.stop()

def turn_baby_turn(degrees, direction, frindo):
    if degrees <= 22.5:
        s_timer = np.divide(degrees, TURN_SPEED[1])
        if direction == 'right':
            frindo.go_diff(GEAR[1][0] + 20, GEAR[1][1] + 15, 1, 0)
        else:
            frindo.go_diff(GEAR[1][0] + 10, GEAR[1][1] + 10, 0, 1)
        sleep(s_timer)
    elif 22.5 < degrees <= 360.0:
        s_timer = np.divide(22.5, TURN_SPEED[1])
        s_timer += np.divide((degrees - 22.5), TURN_SPEED[2])
        if direction == 'right':
            frindo.go_diff(GEAR[1][0] + 20, GEAR[1][1] + 15, 1, 0)
        else:
            frindo.go_diff(GEAR[1][0] + 10, GEAR[1][1] + 10, 0, 1)
        sleep(s_timer)
    else:
        print "ERROR IN RET_DEGREES"
        raise
    turn_break(direction, frindo)
    frindo.stop()
