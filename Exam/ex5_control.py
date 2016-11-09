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
                 est_coordinate= INIT_POS,
                 particles = p.innit_particles(1000),
                 current_goal = INIT_goal):

        self.l_flag = l_flag
        self.l_coordinates = l_coordinates
        self.est_coordinate = est_coordinate
        self.particles = particles
        self.current_goal = current_goal

    def update_l_flag(self, key):
        print 'update l_flag: ' + str(key)
        if 0 <= key <= 3:
            print 'updated l_flag'
            self.l_flag[key] = 1

    def updateCurrentGoal(self, goal):
        print '###################update_current_goal  with: ' + str(goal)
        if 0 <= goal <= 3:
            self.current_goal[goal] = 1
        else:
            raise
        print 'update_current_goal after update: ' + str(self.current_goal)

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

    def getCurrentGoal(self):
        return self.current_goal

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

    def update_from_update_particle(self, dicte):
        self.update_particles(dicte['particles'])
        self.update_l_flag(dicte['obs_obj'][3])
        print "Print obs_obj[3]: "  + str(dicte['obs_obj'][3])
        if dicte['obs_obj'][3] is not None:
            print "control.update_from_update_particle.obs_obj[1]: " + str(dicte['obs_obj'][1]) + 'landmark: ' + str(dicte['obs_obj'][3])
            if dicte['obs_obj'][1] < 75:
                self.updateCurrentGoal(dicte['obs_obj'][3])
        self.update_est_coordinate((dicte['est_pos'].getX(),
                                    dicte['est_pos'].getY(),
                                    dicte['est_pos'].getTheta()))


#def make_observation(inner_frindo):
#    ret_dict = p.update_particles(inner_frindo.getParticles(), cam, 0.0,
#                              0.0, world, WIN_RF1, WIN_World)
#    inner_frindo.update_from_update_particle(ret_dict)

def turn(dir, deg, inner_frindo):
    m.turn_baby_turn(np.divide(abs(deg), 2), dir, frindo)
    if dir == 'left':
        ret_dict = p.update_particles(inner_frindo.getParticles(), cam, 0.0,
                                      deg, world, WIN_RF1, WIN_World)
    else:
        ret_dict = p.update_particles(inner_frindo.getParticles(), cam, 0.0,
                                    ((-1.0) * deg), world, WIN_RF1, WIN_World)
    if ret_dict['obs_obj'][1]:
        print 'observed landmark nr: ' + str(ret_dict['obs_obj'][3])
    inner_frindo.update_from_update_particle(ret_dict)
    sleep(0.2)
    return ret_dict

def go_forward(length, inner_frindo):
    print 'go_forward length: ' + str(length)

    dist_driven = m.lige_gear_sensor(frindo, length)
    ret_dict = p.update_particles(inner_frindo.getParticles(), cam, length,
                                  0.0, world, WIN_RF1, WIN_World)
    inner_frindo.update_from_update_particle(ret_dict)
    sleep(0.2)
    return dist_driven


def find_landmark(inner_frindo, goal_number):
    """attempt to find a given landmark"""
    dest = p.where_to_go(inner_frindo.getEstCoordinates(),
                         inner_frindo.getLCoordinates()[goal_number])
    ret = turn(dest['dir'], dest['deg'], inner_frindo)
    degrees_moved = 0.0
    move_pr_turn = 35.0
    goal = False
    while degrees_moved <= 360:
        degrees_moved += move_pr_turn+10
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


def go_go_go(frindo, inner_frindo, goal):
    """ go to a specific point (probably a landmark) """
    """ Runs until robot thinks we're safely within range """
    while p.dist_between_points(goal, inner_frindo.getEstCoordinates()) > 50:
        # (inner_frindo.getEstCoordinates()[0] not in range(goal[0]-50, goal[0]+50)) \
        #     and (inner_frindo.getEstCoordinates()[1] not in range(goal[1]-50, goal[1]+50)):
        dest = p.where_to_go(inner_frindo.getEstCoordinates(), goal)
        turn(dest['dir'], abs(dest['deg']), inner_frindo)
        if 0 < (dest['dist'] - 50.0) < 50:
            print "GOING FORWARD IN GOGOGO NOT KNOWING ANYTHING"
            turn(dest['dir'], dest['deg'], inner_frindo)
            ret = go_forward(20.0, inner_frindo)
        elif 50 <= (dest['dist'] - 50.0):
            print "GOING FORWARD IN GOGOGO NOT KNOWING ANYTHING"
            turn(dest['dir'], dest['deg'], inner_frindo)
            ret = go_forward((dest['dist'] - 50.0), inner_frindo)
        else:
            print "KAMIKAZE!!"
            turn(rl_wuuut(dest['dir']), abs(180.0 - dest['deg']), inner_frindo)
            go_forward(20.0, inner_frindo)
            break
        # print 'go_go_go goal: ' + str(goal)
        # print 'ret (go_go_go if-statement):' + str(ret)
        # print 'dest[dist] (go_go_go if-statement):' + str(dest['dist'])

        if ret != 20.0:
            right, left, forward = s.determine_way_around(frindo)
            print 'right, left, forward (go_go_go):' , str(right) , str(left) , str(forward)
            if right or forward:
                print 'collision detect'
                if right:
                    while forward or right:
                        turn('left', 10, inner_frindo)
                        right, left, forward = s.determine_way_around(frindo)

                    #while right:
                    go_forward(40, inner_frindo)
                    #right, left, forward = s.determine_way_around(frindo)
                    turn('right', 30, inner_frindo)
                    go_forward(40, inner_frindo)
                else:
                    turn('left', 30, inner_frindo)
                    go_forward(40, inner_frindo)
            elif left:
                print 'collision detect'
                if forward:
                    while forward or left:
                        turn('right', 10, inner_frindo)
                        right, left, forward = s.determine_way_around(frindo)
                    # while right:
                    #     go_forward(20, inner_frindo)
                    #     right, left, forward = s.determine_way_around(frindo)
                    turn('left', 30, inner_frindo)
                    go_forward(40, inner_frindo)
                else:
                    turn('right', 30, inner_frindo)
                    go_forward(20, inner_frindo)
            recon_area(15, 15, inner_frindo, goal)
        if inner_frindo.getFlag()[goal] == 1:
            break


def recon_area(turns, deg, inner_frindo, goal):
    inner_frindo.reset_landmarks()
    for x in range(0, turns):
        turn('right', deg, inner_frindo)
        if inner_frindo.getFlag()[goal] == 1:
            break

def start_observations(turns, deg, inner_frindo):
    inner_frindo.reset_landmarks()
    ret_dict = p.update_particles(inner_frindo.getParticles(), cam, 0.0,
    	                          0.0, world, WIN_RF1, WIN_World)
    inner_frindo.update_from_update_particle(ret_dict)
    for x in range(0, turns):
        turn('right', deg, inner_frindo)

def move_logic(turn_times, turn_deg, inner_frindo, goal):
    print 'current goal: ' + str(goal)
    ret_obj = find_landmark(inner_frindo, goal)
    if ret_obj['goal']:
        if 0 < (ret_obj['dist'] - 50.0) < 50:
            print "GOING FORWARD(short) KNOWING WHERE THE BOX IS"
            turn(ret_obj['dir'], ret_obj['deg'], inner_frindo)
            go_forward(20, inner_frindo)
        elif 50 <= (ret_obj['dist'] - 50.0):
            print "GOING FORWARD(long) KNOWING WHERE THE BOX IS"
            turn(ret_obj['dir'], ret_obj['deg'], inner_frindo)
            go_forward((ret_obj['dist'] - 50.0), inner_frindo)
        else:
            print "IM TOO CLOSE TO THE DANM BOX"
            turn(rl_wuuut(ret_obj['dir']), abs(180 - ret_obj['deg']), inner_frindo)
            go_forward(20, inner_frindo)
    elif inner_frindo.sum_of_observed_landmarks() >= 2:
        go_go_go(frindo, inner_frindo, inner_frindo.getLCoordinates()[goal])
    else:
        print 'FUCK'
        go_forward(30, inner_frindo)
        recon_area(turn_times, turn_deg, inner_frindo, goal)
    print 'getFlag: ' + str(inner_frindo.getFlag())


inner_frindo = FrindosInnerWorld()
current_goal = inner_frindo.getCurrentGoal()
turn_times = 15
turn_deg = 25
dest = p.where_to_go((100, 100, np.radians(0)), [0,0])
turn(dest['dir'], abs(dest['deg']), inner_frindo)
#start_observations(turn_times, turn_deg, inner_frindo)
#while current_goal[0] != 1:
#    print 'current_goal: ' + str(current_goal)
#    move_logic(turn_times, turn_deg, inner_frindo, 0)
#    current_goal = inner_frindo.getCurrentGoal()
#while current_goal[1] != 1:
#    print 'current_goal: ' + str(current_goal)
#    move_logic(turn_times, turn_deg, inner_frindo, 1)
#    current_goal = inner_frindo.getCurrentGoal()
#while current_goal[2] != 1:
#    print 'current_goal: ' + str(current_goal)
#    move_logic(turn_times, turn_deg, inner_frindo, 2)
#    current_goal = inner_frindo.getCurrentGoal()
#while current_goal[3] != 1:
#    print 'current_goal: ' + str(current_goal)
#    move_logic(turn_times, turn_deg, inner_frindo, 3)
#    current_goal = inner_frindo.getCurrentGoal()
