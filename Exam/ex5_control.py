import ex5_i_love_brainz as p
import moves as m
import robot
import camera
import numpy as np
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
    """This class keeps track of where the frindo thinks it is"""
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


def turn(dir, deg, inner_state):
    """Handles turning the robot along with updating robot knowledge,
    in form of orientation change"""
    print 'turn_deg (control.py turn(): ' + str(deg)
    m.turn_baby_turn(abs(deg), dir, frindo)
    if dir == 'left':
        obs_prop = p.update_particles(inner_state.getParticles(), cam, 0.0,
                                      deg, world, WIN_RF1, WIN_World)
    else:
        obs_prop = p.update_particles(inner_state.getParticles(), cam, 0.0,
                                      ((-1.0) * deg), world, WIN_RF1,
                                      WIN_World)
    inner_state.update_particles(obs_prop['particles'])
    inner_state.update_l_flag(obs_prop['obs_obj'][3])
    if obs_prop['obs_obj'][3] is not None:
        if obs_prop['obs_obj'][1] < 75:
            inner_state.update_next_l(obs_prop['obs_obj'][3])
    inner_state.update_est_coordinate((obs_prop['est_pos'].getX(),
                                       obs_prop['est_pos'].getY(),
                                       obs_prop['est_pos'].getTheta()))
    return obs_prop

def go_forward(length, inner_state):
    """move the robot forward at set distance and updates inner values"""
    dist_driven = m.lige_gear_sensor(frindo, length)
    obs_prop = p.update_particles(inner_state.getParticles(), cam, length, 0.0,
                                  world, WIN_RF1, WIN_World)

    if obs_prop['obs_obj'][3] is not None:
        if obs_prop['obs_obj'][1] < 75:
            inner_state.update_next_l(obs_prop['obs_obj'][3])
    inner_state.update_particles(obs_prop['particles'])
    inner_state.update_l_flag(obs_prop['obs_obj'][3])
    inner_state.update_est_coordinate((obs_prop['est_pos'].getX(),
                                       obs_prop['est_pos'].getY(),
                                       obs_prop['est_pos'].getTheta()))
    return dist_driven


def find_landmark(inner_frindo, goal_number):
    """attempt to find a given landmark"""
    dest = p.where_to_go(inner_frindo.getEstCoordinates(),
                         inner_frindo.getLCoordinates()[goal_number])
    ret = turn(dest['turn_dir'], dest['turn_degree'], inner_frindo)
    degrees_moved = 0.0
    move_pr_turn = 25.0
    goal = False
    if ret['obs_obj'][3]:
        if ret['obs_obj'][3] == goal_number:
            goal = True
    if goal:
        dist = ret['obs_obj'][1]
        if ret['obs_obj'][2] < 0:
            dir = 'right'
        else:
            dir = 'left'
        deg = ret['obs_obj'][2]
    else:
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



def go_go_go(frindo, inner_frindo, goal):
    """go to a specific point (probably a landmark)"""
    dest = p.where_to_go(inner_frindo.getEstCoordinates(), goal)
    turn(dest['turn_dir'], dest['turn_degree'], inner_frindo)
    while (inner_frindo.getEstCoordinates()[0] not in range(goal[0]-40, goal[0]+40)) \
        and (inner_frindo.getEstCoordinates()[1] not in range(goal[1]-40, goal[1]+40)):
        ret = go_forward(dest['dist'], inner_frindo)
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
                        turn('left', 20, inner_frindo)
                        right, left, forward = s.determine_way_around(frindo)
                    while right:
                        go_forward(20, inner_frindo)
                        right, left, forward = s.determine_way_around(frindo)
                    turn('right', 20, inner_frindo)
                    go_forward(20, inner_frindo)
                else:
                    turn('left', 30, inner_frindo)
                    go_forward(20, inner_frindo)
            elif left:
                print 'collision detect'
                if forward:
                    while forward or left:
                        turn('right', 20, inner_frindo)
                        right, left, forward = s.determine_way_around(frindo)
                    while right:
                        go_forward(20, inner_frindo)
                        right, left, forward = s.determine_way_around(frindo)
                    turn('left', 20, inner_frindo)
                    go_forward(20, inner_frindo)
                else:
                    turn('right', 30, inner_frindo)
                    go_forward(20, inner_frindo)


def recon_area(turns, deg):
    for x in range(0, turns):
        turn('right', deg, inner_frindo)


inner_frindo = FrindosInnerWorld()
sum_mark = inner_frindo.sum_of_checklist_landmarks()
n_l_mark = inner_frindo.getNextLandmark()
turn_times = 10
turn_deg = 15
while sum_mark < 4:
    print 'checklist: ' + str(inner_frindo.getNextLandmark())
    if n_l_mark[0] < 1:
        print 'Am in n_l_mark 0'
        recon_area(turn_times, turn_deg)
        if inner_frindo.getFlag()[0] == 1:
            ret_obj = find_landmark(inner_frindo, 0)
            if ret_obj['goal']:
                turn(ret_obj['dir'], ret_obj['deg'], inner_frindo)
                go_forward(ret_obj['dist'], inner_frindo)
        elif inner_frindo.sum_of_observed_landmarks() < 2:
            go_go_go(frindo, inner_frindo, inner_frindo.getLCoordinates()[0])
            recon_area(turn_times, turn_deg)
        else:
            print 'FUCK'
            go_forward(30, inner_frindo)
        print 'getFlag: ' + str(inner_frindo.getFlag())
    elif n_l_mark[1] < 1:
        print 'Am in n_l_mark 1'
        recon_area(turn_times, turn_deg)
        if inner_frindo.sum_of_observed_landmarks() < 2:
            go_go_go(frindo, inner_frindo, inner_frindo.getLCoordinates()[1])
            recon_area(turn_times, turn_deg)
        else:
            print 'FUCK'
            go_forward(30, inner_frindo)
    elif n_l_mark[2] < 1:
        print 'Am in n_l_mark 3'
        recon_area(turn_times, turn_deg)
        if inner_frindo.sum_of_observed_landmarks() < 2:
            go_go_go(frindo, inner_frindo, inner_frindo.getLCoordinates()[2])
            recon_area(turn_times, turn_deg)
        else:
            print 'FUCK'
            go_forward(30, inner_frindo)
    else:
        print 'Am in n_l_mark 3'
        recon_area(turn_times, turn_deg)
        if inner_frindo.sum_of_observed_landmarks() < 2:
            go_go_go(frindo, inner_frindo, inner_frindo.getLCoordinates()[3])
            recon_area(turn_times, turn_deg)
        else:
            print 'FUCK'
            go_forward(30, inner_frindo)

    inner_frindo.reset_landmarks()
    sum_mark = inner_frindo.sum_of_checklist_landmarks()
    n_l_mark = inner_frindo.getNextLandmark()
