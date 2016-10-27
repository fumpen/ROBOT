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
    if 0.0 <= (present + delta) < 360.0:
        return present + delta
    elif present + delta < 0.0:
        return 360.0 + (present + delta)
    else:
        return (present + delta) - 360.0


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


def return_when_in_range(list_of_weigthed_particles, random_number, indexing = 500):
    if list_of_weigthed_particles[indexing][0] <= random_number < list_of_weigthed_particles[indexing][1]:
        return list_of_weigthed_particles[indexing][2]
    elif list_of_weigthed_particles[indexing][1] < random_number:
        return return_when_in_range(list_of_particles, random_number, round(indexing * 1.5))
    elif list_of_weigthed_particles[indexing][0] > random_number:
        return return_when_in_range(list_of_particles, random_number, round(indexing * 0.5))
    else:
        print '---return when in range--- fucked up.... ( -__- )'
        raise


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

# Draw map
draw_world(est_pose, particles, world)

print "Opening and initializing camera"

#cam = camera.Camera(0, 'macbookpro')
cam = camera.Camera(0, 'frindo')

while True:

    # Move the robot according to user input (for testing)
    action = cv2.waitKey(10)

    if action == ord('w'): # Forward
        velocity += 4.0;
    elif action == ord('x'): # Backwards
        velocity -= 4.0;
        angular_velocity = 0.0;
    elif action == ord('s'): # Stop
        velocity = 0.0;
        angular_velocity = 0.0;
    elif action == ord('a'): # Left
        angular_velocity -= 0.2;
    elif action == ord('d'): # Right
        angular_velocity += 0.2;
    elif action == ord('q'): # Quit
        break

    # This loop updates position for all current particles
    for p in particles:
        # calculates new orientation
        curr_angle = add_to_angular(p.getTheta, angular_velocity)
        if velocity > 0:
            x, y, x_dir, y_dir = calc_x_y(velocity, curr_angle)
            particle.move_particle(p, x * x_dir, y * y_dir, curr_angle)
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
        # sum of the weight
        sum_of_weigth = 0.0

        sum_of_angle_diff = 0.0

        # List of particles and their pre-normalized weigth
        list_of_particles = []

        # The observed measured coordinates
        obs_x, obs_y, a, b = calc_x_y(measured_distance, measured_angle)
        for p in particles:
            diff_x = np.absolute(np.absolute(obs_x) - np.absolute(p.getX()))
            diff_y = np.absolute(np.absolute(obs_y) - np.absolute(p.getY()))

            diff_ang = np.absolute(np.absolute(p.getWeight) - np.absolute(measured_angle))

            sum_of_angle_diff += diff_ang
            # Distance between observation and particle
            diff_dist = np.sqrt(np.power(diff_x, 2) + np.power(diff_y, 2))
            if diff_dist == 0:
                diff_dist += 0.00001
            # pre-normalized weight
            dist_weight = np.divide(1.0, np.absolute(diff_dist - measured_distance))
            sum_of_weigth += dist_weight
            list_of_particles.append([dist_weight, p, diff_ang])

        # To pick the new particles [lower_bound, upper_bound, particle]
        possible_new_particles = []
        tot_sum_weight = 0.0

        # Because distance is only 0.5 of the weight
        scale = 2
        for p in list_of_particles:
            # setting the dist part of particle weight for all particles
            dist_weight = np.divide(np.divide(p[0], sum_of_weigth), scale)
            angle_weight = np.divide(np.divide(p[2], sum_of_angle_diff), scale)
            p[1].setWeight(dist_weight + angle_weight)
            l_weigth = tot_sum_weight
            tot_sum_weight += dist_weight + angle_weight
            possible_new_particles.append([l_weigth, tot_sum_weight, p[1]])
        # *********** || ***********

        count = 0
        num_of_particles = len(particles)
        particles = []
        while count in range(0, num_of_particles):
            particles.append(return_when_in_range(possible_new_particles, np.random.uniform(0.0, 1.0)))
            count += 1


        # Draw detected pattern
        cam.draw_object(colour)
    else:
        # No observation - reset weights to uniform distribution
        for p in particles:
            p.setWeight(1.0/num_particles)

    
    est_pose = particle.estimate_pose(particles) # The estimate of the robots current pose

    # Draw map
    draw_world(est_pose, particles, world)
    
    # Show frame
    cv2.imshow(WIN_RF1, colour);

    # Show world
    cv2.imshow(WIN_World, world);
    
    
# Close all windows
cv2.destroyAllWindows()