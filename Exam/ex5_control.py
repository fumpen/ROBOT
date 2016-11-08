import ex5_i_love_brainz as p
import moves as m
import robot
import camera
import random
import numpy as np
import math
from time import sleep
import cv2
import sensor as s


# Configuration setup
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
            1: 0,
	    2: 0,
	    3: 0}

LANDMARK_COORDINATES = {0: [0, 0],
                        1: [300, 0],
			            2: [0, 300],
			            3: [300, 300]}

INIT_POS = (0,0,np.radians(0))

class FrindosInnerWorld:

    l_flag = dict
    l_coordinates = dict
    est_coordinate = tuple
    particles = list
    next_l = int

    def __init__(self, l_flag = LANDMARK, l_coordinates = LANDMARK_COORDINATES, est_coordinate= INIT_POS, particles = p.innit_particles(1000), next_l=0):
        self.l_flag = l_flag
        self.l_coordinates = l_coordinates
        self.est_coordinate = est_coordinate
        self.particles = particles
        self.next_l = next_l

    def update_l_flag(self, key, mark):
        if key:
            self.l_flag[mark] = 1
        else:
            self.l_flag[mark] = 0

    def update_next_l(self):
        self.next_l += 1

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

    def getNextLandmark(self):
        return self.next_l

    def reset_landmarks(self):
        for x in range(0, 4):
            self.l_flag[x] = 0

    def sum_of_observed_landmarks(self):
        y = 0
        for x in range(0, 4):
            y += self.l_flag[x]
        return y


# Handles turning the robot along with updating robot knowledge,
# in form of orientation change and
def turn(dir, deg, inner_state):
    m.turn_baby_turn(deg, dir, frindo)
    # print '##############'
    # print 'turn:'  + str(deg)
    if dir == 'left':
        obs_prop = p.update_particles(inner_state.getParticles(), cam, 0.0, deg,
                               world, WIN_RF1, WIN_World)
    else:
        obs_prop = p.update_particles(inner_state.getParticles(), cam, 0.0,
                               ((-1.0) * deg), world, WIN_RF1, WIN_World)
    inner_state.update_particles(obs_prop['particles'])
    inner_state.update_l_flag(True, obs_prop['obs_obj'][3])
    inner_state.update_est_coordinate((obs_prop['est_pos'].getX(),
                                       obs_prop['est_pos'].getY(),
                                       obs_prop['est_pos'].getTheta()))
    return obs_prop

def go_forward(length, inner_state):
    qwe = m.lige_gear_sensor(frindo, length)
    obs_prop = p.update_particles(inner_state.getParticles(), cam, length, 0.0, world,
                                  WIN_RF1, WIN_World)
    inner_state.update_particles(obs_prop['particles'])
    inner_state.update_l_flag(True, obs_prop['obs_obj'][3])
    inner_state.update_est_coordinate((obs_prop['est_pos'].getX(),
                                       obs_prop['est_pos'].getY(),
                                       obs_prop['est_pos'].getTheta()))
    return obs_prop

def find_landmark(inner_frindo, previously_moved=0.0):
    """
    :param particles: list of particles
    :param previously_moved: degrees (to mitegate turning more that 360
    :return: RET = [[est_pose, obj, particles], [objectType, measured_distance,
                    measured_angle, integer-rep-of-landmark]]
             degrees_moved: degrees turned to find a landmark
    """
    degrees_moved = previously_moved
    move_pr_turn = 25.0
    while degrees_moved <= 360:
        degrees_moved += move_pr_turn
        ret = turn('right', move_pr_turn, inner_frindo)
        if ret['obs_obj'][3] is not None:
            print "found :", ret['obs_obj']
            continue
        else:
            ret = None
    return [ret, degrees_moved]

def reset_marks_seen():
    for i in range(0,4):
        inner_frindo.update_l_flag(False, i)

# Initialize particles and update
inner_frindo = FrindosInnerWorld()

#particles = p.innit_particles(1000)
innit_est_pose = p.estimate_position(inner_frindo.getParticles())
# ONLY FOR TESTING TO VIEW ROBOT POSITION
#p.update_particles(particles, cam, 0.0, 0.0, world, WIN_RF1, WIN_World)

# Initializes Frindo Inner World class
#return 0


def go_go_go (frindo, inner_state, goal):
    dest = p.where_to_go(inner_state.getEstCoordinates(), goal)
    turn(frindo, dest[1], dest[2])
    while (inner_state.getEstCoordinates()[0] not in range(goal[0]-30, goal[0]+30)) \
        and (inner_state.getEstCoordinates()[1] not in range(goal[1]-30, goal[1]+30)):
        ret = go_forward(dest[0], inner_state)
        if ret != dest[0]:
            right, left, forward = s.determine_way_around(frindo)
            if right or forward:
                if left:
                    while forward or left:
                        turn('left', 20, inner_state)
                        right, left, forward = s.determine_way_around(frindo)
                    while right:
                        go_forward(20, inner_state)
                        right, left, forward = s.determine_way_around(frindo)
                    turn('right', 20, inner_state)
                    go_forward(20, inner_state)
                    right, left, forward = s.determine_way_around(frindo)
                else:
                    turn('left', 30, inner_state)
                    go_forward(20, inner_state)
            elif left:
                if forward:
                    while forward or left:
                        turn('right', 20, inner_state)
                        right, left, forward = s.determine_way_around(frindo)
                    while right:
                        go_forward(20, inner_state)
                        right, left, forward = s.determine_way_around(frindo)
                    turn('left', 20, inner_state)
                    go_forward(20, inner_state)
                else:
                    turn('right', 30, inner_state)
                    go_forward(20, inner_state)

n_l_mark = inner_frindo.getNextLandmark()
while n_l_mark < 4:
    if n_l_mark == 0:
        for x in range(0, 12):
            find_landmark(inner_frindo, 0)
        if inner_frindo.getFlag()[0] == 1:
            go_go_go(frindo, inner_frindo, inner_frindo.getLCoordinates()[0])
            for x in range(0, 12):
                find_landmark(inner_frindo, 0)
        elif inner_frindo.sum_of_observed_landmarks() > 1:
            print 'FUCK'
            go_forward(30, inner_frindo)
        inner_frindo.reset_landmarks()
    elif n_l_mark == 1:
        for x in range(0, 12) :
            find_landmark(inner_frindo, 0)
        if inner_frindo.getFlag()[0] == 1:
            go_go_go(frindo, inner_frindo, inner_frindo.getLCoordinates()[1])
            for x in range(0, 12):
                find_landmark(inner_frindo, 0)
        elif inner_frindo.sum_of_observed_landmarks() > 1:
            print 'FUCK'
            go_forward(30, inner_frindo)
        inner_frindo.reset_landmarks()
    elif n_l_mark == 2:
        for x in range(0, 12) :
            find_landmark(inner_frindo, 0)
        if inner_frindo.getFlag()[0] == 1:
            go_go_go(frindo, inner_frindo, inner_frindo.getLCoordinates()[2])
            for x in range(0, 12):
                find_landmark(inner_frindo, 0)
        elif inner_frindo.sum_of_observed_landmarks() > 1:
            print 'FUCK'
            go_forward(30, inner_frindo)
        inner_frindo.reset_landmarks()
    else:
        for x in range(0, 12) :
            find_landmark(inner_frindo, 0)
        if inner_frindo.getFlag()[0] == 1:
            go_go_go(frindo, inner_frindo, inner_frindo.getLCoordinates()[3])
            for x in range(0, 12):
                find_landmark(inner_frindo, 0)
        elif inner_frindo.sum_of_observed_landmarks() > 1:
            print 'FUCK'
            go_forward(30, inner_frindo)
        inner_frindo.reset_landmarks()

    n_l_mark = inner_frindo.getNextLandmark()

"""
while True:
    curr_l_flag = inner_frindo.getFlag()
    # TODO : implement for multiple landmarks, not only 2.
    #if inner_frindo.getFlag[inner_frindo.getNextLandmark] == 1:
        # TODO: DRIVE TO LANDMARK!
    #else:
    # TODO : IF WE CAN SEE FROM OUR CURRENT POSITION, THE WISHED LANDMARK, drive to it.
    next_mark = inner_frindo.getNextLandmark()
    print "LOOKING FOR MARK", curr_l_flag[next_mark]
    if curr_l_flag[next_mark] == 1:
        # TODO: DRIVE TO LANDMARK!
        #     :
        drive_manual = p.where_to_go(inner_frindo.getEstCoordinates(), inner_frindo.getLCoordinates()[next_mark])
        print drive_manual
        print "Turning ", drive_manual['turn_dir'], "degrees :", drive_manual['turn_degree']
        turn(drive_manual['turn_dir'], drive_manual['turn_degree'], inner_frindo)
        #go_forward(drive_manual['dist'], inner_frindo)
        p.update_particles(inner_frindo.getParticles(), cam, 0.0, 0.0, world,
                                  WIN_RF1, WIN_World)
        p.update_particles(inner_frindo.getParticles(), cam, 0.0, 0.0, world,
                                  WIN_RF1, WIN_World)
        p.update_particles(inner_frindo.getParticles(), cam, 0.0, 0.0, world,
                                  WIN_RF1, WIN_World)
        if raw_input() == 'w':
            break

    else:
        print "reached hard reset"
        # re-establish location
        reset_marks_seen()
        find_landmark(inner_frindo)
        flags = inner_frindo.getFlag()
"""