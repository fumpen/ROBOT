# ===========================================
#
# Filename: world.py
#
# Description: 
#
# Contains a world simulation for the robot
#
# ===========================================
import cv2
import numpy as np
import robot
import random
import math
import camera
import particle
import random_numbers
from time import sleep

# ===========================================
# 
# COLOR CONSTANTS
#
# ===========================================

CRED = (0, 0, 255)
CGREEN = (0, 255, 0)
CBLUE = (255, 0, 0)
CCYAN = (255, 255, 0)
CYELLOW = (0, 255, 255)
CMAGENTA = (255, 0, 255)
CWHITE = (255, 255, 255)
CBLACK = (0, 0, 0)

# ===========================================
# 
# LANDMARKS
#
# ===========================================
LANDMARKS = [
             (0, 0),
             (300, 0),
             (0, 300),
             (300, 300)]

LANDMARK_FLAGS = [0, 0, 0, 0]

# === FUNCTION ==============================
# 
# Description:
#
# When the robot is in correct range of
# landmark.
#
# ===========================================
def set_Flag(flagNumb):
    LANDMARK_FLAGS[flagNumb] = 1


# === FUNCTION ==============================
# 
# Description:
#
# Check if all landmarks are located.
#
# ===========================================
def all_located():
    return all(flag == 1 for flag in LANDMARK_FLAGS)



# === FUNCTION ==============================
# 
# Description:
#
# Determine which landmark the robot detected
#
# ===========================================
def determineLandmark(colorProb, objectType):
    
    if colorProb[1] >= colorProb[0]:
        color = 'Green'
    else:
        color = 'Red'

    if color == 'Red' and objectType == 'vertical':
        landmark = 0
    elif color == 'Green' and objectType == 'horizontal':
        landmark = 1
    elif color == 'Green' and objectType == 'vertical':
        landmark = 2
    elif color == 'Red' and objectType == 'horizontal':
        landmark = 3

    return landmark



# === FUNCTION ==============================
# 
# Description:
#
# Particle color function, determines color
# according to weight of particle.
#
# ===========================================
def jet(x):
    """Colour map for drawing particles. This function determines the colour of 
    a particle from its weight."""
    r = (x >= 3.0/8.0 and x < 5.0/8.0) * (4.0 * x - 3.0/2.0) + (x >= 5.0/8.0 and x < 7.0/8.0) + (x >= 7.0/8.0) * (-4.0 * x + 9.0/2.0)
    g = (x >= 1.0/8.0 and x < 3.0/8.0) * (4.0 * x - 1.0/2.0) + (x >= 3.0/8.0 and x < 5.0/8.0) + (x >= 5.0/8.0 and x < 7.0/8.0) * (-4.0 * x + 7.0/2.0)
    b = (x < 1.0/8.0) * (4.0 * x + 1.0/2.0) + (x >= 1.0/8.0 and x < 3.0/8.0) + (x >= 3.0/8.0 and x < 5.0/8.0) * (-4.0 * x + 5.0/2.0)

    return (255.0*r, 255.0*g, 255.0*b)




# === FUNCTION ==============================
# 
# Description:
#
# Calculates the probability of a particle
#
# ===========================================
def diff_weight(diff, varians):
    return (1/(math.sqrt(2*np.pi*varians))) * (np.exp(-np.divide(diff**2, 2* varians)))

def weight(p, obs_angle, obs_dist, mark_nr):
    part2Mark = particle_landmark_vector(mark_nr, p)
    mark_dist = dist_vector(part2Mark)
    dist_diff = abs(obs_dist - mark_dist)
    if dist_diff <= 0.000001:
        dist_diff = 0.00001
    dist_weight = diff_weight(dist_diff, 0.5)

    orientation = direction(p.getTheta())
    angle_to_mark = angle_between(orientation, part2Mark)
    angle_diff = abs(angle_to_mark - obs_angle)
    if angle_diff <= 0.00001:
        angle_digg = 0.0001
    angle_weight = diff_weight(angle_diff,1)


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

        list_of_particles.append([dist_w*0.60, angle_w*0.40, p])

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

    return list_of_particles[:,2]




# === FUNCTION ==============================
# 
# Description:
#
# resample the particles.
#
# ===========================================
def resample(particles):
    length = len(particles)
    p3 = []
    index = int(random.random() * length)
    beta = 0.0
    
    mw = 0
    for p in particles:
        mw = max(mw, p.getWeight())


    for i in range(length):
        beta += random.random() * 2.0 * mw
        
        while beta > particles[index].getWeight():
            beta -= particles[index].getWeight()
            index = (index + 1) % length

        p = particles[index]
	p3.append(particle.Particle(p.getX(), p.getY(), p.getTheta(), 1.0/length))

    particle.add_uncertainty(p3, 10, 15)
        
    return p3

# === FUNCTION ==============================
# 
# Description:
#
# Makes a graphically illustration of the
# robot world.
#
# ===========================================
def draw_world(world, est_pose, particles):
    
    offset = 100;
    
    world[:] = CWHITE
    
    # Find largest weight
    max_weight = 0
    for particle in particles:
        max_weight = max(max_weight, particle.getWeight())


    for particle in particles:
        x = int(particle.getX()) + offset
        y = int(particle.getY()) + offset

        colour = jet(particle.getWeight() / max_weight)
        
        cv2.circle(world, (x, y), 2, colour, 2)
        
        b = (int(particle.getX() + 15.0*np.cos(particle.getTheta()))+offset, 
                                     int(particle.getY() - 15.0*np.sin(particle.getTheta()))+offset)
        cv2.line(world, (x,y), b, colour, 2)



    # Draw landmarks
    lm0 = (LANDMARKS[0][0]+offset, LANDMARKS[0][1]+offset)
    lm1 = (LANDMARKS[1][0]+offset, LANDMARKS[1][1]+offset)
    lm2 = (LANDMARKS[2][0]+offset, LANDMARKS[2][1]+offset)
    lm3 = (LANDMARKS[3][0]+offset, LANDMARKS[3][1]+offset)

    cv2.circle(world, lm0, 5, CRED, 2)
    cv2.circle(world, lm1, 5, CGREEN, 2)
    cv2.circle(world, lm2, 5, CGREEN, 2)
    cv2.circle(world, lm3, 5, CRED, 2)
    
    # Draw Robot estimation
    x     = int(est_pose.getX() + offset)
    y     = int(est_pose.getY() + offset)
    theta = est_pose.getTheta()

    direction = (int(est_pose.getX() + 15.0 * np.cos(theta)) + offset,
                 int(est_pose.getY() - 15.0 * np.sin(theta)) + offset) 
    
    cv2.circle(world, (x, y), 5, CMAGENTA, 2)
    cv2.line(world, (x, y), direction, CMAGENTA, 2)
 

# ===========================================
# 
# MAIN PROGRAM
#
# ===========================================
WIN_World = "World view";
cv2.namedWindow(WIN_World);
cv2.moveWindow(WIN_World, 500, 50);

# Allocate space for world map
world = np.zeros((500,500,3), dtype=np.uint8)

# Initialize particles
num_particles = 1000
particles = []

for i in range(num_particles):
   
    x = 500.0 * np.random.ranf() - 100
    y = 500.0 * np.random.ranf() - 100

    theta = random.random() * 2 * math.pi


    weight = 1.0 / num_particles


    p = particle.Particle(x, y, theta, weight)

    p.setNoise(0.05, 0.05, 5.0)
    particles.append(p)

est_pose = particle.estimate_pose(particles)

# Initialize robot
frindo = robot.Robot()


# Draw map
draw_world(world, est_pose, particles) 



cam = camera.Camera(0, 'frindo')

# Main loop
while True:
    
    action = cv2.waitKey(10) 

    # Fetch next frame
    colour, distorted = cam.get_colour()    
    
    
    # Detect objects
    objectType, measured_distance, measured_angle, colourProb = cam.get_object(colour)
    
    if objectType != 'none':
        mark = determineLandmark(colourProb, objectType)
 
        print "Found mark!"

	particles = resample(particles)
	
	
        # Draw detected pattern
        cam.draw_object(colour)
    else:

	for p in particles:
	    p.setWeight(1.0 / num_particles)

        
    # Draw map
    draw_world(world, est_pose, particles)

    # Show world
    cv2.imshow(WIN_World, world)



# Close all windows
cv2.destroyAllWindows()
