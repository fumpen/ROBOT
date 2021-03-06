import numpy as np
import random_numbers as rn

class Particle(object):
    """Data structure for storing particle information (state and weight)"""

    def __init__(self, x = 0.0, y = 0.0, theta = 0.0, weight = 0.0):
        self.x = x
        self.y = y
        self.theta = theta
        self.weight = weight

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getTheta(self):
        return self.theta

    def getWeight(self):
        return self.weight

    def getDegree(self):
	return np.degrees(self.theta)

    def setX(self, val):
        self.x = val

    def setY(self, val):
        self.y = val

    def setTheta(self, val):
        self.theta = val

    def setWeight(self, val):
        self.weight = val

    def __repr__(self):
        return '[x=%.6s y=%.6s theta=%.6s]' % (str(self.x), str(self.y),
                                               str(self.getDegree()))


def estimate_pose(particles_list):
    """Estimate the pose from particles by computing the average position and orientation over all particles.
    This is not done using the particle weights, but just the sample distribution."""
    x_sum = 0.0; y_sum = 0.0; cos_sum = 0.0; sin_sum = 0.0;

    for particle in particles_list:
        x_sum += particle.getX()
        y_sum += particle.getY()
        cos_sum += np.cos(particle.getTheta())
        sin_sum += np.sin(particle.getTheta())

    flen = len(particles_list)
    if flen != 0:
        x = x_sum / flen
        y = y_sum / flen

        theta = np.arctan2(sin_sum/flen, cos_sum/flen)
    else:
        x = x_sum
        y = y_sum
        theta = 0.0
    return Particle(x, y, theta)

def move_particle(particle, delta_x, delta_y, delta_theta):
    """Move the particle by (delta_x, delta_y, delta_theta)"""
    current_x = particle.getX()
    current_y = particle.getY()
    current_tetha = particle.getTheta()

    particle.setX(current_x + delta_x)
    particle.setY(current_y + delta_y)
    particle.setTheta(delta_theta)


def add_uncertainty(particles_list, sigma, sigma_theta):
    """Add some noise to each particle in the list. Sigma and sigma_theta is the noise variances for position and angle noise."""
    for particle in particles_list:
        particle.x += rn.randn(0.0, sigma)
        particle.y += rn.randn(0.0, sigma)
        new_theta = np.degrees(particle.theta) + np.random.normal(0, sigma_theta)
        if new_theta < -180.0:
            particle.theta = np.radians(new_theta + 360.0)
        elif new_theta >= 180.0:
            particle.theta = np.radians(new_theta - 360.0)
        else:
            particle.theta = np.radians(new_theta)


def add_uncertainty_von_mises(particles_list, sigma, theta_kappa):
    """Add some noise to each particle in the list. Sigma and theta_kappa is the noise variances for position and angle noise."""
    for particle in particles_list:
        particle.x += rn.randn(0.0, sigma)
        particle.y += rn.randn(0.0, sigma)
        particle.theta = np.mod(rn.rand_von_mises (particle.theta, theta_kappa), 2.0 * np.pi) - np.pi
