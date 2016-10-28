import cv2
import particle
import camera
import numpy as np



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


# function finds weight for distance and angle for given particle to observed landmark
# turning right will cause for positive angle, and reversed
def weight(p, obs_angle, obs_dist, mark_nr):
    part2Mark = particle_landmark_vector(mark_nr, p)
    mark_dist = dist_vector(part2Mark)
    #dist_weight = 1.0/abs(obs_dist-mark_dist) GAMMEL VÆGT
    dist_weight = np.exp(-(np.divide(np.power(obs_dist-mark_dist,2), np.multiply(2, 18000))))

    orientation = direction(p.getTheta())
    angle_to_mark = angle_between(orientation, part2Mark)
    #angle_weight = 1.0/(angle_to_mark - obs_angle) GAMMEL VÆGT
    dist_weight = np.exp(-(np.divide(np.power(obs_angle-angle_to_mark,2), np.multiply(2, 18000))))
    dist_diff = abs(obs_dist-mark_dist)
    if dist_diff == 0.0:
        dist_weight = 999999999.0
    else:
        dist_weight = 1.0/abs(obs_dist-mark_dist)

    orientation = direction(p.getTheta())
    angle_to_mark = angle_between(orientation, part2Mark)
    angle_diff = angle_to_mark - obs_angle
    if angle_diff == 0:
        angle_weight = 999999999.0
    else:
        angle_weight = 1.0/angle_diff

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


def return_when_in_range(list_of_weigthed_particles, random_number, indexing, n, listLength):
    print indexing
    print n
    print random_number

    if list_of_weigthed_particles[indexing][0] <= random_number < list_of_weigthed_particles[indexing][1]:
        return list_of_weigthed_particles[indexing][2]

    elif list_of_weigthed_particles[indexing][1] < random_number:

	newIndex = int(round(indexing + (np.divide(1, np.power(2, n)) * listLength)))
	new_n    = n + 1

        return_when_in_range(list_of_particles, random_number, newIndex, new_n, listLength)

    elif list_of_weigthed_particles[indexing][0] > random_number:

	newIndex = int(round(indexing - (np.divide(1, np.power(2, n)) * listLength)))
	new_n    = n + 1

	return_when_in_range(list_of_particles, random_number, newIndex, new_n, listLength)

    else:
        print '---return when in range--- fucked up.... ( -__- )'
        raise

def when_in_range(w_particles, lower, upper, value):
    lower = lower
    upper = upper

    while True:
        #print "running when in range"
        ind = int(float(upper-lower)/2)
        if lower-upper <= 1:
            return w_particles[lower][2]

        if w_particles[lower+ind][0] > value:
            if w_particles[lower+ind-1][0] <= value:
                return w_particles[lower+ind][2]
            else:
                upper -= ind

        elif w_particles[lower+ind][0] < value:
            if w_particles[lower+ind+1][0] >= value:
                return w_particles[lower+ind+1][2]
            else:
                lower += ind



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
    p = particle.Particle(2000.0*np.random.ranf() - 1000, 2000.0*np.random.ranf() - 1000, 2.0*np.pi*np.random.ranf() - np.pi, 1.0/num_particles)
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

# print landmarks[0]

# particles = [particle.Particle(-5,-50, 45.0, 1.0/num_particles),
#              particle.Particle(500,50, 270.0, 1.0/num_particles),
#              particle.Particle(50,-100, 180.0, 1.0/num_particles),
#              particle.Particle(-500,50, 0.0, 1.0/num_particles)]
# obs = (50.000, 15.0)

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
    action = cv2.waitKey(4)

    if action == ord('w'): # Forward
        velocity += 4.0;
    elif action == ord('x'): # Backwards
        velocity -= 4.0;
        angular_velocity = 0.0;
    elif action == ord('s'): # Stop
        velocity = 0.0;
        angular_velocity = 0.0;
    elif action == ord('a'): # Left
        angular_velocity += 0.2;
    elif action == ord('d'): # Right
        angular_velocity -= 0.2;
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
            sum_dist_w += dist_w
            sum_angle_w += angle_w

            list_of_particles.append([dist_w, angle_w*0.05, p])

        list_of_particles = np.array(list_of_particles)

        # normalize weights
        list_of_particles[:,0] = np.divide(list_of_particles[:,0], sum_dist_w)
        list_of_particles[:,1] = np.divide(list_of_particles[:,1], sum_angle_w)
        # Because distance is only 0.5 of the weight
        scale = 2

        accum = 0.0
        for p in list_of_particles:
            # setting the dist part of particle weight for all particles
            tmp_w = p[0] # + p[1]
            p[2].setWeight(tmp_w)
            accum += tmp_w
            p[0] = accum

            #p[2].setWeight(np.divide(np.divide(p[0], sum_of_weigth), scale))
        # *********** || ***********


        lower = 0
        num_of_particles = len(particles)
        weight_sum = 0.0
        particles = []
        for count in range(0,int(num_particles*0.9)):
            rando = np.random.uniform(0.0, 1.0)
            p = when_in_range(list_of_particles,
                              lower,
                              num_of_particles,
                              rando)

            #print rando
            #weight_sum += p.getWeight()
            particles.append(p)
        #particle.add_uncertainty(particles, 1.0, 0.5)
        #return_when_in_range(possible_new_particles, , 500, 2, len(possible_new_particles)))
        for c in range(0,int(num_particles*0.1)):
            p = particle.Particle(2000.0*np.random.ranf() - 1000, 2000.0*np.random.ranf() - 1000, 2.0*np.pi*np.random.ranf() - np.pi, 1.0/num_particles)
            particles.append(p)


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
    print est_pose.getX(), est_pose.getY(), est_pose.getTheta()


    # Draw map
    draw_world(est_pose, particles, world)

    # Show frame
    cv2.imshow(WIN_RF1, colour);

    # Show world
    cv2.imshow(WIN_World, world);


# Close all windows
cv2.destroyAllWindows()
