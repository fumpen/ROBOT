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
                        1: [300, 0]}


class FrindosInnerWorld:
    l_flag = dict
    l_coordinates = dict
    est_coordinate = tuple
    particles = list

    def __init__(self, l_flag, l_coordinates, est_coordinate, particles):
        self.l_flag = l_flag
        self.l_coordinates = l_coordinates
        self.est_coordinate = est_coordinate
        self.particles = particles

    def update_l_flag(self, key):
        if key:
            if self.l_flag[key] == 0:
                self.l_flag[key] = 1

    def update_l_coordinates(self, coordinates):
        self.l_coordinates = coordinates

    def update_est_coordinate(self, est_coordinate):
        self.est_coordinate = est_coordinate

    def update_particles(self, particle):
        self.particles = particle

    def getFlag(self):
        return self.l_flag

    def getLCoordinates(self):
        return self.l_coordinates

    def getEstCoordinates(self):
        return self.est_coordinate

    def getParticles(self):
        return self.particles

particles = p.innit_particles()
innit_est_pose = p.estimate_position(particles)
p.update_particles(particles, cam, 0.0, 0.0, world, WIN_RF1, WIN_World)


def update_landmark(num_landmark):
    if num_landmark == 1:
        LANDMARK[1] = 1
    elif num_landmark == 0:
        LANDMARK[0] = 1


def turn(dir, deg, inner_state):
    m.turn_baby_turn(deg, dir, frindo)
    print '##############'
    print 'turn:'  + str(deg)
    if dir == 'left':
        x = p.update_particles(inner_state.getParticles(), cam, 0.0, deg,
                               world, WIN_RF1, WIN_World)
    else:
        x = p.update_particles(inner_state.getParticles(), cam, 0.0,
                               ((-1.0) * deg), world, WIN_RF1, WIN_World)
    inner_state.update_particles(x['particles'])
    inner_state.update_l_flag(x['obs_obj'][3])
    return x

def go_forward(length, inner_state):
    m.lige_gear(frindo, length)
    x = p.update_particles(inner_state.getParticles(), cam, length, 0.0, world,
                           WIN_RF1, WIN_World)
    inner_state.update_particles(x['particles'])
    inner_state.update_l_flag(x['obs_obj'][3])
    return x

def find_landmark(inner_frindo, previously_moved=0.0):
    """
    :param particles: list of particles
    :param previously_moved: degrees (to mitegate turning more that 360
    :return: RET = [[est_pose, obj, particles], [objectType, measured_distance,
                    measured_angle, integer-rep-of-landmark]]
             degrees_moved: degrees turned to find a landmark
    """
    degrees_moved = previously_moved
    move_pr_turn = 100.0
    while degrees_moved <= 360:
        degrees_moved += move_pr_turn
        ret = turn('right', move_pr_turn, inner_frindo)
        if ret['obs_obj'][3] is not None:
            break
        else:
            ret = None
    return [ret, degrees_moved]

inner_frindo = FrindosInnerWorld(LANDMARK, LANDMARK_COORDINATES,
                                 innit_est_pose, particles)
while True:
    curr_l_flag = inner_frindo.getFlag()
    if curr_l_flag[0] == curr_l_flag[1] == 1:
        print "Found Both landmarks"
        dest = p.where_to_go(p.estimate_position(particles), [0, 150])
        turn(dest[1], dest[2], inner_frindo)
        sleep(0.5)

        go_forward(dest[0], inner_frindo)
        for t in range(1, 3):
            q = find_landmark(inner_frindo)
            if q[0][0]:
                dest = p.where_to_go(q[0][0], [0, 150])
                turn(dest[1], dest[2], inner_frindo)
                sleep(0.5)
                go_forward(dest[0], inner_frindo)
        break
    elif curr_l_flag[0] + curr_l_flag[1] == 1:
        print "Found one landmark!! In elif"
        x = find_landmark(inner_frindo)
        if np.degrees(x[0]['obs_obj'][2]) >= 0.0:
            turn_dir = 'left'
        else:
            turn_dir = 'right'
        x = turn(turn_dir, abs(np.degrees(x[0]['obs_obj'][2])), inner_frindo)
        sleep(0.5)

        if x['obs_obj'][1] > 20.0:
            go_forward(x[0][1][1] - 20.0, inner_frindo)
            sleep(0.5)

        turn('right', 80.0, inner_frindo)
        sleep(0.5)

        go_forward(80.0, inner_frindo)
        sleep(0.5)

        turn('left', 80.0, inner_frindo)
        sleep(0.5)

        go_forward(60.0, inner_frindo)
        particles = x[2]
        previously_turned = 0.0
        while previously_turned <= 360:
            curr_l_flag = inner_frindo.getFlag()
            if curr_l_flag[0] == curr_l_flag[1] != 1:
                x = find_landmark(inner_frindo)
            else:
                break
            previously_turned += x[1]

    else:
        previously_turned = 0.0
        print "Sitting in Else inside while loop"
        while previously_turned <= 360:
            if LANDMARK[0] + LANDMARK[1] != 2:
                x = find_landmark(inner_frindo)
            else:
                break
            previously_turned += x[1]
