import cv2
import particle
import camera
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
landmarks = [(0, 0), (300, 0)]


def add_to_angular(present, delta):
    # Ensures that the orientation of the particle stays in range 0-360
    new_angle = np.degrees(present) + delta
    if new_angle >= 360.0:
        new_angle = new_angle - 360.0
    elif new_angle < 0.0:
        new_angle = new_angle + 360.0
    return np.radians(new_angle)

def vector_angle(v1, v2):
    l1 = np.sqrt(np.power(v1[0], 2) + np.power(v1[1], 2))
    l2 = np.sqrt(np.power(v2[0], 2) + np.power(v2[1], 2))
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    return np.arccos(np.divide(dot, (l1 * l2)))

def calc_x_y(velocity, angle):
    if 0.0 <= angle < 90.0:
        x_dir = 1.0
        y_dir = -1.0
        A = angle
    elif 90.0 <= angle < 180.0:
        x_dir = -1.0
        y_dir = -1.0
        A = angle - 90.0
    elif 180.0 <= angle < 270.0:
        x_dir = -1.0
        y_dir = 1.0
        A = angle - 180.0
    elif 270.0 <= angle < 360.0:
        x_dir = 1.0
        y_dir = 1.0
        A = angle - 270.0
    else:
        # should not happen....
        print "Fuck, something went wrong in calc x,y"
        raise
    # avoid div by zero if particle have not moved
    if velocity > 0:
        # calculates delta_x/y by triangle calculations...
        C = 90.0
        B = 180.0 - A - C
        c = velocity
        a = (c * np.sin(A)) / np.sin(C)
        b = (c * np.sin(B)) / np.sin(C)
        return b, a, x_dir, y_dir
    else:
        raise

def particle_landmark_vector(mark, particle):
    (mark_x, mark_y) = landmarks[mark]
    x = mark_x - particle.getX()
    y = -1.0 * (mark_y - particle.getY())
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

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    #v1_u = unit_vector(v1)
    v1_u = v1
    #print "orient", v1_u
    v2_u = unit_vector(v2)
    #print "mark", v2_u
    return np.degrees(np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)))

def diff_weight(diff, varians):
    return 1/(2*np.pi*varians) * np.exp(-np.divide(diff**2, 2* varians))

# function finds weight for distance and angle for given particle to observed landmark
# turning right will cause for positive angle, and reversed
def weight(p, obs_angle, obs_dist, mark_nr):
    part2Mark = particle_landmark_vector(mark_nr, p)
    mark_dist = dist_vector(part2Mark)
    dist_diff = abs(obs_dist - mark_dist)
    if dist_diff <= 0.000001:
        dist_diff = 0.00001
    dist_weight = diff_weight(dist_diff, 100)

    orientation = direction(p.getTheta())
    angle_to_mark = angle_between(orientation, part2Mark)
    angle_diff = abs(angle_to_mark - obs_angle)
    if angle_diff <= 0.00001:
        angle_digg = 0.0001
    angle_weight = diff_weight(angle_diff, 50)


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
    #print "dist", sum_dist_w, "angle_w", sum_angle_w

    # normalize weights checks if weight sum have
    if math.isnan(sum_dist_w) or math.isnan(sum_angle_w):
        print "found nan value", sum_dist_w, sum_angle_w

    # list_of_particles[:,0] = np.divide(list_of_particles[:,0], sum_dist_w)
    # list_of_particles[:,1] = np.divide(list_of_particles[:,1], sum_angle_w)

    #lower = 0.0
    accum = 0.0
    for p in list_of_particles:
        p[0] /= sum_dist_w
        p[1] /= sum_angle_w
        p[2].setWeight(p[0])
        p[0] = p[0] + p[1]
        accum += p[0]
        p[1] = accum

    return list_of_particles

def ret_landmark(color, horizontal_or_vertical):
    if color[1] >= color[0]:
        x = 'Green'
    else:
        x = 'Red'
    print x
    if x == 'Red' and horizontal_or_vertical == 'horizontal':
        return 0
    elif x == 'Red' and horizontal_or_vertical == 'vertical':
        return 0
    elif x == 'Green' and horizontal_or_vertical == 'vertical':
        return 1
    elif x == 'Green' and horizontal_or_vertical == 'horizontal':
        return 1


def where_to_go(particle, goal):
    """ Takes a particle (which must be our best bet for our actual position)
    and the place we want to be (goal = [x, y])

    returns a list of the length the robot needs to drive, the degrees it
    needs to turn and the direction it needs to turn"""
    ang = vector_angle([particle.getX(), particle.getY()], goal)
    if ang <= 180:
        turn_dir = 'right'
        turn_deg = ang
    else:
        turn_dir = 'left'
        turn_deg = 180 - ang
    length = np.sqrt(
        np.power((particle.getX() - goal[0]), 2) + np.power(
            (particle.getY() - goal[1]), 2))
    return [length, turn_dir, turn_deg]


def in_range(list_of_weigthed_particles, random_number, dicte, listLength):
    if list_of_weigthed_particles[dicte['i']][1] <= random_number < list_of_weigthed_particles[dicte['i']][0]:
        return list_of_weigthed_particles[dicte['i']][2]
    elif list_of_weigthed_particles[dicte['i']][0] < random_number:
        a = np.power(2.0, dicte['n'])
        b = np.divide(1.0, a)
        c = b * listLength
        x = int(round(c))
        dicte['i'] += x
        dicte['n'] += 1
        return in_range(list_of_weigthed_particles, random_number, dicte, listLength)
    elif list_of_weigthed_particles[dicte['i']][1] > random_number:
        dicte['i'] -= int(round((np.divide(1.0, np.power(2.0, dicte['n'])) * listLength)))
        dicte['n'] += 1
        return in_range(list_of_weigthed_particles, random_number, dicte, listLength)
    else:
        print '---return when in range--- fucked up.... ( -__- )'
        raise


def when_in_range(w_particles, lower, upper, value):
    lower = lower
    upper = upper
    #print "initialize resampling"
    while True:
        ind = (upper-lower)/2
        if upper-lower <= 1:
            return w_particles[lower][2]

        #print "running when in range"

        if w_particles[upper-ind][1] < value:
            if w_particles[upper-ind+1][1] >= value:
                return w_particles[upper-ind+1][2]
            else:
                lower += ind
        else:
            if w_particles[upper-ind-1][1] < value:
                return w_particles[upper-ind-1][2]
            else:
                upper -= ind


def innit_particles(num_particles = 1000):
    # Initialize particles
    particles = []
    for i in range(num_particles):
        # Random starting points. (x,y) \in [-1000, 1000]^2, theta \in [-pi, pi].
        p = particle.Particle(2000.0 * np.random.ranf() - 1000,
                              2000.0 * np.random.ranf() - 1000,
                              2.0 * np.pi * np.random.ranf() - np.pi,
                              1.0 / num_particles)
        # p = particle.Particle(2000.0*np.random.ranf() - 1000, 2000.0*np.random.ranf() - 1000, np.pi+3.0*np.pi/4.0, 1.0/num_particles)
        particles.append(p)
    return particles

def update_particles(particles, cam, velocity, angular_velocity):

    num_particles = len(particles)
    for p in particles:
        # calculates new orientation
        curr_angle = add_to_angular(p.getTheta(), angular_velocity)
        if velocity > 0:
            [x, y] = move_vector(p, velocity)
            # x, y, x_dir, y_dir = calc_x_y(velocity, curr_angle)
            particle.move_particle(p, x, y, curr_angle)
        else:
            particle.move_particle(p, 0.0, 0.0, curr_angle)

    # Fetch next frame
    colour, distorted = cam.get_colour()

    # Detect objects
    objectType, measured_distance, measured_angle, colourProb = cam.get_object(
        colour)

    if objectType != 'none':

        observed_obj = [objectType, measured_distance, measured_angle,
                        ret_landmark(colourProb, objectType)]

        print "Object type = ", objectType
        print "Measured distance = ", measured_distance
        print "Measured angle = ", measured_angle
        print "Colour probabilities = ", colourProb

        if (objectType == 'horizontal'):
            print "Landmark is horizontal"
        elif (objectType == 'vertical'):
            print "Landmark is vertical"
        else:
            print "Unknown landmark type"
        # *********** set weights ***********

        obs_landmark = ret_landmark(colourProb, objectType)
        print obs_landmark

        sum_of_angle_diff = 0.0

        # Computes weights and normalizes for each particle
        list_of_particles = weight_particles(particles,
                                             np.degrees(measured_angle),
                                             measured_distance, obs_landmark)

        # for p in list_of_particles:
        #     print p[1]
        # The observed measured coordinates


        # print sum(list_of_particles[:,0]),
        print "normalized weights"
        # print len(list_of_particles)
        # print list_of_particles[num_particles-1,1]
        scale = 2

        accum = 0.0
        # updates resampled particle weights
        # for p in list_of_particles:


        lower = 0
        upper = 0
        # nunum_of_particles = len(particles)
        weight_sum = 0.0
        particles = []
        for count in range(0, int(num_particles * 0.95)):
            rando = np.random.uniform(0.0,
                                      1.0)  # np.random.normal(0.0, 1.0, 1)

            # dicto = {'i': 500,
            #          'n': 2}
            p = when_in_range(list_of_particles,
                              0,
                              num_particles,
                              rando)
            # rando,
            #                               {'i': num_particles/2, 'n': 2},
            #                          num_particles)


            # weight_sum += p.getWeight()
            particles.append(
                particle.Particle(p.getX(), p.getY(), p.getTheta(),
                                  1.0 / num_particles))
        print "resampled"

        particle.add_uncertainty(particles, 12, 15)

        # 10% new random particles added
        for c in range(0, int(math.ceil(num_particles * 0.05))):
            p = particle.Particle(500.0 * np.random.ranf() - 100,
                                  500.0 * np.random.ranf() - 100,
                                  2.0 * np.pi * np.random.ranf() - np.pi, 0.0)

            particles.append(p)

        # Draw detected pattern
        cam.draw_object(colour)
    else:
        observed_obj = [None, None, None, None]
        # No observation - reset weights to uniform distribution
        for p in particles:
            p.setWeight(1.0 / num_particles)

    est_pose = particle.estimate_pose(
        particles)  # The estimate of the robots current pose
    return [est_pose, observed_obj]

def estimate_position(particles):
    return particle.estimate_pose(particles)