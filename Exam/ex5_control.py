import ex5_i_love_brainz as p
import moves as m
import robot
import camera
import numpy as np
import cv2
import sensor as s
from time import sleep

# Configuration setup
frindo = robot.Robot()
cam = camera.Camera(0, 'frindo')
world = np.zeros((500, 500, 3), dtype=np.uint8)
WIN_RF1 = "Robot view"
cv2.namedWindow(WIN_RF1)
cv2.moveWindow(WIN_RF1, 50, 50)

WIN_World = "World view"
cv2.namedWindow(WIN_World)
cv2.moveWindow(WIN_World, 700, 50)

LANDMARK = {0: 0,
            1: 0,
            2: 0,
            3: 0}

LANDMARK_COORDINATES = {0: [0, 0],
                        1: [300, 0],
                        2: [0, 300],
                        3: [300, 300]}

INIT_POS = (0, 0, np.radians(0))

INIT_goal = [0, 0, 0, 0]

def rl_wuuut(dir):
    if dir == 'right':
        return 'left'
    else:
        return 'right'

class FrindosInnerWorld:
    """This class keeps track of where the frindo thinks it is"""
    l_flag = dict
    l_coordinates = dict
    est_coordinate = tuple
    particles = list
    current_goal = list

    def __init__(self,
                 l_flag = LANDMARK,
                 l_coordinates = LANDMARK_COORDINATES,
                 est_coordinate= INIT_POS,print "GOING FORWARD IN GOGOGO NOT KNOWING ANYTHING"
            turn(dest['dir'], dest['deg'], inner_frindo)
            ret = go_forward((dest['dist'] - 50.0), inner_frindo)
        else:
            print "IN GOGOGO AND THINK IM CLOSE?"
            recon_area(25, 10, inner_frindo, goal)
            break

        if ret != (dest['dist'] - 50.0):
            right, left, forward = s.determine_way_around(frindo)
            print 'right, left, forward (go_go_go):' , str(right) , str(left) , str(forward)
            if right or forward:
                print 'collision detect'
                if right:
                    while forward or left:
                        turn('left', 20, inner_frindo)
                        right, left, forward = s.determine_way_around(frindo)
                    while right:
                        go_forward(20, inner_frindo)
                        right, left, forward = s.determine_way_around(frindo)
                    turn('right', 30, inner_frindo)
                    go_forward(40, inner_frindo)
                else:
                    turn('left', 30, inner_frindo)
                    go_forward(40, inner_frindo)
            elif left:
                print 'collision detect'
                if forward:
                    while forward or left:
                        turn('right', 20, inner_frindo)
                        right, left, forward = s.determine_way_around(frindo)
                    while left:
                        go_forward(20, inner_frindo)
                        right, left, forward = s.determine_way_around(frindo)
                    turn('left', 30, inner_frindo)
                    go_forward(40, inner_frindo)
                else:
                    turn('right', 30, inner_frindo)
                    go_forward(20, inner_frindo)
            recon_area(15, 15, inner_frindo, goal)
        if inner_frindo.getFlag()[goal] == 1:
            break


def recon_area(turns, deg, inner_frindo, goal_nr):
    print '### recon_area ###'
    inner_frindo.reset_landmarks()
    for x in range(0, turns):
        turn('right', deg, inner_frindo)
        print 'RECON AREA: ' + str(goal_nr)
        if inner_frindo.getFlag()[goal_nr] == 1:
            break


def start_observations(turns, deg, inner_frindo):
    print '### start_observation ###'
    landmark1_counter = 0
    inner_frindo.reset_landmarks()
    ret_dict = p.update_particles(inner_frindo.getParticles(), cam, 0.0,
    	                          0.0, world, WIN_RF1, WIN_World)
    if ret_dict['obs_obj'][3] == 0:
        landmark1_counter += 1

    inner_frindo.update_from_update_particle(ret_dict)
    
    for x in range(0, turns):
        ret_dict = turn('right', deg, inner_frindo)
        if ret_dict['obs_obj'][3] == 0:
            landmark1_counter += 1
        if landmark1_counter > 1:
            break
            

def move_logic(turn_times, turn_deg, inner_frindo, goal):
    print '### move_logic ### current goal: ' + str(goal)
    ret_obj = find_landmark(inner_frindo, goal)
    if ret_obj['goal']:
        if 50 <= (ret_obj['dist'] - 50.0):
            print "GOING FORWARD(long) KNOWING WHERE THE BOX IS"
            print 'IF GOAL: ' + str(goal)
            turn(ret_obj['dir'], ret_obj['deg'], inner_frindo)
            go_forward((ret_obj['dist'] - 50.0), inner_frindo)
        else:
            print 'ELSE GOAL: ' + str(goal)
            current_goal = inner_frindo.getCurrentGoal()
            if current_goal[goal] == 1:
                pass
            else:
                recon_area(turn_times, turn_deg, inner_frindo, goal)
            # print "IM TOO CLOSE TO THE DANM BOX"
            # turn(rl_wuuut(ret_obj['dir']), abs(180 - ret_obj['deg']), inner_frindo)
            # go_forward(20, inner_frindo)
    elif inner_frindo.sum_of_observed_landmarks() >= 2:
        print 'ELIF GOAL: ' + str(goal)
        go_go_go(frindo, inner_frindo, inner_frindo.getLCoordinates()[goal], goal)
    else:
        print 'FUCK'
        print 'ELSE(fuck) GOAL: ' + str(goal)
        go_forward(30, inner_frindo)
        recon_area(turn_times, turn_deg, inner_frindo, goal)
    print 'getFlag: ' + str(inner_frindo.getFlag())


inner_frindo = FrindosInnerWorld()
current_goal = inner_frindo.getCurrentGoal()
turn_times = 15
turn_deg = 35
start_observations(turn_times, turn_deg, inner_frindo)
while current_goal[0] != 1:
    print '### while loop 0 ### current_goal: ' + str(current_goal)
    move_logic(turn_times, turn_deg, inner_frindo, 0)
    current_goal = inner_frindo.getCurrentGoal()
while current_goal[1] != 1:
    print '### while loop 1 ### current_goal: ' + str(current_goal)
    move_logic(turn_times, turn_deg, inner_frindo, 1)
    current_goal = inner_frindo.getCurrentGoal()
while current_goal[2] != 1:
    print '### while loop 2 ### current_goal: ' + str(current_goal)
    move_logic(turn_times, turn_deg, inner_frindo, 2)
    current_goal = inner_frindo.getCurrentGoal()
while current_goal[3] != 1:
    print '### while loop 3 ### current_goal: ' + str(current_goal)
    move_logic(turn_times, turn_deg, inner_frindo, 3)
    current_goal = inner_frindo.getCurrentGoal()
