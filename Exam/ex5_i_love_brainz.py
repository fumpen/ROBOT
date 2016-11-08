import cv2
import particle
import camera
import random
import numpy as np
import math


# Some colors constants
CRED = (0, 0, 255)
CGREEN = (0, 255, 0)
CBLUE = (255, 0, 0)
CCYAN = (255, 255, 0)
CYELLOW = (0, 255, 255)
CMAGENTA = (255, 0, 255)
CWHITE = (255, 255, 255)
CBLACK = (0, 0, 0)

# Landmarks.
# The robot knows the position of 2 landmarks. Their coordinates are in cm.
landmarks = [(0, 0), (300, 0), (0, 300), (300, 300)]



def add_to_angular_v2(present, delta):
    # Ensures that the orientation of the particle stays in range 0-360
    new_angle = present + delta
    if new_angle >= 180.0:
        new_angle = new_angle - 360.0
    elif new_angle < -180.0:
        new_angle = new_angle + 360.0
    return np.radians(new_angle)


def particle_landmark_vector(mark, particle):
    (mark_x, mark_y) = landmarks[mark]
    x = mark_x - particle.getX()
    y = -1.0 * (mark_y - particle.getY())
    return [x, y]

def particle_landmark_vector_v2(mark, vector):
    #(mark_x, mark_y) = landmarks[mark]
    x = mark[0] - vector[0]
    y = -1.0 * (mark[1] - vector[1])
    return [x, y]

def direction(angle):
    x = np.cos(angle)
    y = np.sin(angle)
    return [x, y]

def move_vector(p, velocity):
    unit_v = direction(p.getTheta())
    return [unit_v[0]*velocity, -unit_v[1]*velocity]


def dist_vector(vec):
    return np.linalg.norm(vec) #np.sqrt(vec[0]**2 + vec[1]**2)

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

# Returns angle between orientation of particle and particle to landmark vector
# v1 : particle to landmark vector
# v2 : particle orientation vector
def vector_angle(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    tmp1 = np.degrees(np.arctan2(v1_u[1],v1_u[0]))
    tmp2 = np.degrees(np.arctan2(v2_u[1],v2_u[0]))
    return tmp2-tmp1

def diff_weight(diff, varians):
    return 1/np.sqrt((2*np.pi*varians)) *\
           np.exp(-np.divide(diff**2, 2 * varians))

# This function finds weight for distance and angle for given particle to
# observed landmark. Turning right will cause for positive angle, and reversed
def weight(p, obs_angle, obs_dist, mark_nr):
    part2Mark = particle_landmark_vector(mark_nr, p)
    mark_dist = dist_vector(part2Mark)
    dist_diff = abs(obs_dist - mark_dist)
    if dist_diff <= 0.000001:
        dist_diff = 0.00001
    dist_weight = diff_weight(dist_diff, 25)

    orientation = direction(p.getTheta())
    angle_to_mark = vector_angle(part2Mark, orientation)
    angle_diff = abs(angle_to_mark - obs_angle)
    if angle_diff <= 0.00001:
        angle_digg = 0.0001
    angle_weight = diff_weight(angle_diff, 25)


    if math.isnan(dist_weight):
        dist_weight = 0.0
    if math.isnan(angle_weight):
        angle_weight = 0.0
    return dist_weight, angle_weight


def weight_particles(particles, measured_angle, measured_distance, mark_nr):
    # sum of the weight
    sum_dist_w = 0.0
    sum_angle_w = 0.0
    list_of_particles = []
    for p in particles:
        # pre-normalized measured weight
        dist_w, angle_w = weight(p, measured_angle, measured_distance, mark_nr)

        sum_dist_w += dist_w  #tmp
        sum_angle_w += angle_w

        list_of_particles.append([dist_w*0.6, angle_w*0.4, p])

    list_of_particles = np.array(list_of_particles)

    # normalize weights checks if weight sum have
    if math.isnan(sum_dist_w) or math.isnan(sum_angle_w):
        print "found nan value", sum_dist_w, sum_angle_w

    accum = 0.0
    for p in list_of_particles:
        p[0] /= sum_dist_w
        p[1] /= sum_angle_w
        p[2].setWeight(p[0])
        p[0] = p[0] + p[1]
        accum += p[0]
        p[1] = accum

    return list_of_particles

def ret_landmark(colorProb, direction):
    if colorProb[1] >= colorProb[0]:
        color = 'Green'
    else:
        color = 'Red'

    if color == 'Red' and direction == 'vertical':
        landmark = 0
    elif color == 'Green' and direction == 'vertical':
        landmark = 1
    elif color == 'Green' and direction == 'horizontal':
        landmark = 2
    elif color == 'Red' and direction == 'horizontal':
        landmark = 3

    return landmark


def where_to_go(pose, goal):
    """ Takes a particle (which must be our best bet for our actual position)
    and the place we want to be (goal = [x, y])

    returns a list of the length the robot needs to drive, the degrees it
    needs to turn and the direction it needs to turn"""

    ang = vector_angle(particle_landmark_vector_v2(goal, [pose[0],pose[1]]),
                       direction(pose[2]))

    if math.isnan(ang):
        print "pose information :", pose
        print "goal information :", goal
    if ang <= 0:
        turn_dir = 'right'
    else:
        turn_dir = 'left'
    turn_deg = ang
    length = np.linalg.norm([pose[0]-goal[0], pose[1]-goal[1]])

    # length = np.sqrt(
    #     np.power((particle.getX() - goal[0]), 2) + np.power(
    #         (particle.getY() - goal[1]), 2))

    print 'REPORT FROM: where_to_go'
    print 'est_particle: ' , str([pose[0], pose[1], pose[2]])
    print 'goal: ' , str(goal)
    print 'estimated course: dist= ' + str(length) + ', dir= ' + turn_dir,  \
          'turn degree=' + str(turn_deg)
    return {'dist' : length,
            'turn_dir' : turn_dir,
            'turn_degree' : turn_deg}
#[length, turn_dir, turn_deg]


def resample_particles(w_particles):
    N = len(w_particles[:,0])
    new_particles = []
    index = int(random.random() * N)
    beta = 0.0

    mw = w_particles[w_particles[:,0] == max(w_particles[:, 0])][0,0]
    for i in range(N):
        beta += random.random() * 2.0 * mw
        while beta > w_particles[index,0]:
            beta -= w_particles[index,0]
            index = (index + 1) % N
        p = w_particles[index,1]
        new_particles.append(particle.Particle(p.getX(),
                             p.getY(),
                             p.getTheta(),
                             1.0/N))

    return np.array(new_particles)


# For graphic
def jet(x):
    """Colour map for drawing particles. This function determines the colour of
    a particle from its weight."""
    r = (x >= 3.0/8.0 and x < 5.0/8.0) * (4.0 * x - 3.0/2.0) + (x >= 5.0/8.0 and x < 7.0/8.0) + (x >= 7.0/8.0) * (-4.0 * x + 9.0/2.0)
    g = (x >= 1.0/8.0 and x < 3.0/8.0) * (4.0 * x - 1.0/2.0) + (x >= 3.0/8.0 and x < 5.0/8.0) + (x >= 5.0/8.0 and x < 7.0/8.0) * (-4.0 * x + 7.0/2.0)
    b = (x < 1.0/8.0) * (4.0 * x + 1.0/2.0) + (x >= 1.0/8.0 and x < 3.0/8.0) + (x >= 3.0/8.0 and x < 5.0/8.0) * (-4.0 * x + 5.0/2.0)

    return (255.0*r, 255.0*g, 255.0*b)

def draw_world(est_pose, particles, world):
    """Visualization.
    This functions draws robots position in the world."""

    offset = 100;

    world[:] = CWHITE # Clear background to white

    # Find largest weight
    max_weight = 0
    for particle in particles:
        max_weight = max(max_weight, particle.getWeight())

    # Draw particles
    for particle in particles:
        x = int(particle.getX()) + offset
        y = int(particle.getY()) + offset
        colour = jet(particle.getWeight() / max_weight)
        cv2.circle(world, (x,y), 2, colour, 2)
        b = (int(particle.getX() + 15.0*np.cos(particle.getTheta()))+offset,
                                     int(particle.getY() - 15.0*np.sin(particle.getTheta()))+offset)
        cv2.line(world, (x,y), b, colour, 2)

    # Draw landmarks
    lm0 = (landmarks[0][0]+offset, landmarks[0][1]+offset)
    lm1 = (landmarks[1][0]+offset, landmarks[1][1]+offset)
    lm2 = (landmarks[2][0]+offset, landmarks[2][1]+offset)
    lm3 = (landmarks[3][0]+offset, landmarks[3][1]+offset)

    cv2.circle(world, lm0, 5, CRED, 2)
    cv2.circle(world, lm1, 5, CGREEN, 2)
    cv2.circle(world, lm2, 5, CGREEN, 2)
    cv2.circle(world, lm3, 5, CRED, 2)

    # Draw estimated robot pose
    a = (int(est_pose.getX())+offset, int(est_pose.getY())+offset)
    b = (int(est_pose.getX() + 15.0*np.cos(est_pose.getTheta()))+offset,
                                 int(est_pose.getY() - 15.0*np.sin(est_pose.getTheta()))+offset)
    cv2.circle(world, a, 5, CMAGENTA, 2)
    cv2.line(world, a, b, CMAGENTA, 2)


def innit_particles(num_particles=1000):
    # Initialize particles
    particles = []
    for i in range(num_particles):
        p = particle.Particle(500.0 * np.random.ranf() - 100,
                              500.0 * np.random.ranf() - 100,
                              2.0 * np.pi * np.random.ranf() - np.pi,
                              1.0 / num_particles)
        particles.append(p)
    return particles


def update_particles(particles, cam, velocity, angular_velocity, world,
                     WIN_RF1, WIN_World):
    #print 'update: ' + str(angular_velocity)
    cv2.waitKey(4)
    num_particles = len(particles)
    for p in particles:
        # calculates new orientation

        curr_angle = add_to_angular_v2(np.degrees(p.getTheta()), angular_velocity)
        # print 'theta_rad: ' + str(p.getTheta())
        # print 'theta_deg: ' + str(np.degrees(p.getTheta()))
        # print 'cur_ang_deg: ' + str(np.degrees(curr_angle))
        if velocity > 0.0:
            [x, y] = move_vector(p, velocity)
            particle.move_particle(p, x, y, curr_angle)
        else:
            particle.move_particle(p, 0.0, 0.0, curr_angle)
            #print 'cur_ang_rad: ' + str(curr_angle)
    if velocity != 0.0:
        particle.add_uncertainty(particles, 12, 10)
    if velocity == 0.0 and angular_velocity != 0.0:
        particle.add_uncertainty(particles, 0, 10)

    # Fetch next frame
    colour, distorted = cam.get_colour()

    # Detect objects
    objectType, measured_distance, measured_angle, colourProb = cam.get_object(
        colour)

    if objectType != 'none':
        obs_landmark = ret_landmark(colourProb, objectType)
        observed_obj = [objectType, measured_distance, measured_angle,
                        obs_landmark]


        list_of_particles = weight_particles(particles,
                                             np.degrees(measured_angle),
                                             measured_distance, obs_landmark)


        particles = resample_particles(list_of_particles[:,[0,2]])

        particle.add_uncertainty(particles, 15, 10)

        cam.draw_object(colour)
    else:
        observed_obj = [None, None, None, None]
        for p in particles:
            p.setWeight(1.0 / num_particles)

        particle.add_uncertainty(particles, 10, 10)

    est_pose = particle.estimate_pose(particles)

    #print 'Updated pose: ' + str([est_pose.getX(), est_pose.getY()])
    draw_world(est_pose, particles, world)
    # Show frame
    cv2.imshow(WIN_RF1, colour)
    # Show world
    cv2.imshow(WIN_World, world)
    #print est_pose
    return {'est_pos': est_pose,
            'obs_obj': observed_obj,
            'particles': particles}


# Lazily avoiding to import particle in control for no reason what-so-ever...
def estimate_position(particles):
    return particle.estimate_pose(particles)
