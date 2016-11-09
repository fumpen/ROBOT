# ===========================================
#
# Filename: moves.py
#
# Description:
#
# Robot movement functions.
#
# ===========================================

from time import sleep
import sensor as s
import numpy as np
from datetime import datetime as dt
import robot


# === MOVEMENT CONSTANTS ====================
#
# TURN_SPEED:
#
# GEAR:
#
#     Speed constants [left, right] wheel.
#     Robot gears range from [1; 7].
#
# GEAR_SPEED:
#
# BREAK:
#
#     Break constants [left, right] wheel.
#     Robot breaks according to gear speed.
#
# ===========================================

THETA_TIME = 0.000866

# THETA_CHANGE_GEAR = 57
THETA_CHANGE_GEAR = 45

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


def force_break(frindo, gear):
    frindo.go_diff(BREAK[gear][0], BREAK[gear][1], 0, 0)
    sleep(0.05)
    frindo.stop()


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


def lige_gear_sensor(frindo, dist):
    print 'Lige_gear_distance: ' + str(dist)
    g, d = choose_gear(dist)
    print 'g (init):' + str(g)
    x = 1
    ts = dt.now()
    print 'ts (init): ' + str(ts)
    while x < g:
        print 'x (first while loop): ' + str(x)
        y = GEAR[x]
        frindo.go_diff(y[0], y[1], 1, 1)
        x += 1
        y = 0
        while y < THETA_CHANGE_GEAR:
            if not s.allSensor_gear(frindo, x):
                break
            y += 1
        if y != THETA_CHANGE_GEAR:
            break
    if x == g:
        frindo.go_diff(GEAR[g][0], GEAR[g][1], 1, 1)
        y = 0
        time_left = abs(np.divide(
            np.divide((dist - d), GEAR_SPEED[g]), THETA_TIME))
        print 'time_left: ' + str(time_left)
        while y < time_left:
            if not s.allSensor_gear(frindo, g):
                break
            y += 1
        force_break(frindo, g)
        if y == time_left:
            print 'finished as planned'
            return dist
        else:
            print 'after reaching gear'
            tf = dt.now()
            print 'tf first else: ' + str(tf)
            return dist_at_time(x, (tf - ts).total_seconds())
    else:
        print 'while gearing up'
        force_break(frindo, x)
        tf = dt.now()
	print 'tf andet else: ' + str(tf)
        return dist_at_time(x, (tf - ts).total_seconds())


def dist_at_time(current_gear, time):
    print 'dist_at_time: ' + str(time)
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
        if 0 < s_timer:
            sleep(s_timer)
    elif 22.5 < degrees <= 360.0:
        s_timer = np.divide(22.5, TURN_SPEED[1])
        s_timer += np.divide((degrees - 22.5), TURN_SPEED[2])
        if direction == 'right':
            frindo.go_diff(GEAR[1][0] + 20, GEAR[1][1] + 15, 1, 0)
        else:
            frindo.go_diff(GEAR[1][0] + 10, GEAR[1][1] + 10, 0, 1)
        if 0 < s_timer:
            sleep(s_timer)
    else:
        print "ERROR IN RET_DEGREES"
        raise
    turn_break(direction, frindo)
    frindo.stop()
