import cv2
import particle
import camera
import numpy as np
import math



# TODO: The coordinate system is such that the y-axis points downwards due to the visualization in draw_world.
# Consider changing the coordinate system into a normal cartesian coordinate system.


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
    new_angle = present + delta
    if new_angle >= 360.0:
        new_angle = new_angle - 360.0
    elif new_angle < 0.0:
        new_angle = new_angle +  360.0
    return new_angle

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
    if dist_diff == 0:
        dist_diff = 1
    dist_weight = diff_weight(dist_diff, 30)

    # if dist_diff == 0.0:
    #     dist_weight = 999999999.0
    # else:
    #     dist_weight = 1.0/abs(obs_dist-mark_dist)

    orientation = direction(p.getTheta())
    angle_to_mark = angle_between(orientation, part2Mark)
    angle_diff = angle_to_mark - obs_angle
    angle_weight = diff_weight(angle_diff, 30)
    #np.exp(-(np.divide(np.power(obs_angle-angle_to_mark,2), np.multiply(2, 18000))))
    #dist_diff = abs(obs_dist-mark_dist)

    # orientation = direction(p.getTheta())
    # angle_to_mark = angle_between(orientation, part2Mark)
    # angle_diff = angle_to_mark - obs_angle
    # if angle_diff == 0:
    #     angle_weight = 999999999.0
    # else:
    #     angle_weight = 1.0/angle_diff
    if math.isnan(dist_weight):
        dist_weight = 0.0
    if math.isnan(angle_weight):
        angle_weight = 0.0
    return dist_weight, angle_weight


def ret_landmark_coordinates(color, horizontal_or_vertical):
    if color[1] >= color[0]:
        x = 'Green'
    else:
        x = 'Red'
    if x == 'Red' and horizontal_or_vertical == 'horizontal':
        return landmarks[0]
    elif x == 'Red' and horizontal_or_vertical == 'vertical':
        return landmarks[0]
    elif x == 'Green' and horizontal_or_vertical == 'vertical':
        return landmarks[1]
    elif x == 'Green' and horizontal_or_vertical == 'horizontal':
        return landmarks[1]


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

    while True:
        #print "running when in range"
        ind = (upper-lower)/2
        if upper-lower <= 1:
            return w_particles[lower][1]
        if w_particles[lower+ind][0] > value:
            if w_particles[lower+ind-1][0] <= value:
                return w_particles[lower+ind][1]
            else:
                upper -= ind
        elif w_particles[upper-ind][0] <= value:
            try:
                if w_particles[upper-ind+1][0] > value:
                    return w_particles[upper-ind+1][1]
                else:
                    lower += ind
            except:
                return w_particles[upper-ind][1]


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
    # Random starting points. (x,y) \in [-1000, 1000]^2, theta \in [-pi, pi].
    p = particle.Particle(500.0*np.random.ranf() - 100, 500.0*np.random.ranf() - 100, 2.0*np.pi*np.random.ranf() - np.pi, 1.0/num_particles)
    #p = particle.Particle(2000.0*np.random.ranf() - 1000, 2000.0*np.random.ranf() - 1000, np.pi+3.0*np.pi/4.0, 1.0/num_particles)
    particles.append(p)

est_pose = particle.estimate_pose(particles) # The estimate of the robots current pose

# Driving parameters
velocity = 0.0; # cm/sec
angular_velocity = 0.0; # radians/sec

# Initialize the robot (XXX: You do this)

# Allocate space for world map
world = np.zeros((500,500,3), dtype=np.uint8)


####################
# TESTING PURPOSES #
####################

#print landmarks[0]

# particles =  [particle.Particle(0,50, 90.0, 1.0/num_particles),
#               particle.Particle(0,100, 90.0, 1.0/num_particles),
#               particle.Particle(0,150, 90.0, 1.0/num_particles),
#               particle.Particle(0,200, 90.0, 1.0/num_particles)]
# obs = (250, 0)

# for p in particles:
#     vec = particle_landmark_vector(0, p)
#     print "vector mark", vec
#     dist = dist_vector(vec)
#     print "dist to mark", dist
#     orientation = direction(p.getTheta())
#     print "orienttation", orientation

#     print weight(p, obs[1], obs[0], 0)
#     print



# Draw map
draw_world(est_pose, particles, world)

print "Opening and initializing camera"


cam = camera.Camera(0, 'macbookpro')
#cam = camera.Camera(0)

while True:

    # Move the robot according to user input (for testing)
    action = cv2.waitKey(1)

    if action == ord('w'): # Forward
        velocity += 0.4;
    elif action == ord('x'): # Backwards
        velocity -= 0.4;
        angular_velocity = 0.0;
    elif action == ord('s'): # Stop
        velocity = 0.0;
        angular_velocity = 0.0;
    elif action == ord('a'): # Left
        angular_velocity += 0.02;
    elif action == ord('d'): # Right
        angular_velocity -= 0.02;
    elif action == ord('q'): # Quit
        break

    # This loop updates position for all current particles
    for p in particles:
        # calculates new orientation
        curr_angle = add_to_angular(p.getTheta(), angular_velocity)
        if velocity > 0:
            [x,y] = move_vector(p, velocity)
            #x, y, x_dir, y_dir = calc_x_y(velocity, curr_angle)
            particle.move_particle(p, x, y, curr_angle)
        else:
            particle.move_particle(p, 0.0, 0.0, curr_angle)

    # Fetch next frame
    colour, distorted = cam.get_colour()


    # Detect objects
    objectType, measured_distance, measured_angle, colourProb = cam.get_object(colour)
    if objectType != 'none':
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
            continue

        # *********** set weights ***********

        obs_landmark = ret_landmark_coordinates(colourProb, objectType)
        # sum of the weight
        sum_dist_w = 0.0
        sum_angle_w = 0.0

        sum_of_angle_diff = 0.0

        # List of particles and their pre-normalized weigth
        list_of_particles = []

        # The observed measured coordinates

        for p in particles:
            # pre-normalized measured weight
            dist_w, angle_w = weight(p, measured_angle, measured_distance, 0)

            # accum weights
            tmp = (dist_w*0.75) + (angle_w*0.25)
            sum_dist_w += tmp
            #sum_angle_w += angle_w

            list_of_particles.append([tmp, sum_dist_w, p])

        list_of_particles = np.array(list_of_particles)
        print "dist", sum_dist_w, "angle_w", sum_angle_w

        # normalize weights checks if weight sum have
        if math.isnan(sum_dist_w):
            print "found nan value", sum_dist_w

        list_of_particles[:,0] = np.divide(list_of_particles[:,0], sum_dist_w)
        list_of_particles[:,1] = np.divide(list_of_particles[:,1], sum_dist_w)
        print sum(list_of_particles[:,0]),

        scale = 2

        accum = 0.0
        # updates resampled particle weights
        for p in list_of_particles:
            p[2].setWeight(p[0])

        lower = 0
        num_of_particles = len(particles)
        weight_sum = 0.0
        particles = []
        for count in range(0,int(num_particles)):
            rando = np.random.uniform(0.0, 1.0) #np.random.normal(0.0, 1.0, 1)

            p = when_in_range(list_of_particles[:,[0,2]],
                              lower,
                              num_of_particles,
                              rando)
            #print rando
            #weight_sum += p.getWeight()
            particles.append(particle.Particle(p.getX(), p.getY(), p.getTheta(), 1.0/num_particles))
        # for p in particles:
        #     print p.getX(), p.getY(), p.getWeight()

        particle.add_uncertainty(particles, 30, 0.0005)
        # for p in particles:
        #     print p.getX(), p.getY(), p.getWeight()
        #return_when_in_range(possible_new_particles, , 500, 2, len(possible_new_particles)))
        # for c in range(0,int(num_particles*0.1)):
        #     p = particle.Particle(2000.0*np.random.ranf() - 1000, 2000.0*np.random.ranf() - 1000, 2.0*np.pi*np.random.ranf() - np.pi, 1.0/num_particles)

        #     particles.append(p)


        # for p in particles:
        #     tmp = p.getWeight()/weight_sum
        #     #print tmp
        #     p.setWeight(tmp)


        # Draw detected pattern
        cam.draw_object(colour)
    else:
        # No observation - reset weights to uniform distribution
        for p in particles:
            p.setWeight(1.0/num_particles)


    est_pose = particle.estimate_pose(particles) # The estimate of the robots current pose
    print "est position"
    print est_pose.getX(), est_pose.getY(), est_pose.getTheta()


    # Draw map
    draw_world(est_pose, particles, world)

    # Show frame
    cv2.imshow(WIN_RF1, colour);

    # Show world
    cv2.imshow(WIN_World, world);

# Close all windows
cv2.destroyAllWindows()
