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

innit_landmark_list = [0, 0, 0, 0]

class FrindosInnerWorld:

    l_flag = dict
    l_coordinates = dict
    est_coordinate = tuple
    particles = list
    landmark_checklist = list

    def __init__(self, l_flag = LANDMARK, l_coordinates = LANDMARK_COORDINATES,
                 est_coordinate= INIT_POS, particles = p.innit_particles(1000),
                 landmark_checklist = innit_landmark_list):
        self.l_flag = l_flag
        self.l_coordinates = l_coordinates
        self.est_coordinate = est_coordinate
        self.particles = particles
        self.landmark_checklist = landmark_checklist

    def update_l_flag(self, key):
        print 'update l_flag: ' + str(key)
        if 0 <= key <= 3:
            print 'updated l_flag'
            self.l_flag[key] = 1

    def update_next_l(self, list_index):
        self.landmark_checklist[list_index] = 1

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
        return self.landmark_checklist

    def reset_landmarks(self):
        x = 0
        while x < 4:
            self.l_flag[x] = 0
            x += 1
    def sum_of_observed_landmarks(self):
        x = 0
        for key, val in self.l_flag.iteritems():
            x += val
        return x

    def sum_of_checklist_landmarks(self):
        x = 0
        for val in self.landmark_checklist:
           x += val
        return x

        # Handles turning the robot along with updating robot knowledge,
# in form of orientation change and
def turn(dir, deg, inner_state):
    print 'turn_deg (control.py turn(): ' + str(deg)
    m.turn_baby_turn(abs(deg), dir, frindo)
    # print '##############'
    # print 'turn:'  + str(deg)
    if dir == 'left':
        obs_prop = p.update_particles(inner_state.getParticles(), cam, 0.0,
                                      deg, world, WIN_RF1, WIN_World)
    else:
        obs_prop = p.update_particles(inner_state.getParticles(), cam, 0.0,
                               ((-1.0) * deg), world, WIN_RF1, WIN_World)
    inner_state.update_particles(obs_prop['particles'])
    inner_state.update_l_flag(obs_prop['obs_obj'][3])
    if obs_prop['obs_obj'][3]:
        if obs_prop['obs_obj'][1] < 75:
            inner_state.update_next_l(obs_prop['obs_obj'][3])
    inner_state.update_est_coordinate((obs_prop['est_pos'].getX(),
                                       obs_prop['est_pos'].getY(),
                                       obs_prop['est_pos'].getTheta()))
    return obs_prop

def go_forward(length, inner_state):
    dist_driven = m.lige_gear_sensor(frindo, length)
    obs_prop =p.update_particles(inner_state.getParticles(), cam, length, 0.0, world,
                       WIN_RF1, WIN_World)

    if obs_prop['obs_obj'][3]:
        if obs_prop['obs_obj'][1] > 75:
            inner_state.update_next_l(obs_prop['obs_obj'][3])
    inner_state.update_particles(obs_prop['particles'])
    inner_state.update_l_flag(obs_prop['obs_obj'][3])
    inner_state.update_est_coordinate((obs_prop['est_pos'].getX(),
                                       obs_prop['est_pos'].getY(),
                                       obs_prop['est_pos'].getTheta()))
    return dist_driven


def find_landmark(inner_frindo, goal_number):
    degrees_moved = 0.0
    move_pr_turn = 25.0
    goal = False
    while degrees_moved <= 360:
        degrees_moved += move_pr_turn
        ret = turn('right', move_pr_turn, inner_frindo)
        if ret['obs_obj'][3] is not None:
            print "found :", ret['obs_obj']
            if ret['obs_obj'][3] == goal_number:
                goal = True
                break
        else:
            ret = None
    if goal:
        dist = ret['obs_obj'][1]
        if ret['obs_obj'][2] < 0:
            dir = 'right'
        else:
            dir = 'left'
        deg = ret['obs_obj'][2]
    else:
        dist = None
        dir = None
        deg = None
    return {'dist': dist, 'dir': dir, 'deg': deg, 'goal': goal}


# Initialize particles and update
inner_frindo = FrindosInnerWorld()

#particles = p.innit_particles(1000)
innit_est_pose = p.estimate_position(inner_frindo.getParticles())

# Initializes Frindo Inner World class
#return 0

def go_go_go (frindo, inner_state, goal):
    dest = p.where_to_go(inner_state.getEstCoordinates(), goal)
    turn(dest['turn_dir'], dest['turn_degree'], inner_state)
    while (inner_state.getEstCoordinates()[0] not in range(goal[0]-40, goal[0]+40)) \
        and (inner_state.getEstCoordinates()[1] not in range(goal[1]-40, goal[1]+40)):
        ret = go_forward(dest['dist'], inner_state)
        print 'go_go_go goal: ' + str(goal)
        print 'ret (go_go_go if-statement):' + str(ret)
        print 'dest[dist] (go_go_go if-statement):' + str(dest['dist'])
        if ret != dest['dist']:
            right, left, forward = s.determine_way_around(frindo)
            print 'right, left, forward (go_go_go):' + str(right) + ', ' + str(left) + ', ' + str(forward)
            if right or forward:
                print 'collision detect'
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
                print 'collision detect'
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

sum_mark = inner_frindo.sum_of_checklist_landmarks()
n_l_mark = inner_frindo.getNextLandmark()
turn_times = 10
turn_deg = 15
while sum_mark < 4:
    print 'checklist: ' + str(inner_frindo.getNextLandmark())
    if n_l_mark[0] < 1:
        print 'Am in n_l_mark 0'
        for x in range(0, turn_times):
            turn('right', turn_deg, inner_frindo)
        if inner_frindo.getFlag()[0] == 1:
            ret_obj = find_landmark(inner_frindo, 0)
            if ret_obj['goal']:
                turn(ret_obj['dir'], ret_obj['deg'], inner_frindo)
                go_forward(ret_obj['dist'])
        elif inner_frindo.sum_of_observed_landmarks() < 2:
            go_go_go(frindo, inner_frindo, inner_frindo.getLCoordinates()[0])
            for x in range(0, turn_times):
                turn('right', 25, inner_frindo)
        else:
            print 'FUCK'
            go_forward(30, inner_frindo)
        print 'getFlag: ' + str(inner_frindo.getFlag())
        inner_frindo.reset_landmarks()
    elif n_l_mark[1] < 1:
        print 'Am in n_l_mark 1'
        for x in range(0, turn_times):
            turn('right', turn_deg, inner_frindo)
        if inner_frindo.sum_of_observed_landmarks() < 2:
            go_go_go(frindo, inner_frindo, inner_frindo.getLCoordinates()[1])
            for x in range(0, turn_times):
                turn('right', 25, inner_frindo)
        else:
            print 'FUCK'
            go_forward(30, inner_frindo)
        inner_frindo.reset_landmarks()
    elif n_l_mark[2] < 1:
        print 'Am in n_l_mark 3'
        for x in range(0, turn_times):
            turn('right', turn_deg, inner_frindo)
        if inner_frindo.sum_of_observed_landmarks() < 2:
            go_go_go(frindo, inner_frindo, inner_frindo.getLCoordinates()[2])
            for x in range(0, turn_times):
                turn('right', turn_deg, inner_frindo)
        else:
            print 'FUCK'
            go_forward(30, inner_frindo)
        inner_frindo.reset_landmarks()
    else:
        print 'Am in n_l_mark 3'
        for x in range(0, turn_times):
            turn('right', turn_deg, inner_frindo)
        if inner_frindo.sum_of_observed_landmarks() < 2:
            go_go_go(frindo, inner_frindo, inner_frindo.getLCoordinates()[3])
            for x in range(0, turn_times):
                turn('right', turn_deg, inner_frindo)
        else:
            print 'FUCK'
            go_forward(30, inner_frindo)
        inner_frindo.reset_landmarks()
        
    sum_mark = inner_frindo.sum_of_checklist_landmarks()
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
