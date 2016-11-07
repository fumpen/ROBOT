import numpy as np
import random
import random_numbers as rn
import math

class Particle(object):
    """Data structure for storing particle information (state and weight)"""
    
    def __init__(self, x = 0.0, y = 0.0, theta = 0.0, weight = 0.0):
        # Position and orientation of robot
        self.x      = x
        self.y      = y
        self.theta  = theta
        self.weight = weight
    
        # Noise in movement and sensor
        self.move_noise = 0.0
        self.turn_noise = 0.0
        self.cam_noise  = 0.0

    def getX(self):
        return self.x
        
    def getY(self):
        return self.y
        
    def getTheta(self):
        return self.theta
    
    def getThetaDegree(self):
        return np.degrees(self.theta)

    def getCamNoise(self):
        return self.cam_noise

    def getWeight(self):
        return self.weight

    def setX(self, val):
        self.x = val

    def setY(self, val):
        self.y = val

    def setTheta(self, val):
        self.theta = val

    def setWeight(self, val):
        self.weight = val

    def setNoise(self, new_move_noise, new_turn_noise, new_cam_noise):
        self.move_noise = float(new_move_noise)
        self.turn_noise = float(new_turn_noise)
        self.cam_noise = float(new_cam_noise)
    
    def set(self, new_x, new_y, new_theta):
        if new_theta < 0 or new_theta >= 2 * math.pi:
            raise 'Theta must be in [0 .. 2pi]'
        
        self.x     = float(new_x)
        self.y     = float(new_y)
        self.theta = float(new_theta)


    def Gaussian(self, mu, sigma, x):
        return exp(- ((mu - x) ** 2) / (sigma ** 2) / 2.0) / math.sqrt(2.0 * pi * (sigma ** 2))

    
    # === ROBOT REPRESENTATIVE ========================
    # 
    # Description:
    #
    # Function to display particle coordinates and 
    # orientation.
    #
    # ================================================
    def __repr__(self):
        return '[x=%.6s y=%.6s theta=%.6s]' % (str(self.x), str(self.y),
                                               str(self.getThetaDegree()))

def estimate_pose(particles_list):
    """Estimate the pose from particles by computing the average position and orientation over all particles. 
    This is not done using the particle weights, but just the sample distribution."""
    x_sum = 0.0; y_sum = 0.0; cos_sum = 0.0; sin_sum = 0.0
     
    for particle in particles_list:
        x_sum += particle.getX()
        y_sum += particle.getY()
        cos_sum += np.cos(particle.getTheta())
        sin_sum += np.sin(particle.getTheta())
        
    flen = len(particles_list)
    if flen !=0:
        x = x_sum / flen
        y = y_sum / flen
        theta = np.arctan2(sin_sum/flen, cos_sum/flen)
    else:
        x = x_sum
        y = y_sum
        theta = 0.0
        
    return Particle(x,y,theta)
     
     
def move_particle(particle, turn, distance):
    # Turn robot
    theta = particle.theta + float(np.radians(turn)) + random.gauss(0.0, particle.turn_noise)

    theta %= 2 * math.pi

    # Move
    dist = float(distance) + random.gauss(0.0, particle.move_noise)

    x = particle.x + (np.cos(theta) * dist)
    y = particle.y + (np.sin(theta) * dist)


    # Set robot Coordinates
    particle.set(x, y, theta)

def move_Allparticle(particles, turn, distance):
    for p in particles:
	move_particle(p, turn, distance)	



def add_uncertainty(particles_list, sigma, sigma_theta):
    """Add some noise to each particle in the list. Sigma and sigma_theta is the noise variances for position and angle noise."""
    for particle in particles_list:
        particle.x += rn.randn(0.0, sigma) #np.random.uniform(0.0, sigma)
        particle.y += rn.randn(0.0, sigma) # (particle.getY()+ np.random.uniform(0.0, sigma))
        #print particle.theta
        new_theta = np.degrees(particle.theta) + np.random.uniform(-sigma_theta, sigma_theta)
        if new_theta < -180.0:
            particle.theta = np.radians(new_theta + 360.0)
        elif new_theta >= 180.0:
            particle.theta = np.radians(new_theta - 360.0)
        else:
            particle.theta = np.radians(new_theta)
        #print particle.theta
        #(np.mod(particle.getTheta() + np.random.uniform(particle.theta, sigma_theta), 2.0 * np.pi))
