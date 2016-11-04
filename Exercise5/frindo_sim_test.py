import cv2
import particle
import camera
import numpy as np
import math
import mock_control as con
import robot

# Some colors constants
CRED = (0, 0, 255)
CGREEN = (0, 255, 0)
CBLUE = (255, 0, 0)
CCYAN = (255, 255, 0)
CYELLOW = (0, 255, 255)
CMAGENTA = (255, 0, 255)
CWHITE = (255, 255, 255)
CBLACK = (0, 0, 0)

LANDMARK = {0: 0,
            1: 0}
LANDMARK_COORDINATES = {0: (0, 0),
                        1: (300, 0)}
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
    (mark_x, mark_y) = LANDMARK_COORDINATES[mark]
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

        list_of_particles.append([dist_w*0.65, angle_w*0.35, p])

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
    lm0 = (LANDMARK_COORDINATES[0][0]+offset, LANDMARK_COORDINATES[0][1]+offset)
    lm1 = (LANDMARK_COORDINATES[1][0]+offset, LANDMARK_COORDINATES[1][1]+offset)
    cv2.circle(world, lm0, 5, CRED, 2)
    cv2.circle(world, lm1, 5, CGREEN, 2)

    # Draw estimated robot pose
    a = (int(est_pose.getX())+offset, int(est_pose.getY())+offset)
    b = (int(est_pose.getX() + 15.0*np.cos(est_pose.getTheta()))+offset,
                                 int(est_pose.getY() - 15.0*np.sin(est_pose.getTheta()))+offset)
    cv2.circle(world, a, 5, CMAGENTA, 2)
    cv2.line(world, a, b, CMAGENTA, 2)


### Main program ###

# Open windows
WIN_RF1 = "Robot view";
cv2.namedWindow(WIN_RF1);
cv2.moveWindow(WIN_RF1, 50       , 50);

WIN_World = "World view";
cv2.namedWindow(WIN_World);
cv2.moveWindow(WIN_World, 500       , 50);


# Initialize particles
num_particles = 1000
particles = []
for i in range(num_particles):
    p = particle.Particle(500.0*np.random.ranf() - 100, 500.0*np.random.ranf() - 100, np.degrees(2.0*np.pi*np.random.ranf()), 1.0/num_particles)
    particles.append(p)

est_pose = particle.estimate_pose(particles) #The estimate of the robots current pose

# Driving parameters
velocity = 0.0;
angular_velocity = 0.0;

# Initialize the robot (XXX: You do this)

# Allocate space for world map
world = np.zeros((500,500,3), dtype=np.uint8)

# Draw map
draw_world(est_pose, particles, world)

print "Opening and initializing camera"


#cam = camera.Camera(0, 'macbookpro')
cam = camera.Camera(0, 'frindo')

frindo = robot.Robot()
former_turn = 0.0
while True:

    cv2.waitKey(4)

    updated_values = con.control_frindo(LANDMARK, former_turn, est_pose, frindo)

    former_turn += updated_values[2]
    angular_velocity = updated_values[1]
    velocity = updated_values[0]

    num_particles = len(particles)
    for p in particles:
        # calculates new orientation
        if angular_velocity != 0:
            curr_angle = add_to_angular(p.getTheta(), angular_velocity)
        if velocity > 0:
            [x,y] = move_vector(p, velocity)
            particle.move_particle(p, x, y, curr_angle)

    particle.add_uncertainty(particles, 12, 15)

    # Fetch next frame
    colour, distorted = cam.get_colour()

    # Detect objects
    objectType, measured_distance, measured_angle, colourProb = cam.get_object(colour)

    if objectType != 'none':
        obs_landmark = ret_landmark(colourProb, objectType)
        print obs_landmark
        sum_of_angle_diff = 0.0
        list_of_particles = weight_particles(particles, np.degrees(measured_angle), measured_distance, obs_landmark)
        print "normalized weights"
        scale = 2
        accum = 0.0
        lower = 0
        upper = 0
        weight_sum = 0.0

        list_of_particles = weight_particles(particles,
                                             np.degrees(measured_angle),
                                             measured_distance, obs_landmark)

        particles = []
        for count in range(0, int(num_particles * 0.95)):
            rando = np.random.uniform(0.0, 1.0)

            p = when_in_range(list_of_particles,
                              0,
                              num_particles,
                              rando)
            particles.append(
                particle.Particle(p.getX(), p.getY(), p.getTheta(),
                                  1.0 / num_particles))

        particle.add_uncertainty(particles, 12, 15)

        # New random particles added
        for c in range(0, int(math.ceil(num_particles * 0.01))):
            p = particle.Particle(500.0 * np.random.ranf() - 100,
                                  500.0 * np.random.ranf() - 100,
                                  2.0 * np.pi * np.random.ranf() - np.pi, 0.0)

            particles.append(p)

        # Draw detected pattern
        cam.draw_object(colour)
    else:
        # No observation - reset weights to uniform distribution
        for p in particles:
	    particle.add_uncertainty(particles, 12, 15)
            p.setWeight(1.0 / num_particles)

    est_pose = particle.estimate_pose(particles)

    print 'Updated pose: ' + str([est_pose.getX(), est_pose.getY()])
    
    draw_world(est_pose, particles, world)

    cv2.imshow(WIN_RF1, colour);

    # Show world
    cv2.imshow(WIN_World, world);


# Close all windows
cv2.destroyAllWindows()
