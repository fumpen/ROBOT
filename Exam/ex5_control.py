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



# Handles turning the robot along with updating robot knowledge,
# in form of orientation change and
def turn(dir, deg, inner_state):
    m.turn_baby_turn(deg, dir, frindo)
    # print '##############'
    # print 'turn:'  + str(deg)
    if dir == 'left':
        p.update_particles(inner_state.getParticles(), cam, 0.0, deg,
                           world, WIN_RF1, WIN_World)
        obs_prop = p.update_particles(inner_state.getParticles(), cam, 0.0, 0.0,
                               world, WIN_RF1, WIN_World)
    else:
        p.update_particles(inner_state.getParticles(), cam, 0.0, 0.0,
                           world, WIN_RF1, WIN_World)
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
    p.update_particles(inner_state.getParticles(), cam, length, 0.0, world,
                       WIN_RF1, WIN_World)
    obs_prop = p.update_particles(inner_state.getParticles(), cam, 0.0 , 0.0, world,
                                  WIN_RF1, WIN_World)
    inner_state.update_particles(obs_prop['particles'])
    inner_state.update_l_flag(True, obs_prop['obs_obj'][3])
    inner_state.update_est_coordinate((obs_prop['est_pos'].getX(),
                                       obs_prop['est_pos'].getY(),
                                       obs_prop['est_pos'].getTheta()))
    return qwe

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
    while degrees_moved <= 180:
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
    while (inner_state.getEstCoordinates()[0] not in range(goal[0]-40, goal[0]+40)) \
        and (inner_state.getEstCoordinates()[1] not in range(goal[1]-40, goal[1]+40)):
        print 'go_go_go goal: ' + str(goal)
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
        print 'Am in n_l_mark 0'
        for x in range(0, 12):
            print x
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
        print 'Am in n_l_mark 1'
        for x in range(0, 12):
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
        print 'Am in n_l_mark 3'
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
        print 'Am in n_l_mark 3'
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
	print inner_frindo.getEstCoordinates()
        print "Turning ", drive_manual['turn_dir'], "degrees :", drive_manual['turn_degree']
        turn(drive_manual['turn_dir'], abs(drive_manual['turn_degree']), inner_frindo)
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
        # Search for landmarks
        find_landmark(inner_frindo)
        flags = inner_frindo.getFlag()
        # while flags[inner_frindo.getNextLandmark()] != 1:
        #     break #inner_frindo.getEstCoordinates()

        #continue




        # TODO: FIGURE A ROUTE FROM OBSERVED
        #     : FIRST ESTABLISH POSITION (ACCEPT WE KNOW NOTHING)
        #     : Start by resetting landmarks seen
        #     : find at least 1 landmark, drive to if necessary
        #     : find second and or third landmark, figure a route to next landmark
        #     : adjust if obstacles occur,
        #     : however reframe from moving toward previously visitted landmark.



    # if curr_l_flag[0] == curr_l_flag[1] == 1:
    #     print "Found Both landmarks"
    #     dest = p.where_to_go(p.estimate_position(inner_frindo.getParticles()), [0, 150])
    #     turn(dest[1], dest[2], inner_frindo)
    #     sleep(0.5)

    #     go_forward(dest[0], inner_frindo)
    #     for t in range(1, 3):
    #         q = find_landmark(inner_frindo)
    #         if q[0][0]:
    #             dest = p.where_to_go(q[0][0], [0, 150])
    #             turn(dest[1], dest[2], inner_frindo)
    #             sleep(0.5)
    #             go_forward(dest[0], inner_frindo)
    #     break
    # elif curr_l_flag[0] + curr_l_flag[1] == 1:
    #     print "Found one landmark!! In elif"
    #     x = find_landmark(inner_frindo)
    #     if np.degrees(x[0]['obs_obj'][2]) >= 0.0:
    #         turn_dir = 'left'
    #     else:
    #         turn_dir = 'right'
    #     x = turn(turn_dir, abs(np.degrees(x[0]['obs_obj'][2])), inner_frindo)
    #     sleep(0.5)

    #     if x['obs_obj'][1] > 20.0:
    #         go_forward(x[0][1][1] - 20.0, inner_frindo)
    #         sleep(0.5)

    #     turn('right', 80.0, inner_frindo)
    #     sleep(0.5)

    #     go_forward(80.0, inner_frindo)
    #     sleep(0.5)

    #     turn('left', 80.0, inner_frindo)
    #     sleep(0.5)

    #     go_forward(60.0, inner_frindo)
    #     particles = x[2]
    #     previously_turned = 0.0
    #     while previously_turned <= 360:
    #         curr_l_flag = inner_frindo.getFlag()
    #         if curr_l_flag[0] == curr_l_flag[1] != 1:
    #             x = find_landmark(inner_frindo)
    #         else:
    #             break
    #         previously_turned += x[1]

    # else:
    #     # Initial program case, which would only be called if no landmarks have been seen.
    #     # Or in the case that we do not know where we are.
    #     previously_turned = 0.0
    #     print "Sitting in Else inside while loop"
    #     find_landmark(inner_frindo)

        # TODO : ENSURE THAT WE FIND A LANDMARK BEFORE LEAVING THIS CASE
        #        E.G. DRIVE 20 CM AWAY, AND REDO PROCEDURE
"""