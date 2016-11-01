import ex5_i_love_brainz as p
import moves as m
import robot
import camera
import numpy as np
import math
from time import sleep
import cv2

# setup config
frindo = robot.Robot()
cam = camera.Camera(0, 'frindo')
world = np.zeros((500, 500, 3), dtype=np.uint8)
WIN_RF1 = "Robot view"
cv2.namedWindow(WIN_RF1)
cv2.moveWindow(WIN_RF1, 50, 50)

WIN_World = "World view"
cv2.namedWindow(WIN_World)
cv2.moveWindow(WIN_World, 500, 50)


LANDMARK = {0: 0,
            1: 0}
LANDMARK_COORDINATES = {0: [0, 0],
                        1: [0, 300]}


def update_landmark(num_landmark):
    if num_landmark == 1:
        LANDMARK[1] = 1
    elif num_landmark == 0:
        LANDMARK[0] = 1
    else:
        raise

def update_turn(particles, dir, deg):
    if dir == 'left':
        return p.update_particles(particles, cam, 0.0, deg, world, WIN_RF1, WIN_World)
    else:
        return p.update_particles(particles, cam, 0.0, ((-1.0) * deg), world, WIN_RF1, WIN_World)

def find_landmark(particles, previously_moved=0.0):
    """
    :param particles: list of particles
    :param previously_moved: degrees (to mitegate turning more that 360
    :return: RET = [est_pose, [objectType, measured_distance, measured_angle,
                        integer-rep-of-landmark]]
             degrees_moved: degrees turned to find a landmark
    """
    degrees_moved = previously_moved
    move_pr_turn = 25.0
    while degrees_moved <= 360:
        m.turn_baby_turn(move_pr_turn, 'right', frindo)
        degrees_moved += move_pr_turn
        ret = update_turn(particles, 'right', move_pr_turn)
        if ret[1][3] is not None:
            update_landmark(ret[1][3])
            break
        else:
            ret = None

    print [ret[0].getX(), ret[0].getY()]
    return [ret, degrees_moved]


particles = p.innit_particles()
innit_est_pose = p.estimate_position(particles)
p.update_particles(particles, cam, 0.0, 0.0, world, WIN_RF1, WIN_World)

while True:
    print 'Landmarks ' + str(LANDMARK[0]) + ' | ' + str(LANDMARK[1])
    if LANDMARK[0] == LANDMARK[1] == 1:
        print "Found Both landmarks"
        dest = p.where_to_go(p.estimate_position(particles), [0, 150])
        m.turn_baby_turn(dest[2], dest[1], frindo)
        sleep(0.5)
        update_turn(particles, dest[1], dest[2])
        m.lige_gear(frindo, dest[0])
        p.update_particles(particles, cam, dest[0], 0.0, world, WIN_RF1, WIN_World)

        for t in range(1, 3):
            q = find_landmark(particles)
            if q[0][0]:
                dest = p.where_to_go(q[0][0], [0, 150])
                m.turn_baby_turn(dest[2], dest[1], frindo)
                sleep(0.5)
                update_turn(particles, dest[1], dest[2])
                m.lige_gear(frindo, dest[0])
                p.update_particles(particles, cam, dest[0], 0.0, world, WIN_RF1, WIN_World)
        break
    elif LANDMARK[0] + LANDMARK[1] == 1:
        print "Found one landmark!! In elif"
        x = find_landmark(particles)
        if np.degrees(x[0][1][2]) >= 0.0:
            turn_dir = 'left'
        else:
            turn_dir = 'right'
        m.turn_baby_turn(np.degrees(x[0][1][2]), turn_dir, frindo)
        update_turn(particles, turn_dir, np.degrees(x[0][1][2]))
        sleep(0.5)

        if x[0][1][1] > 20.0:
            m.lige_gear(frindo, (x[0][1][1] - 20.0))
            p.update_particles(particles, cam, (x[0][1][1] - 20.0), 0.0, world, WIN_RF1, WIN_World)
            sleep(0.5)

        m.turn_baby_turn(80.0, 'right', frindo)
        update_turn(particles, 'right', 80.0)
        sleep(0.5)

        m.lige_gear(frindo, 80.0)
        p.update_particles(particles, cam, 80.0, 0.0, world, WIN_RF1, WIN_World)
        sleep(0.5)

        m.turn_baby_turn(80.0, 'left', frindo)
        update_turn(particles, 'left', 80.0)
        sleep(0.5)

        m.lige_gear(frindo, 60.0)
        p.update_particles(particles, cam, 60.0, 0.0, world, WIN_RF1, WIN_World)
        previously_turned = 0.0
        while previously_turned <= 360:
            if LANDMARK[0] == LANDMARK[1] != 1:
                x = find_landmark(particles)
            else:
                break
            previously_turned += x[1]

    else:
        previously_turned = 0.0
        print "Sitting in Else inside while loop"
        while previously_turned <= 360:
            if LANDMARK[0] + LANDMARK[1] != 2:
                x = find_landmark(particles)
            else:
                break
            previously_turned += x[1]
