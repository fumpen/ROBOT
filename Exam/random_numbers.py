import math
import numpy as np

def Gaussian(mu, sigma, x):
   

    return math.exp(- (np.power((mu - x), 2)) / np.power(sigma, 2) / 2.0) / math.sqrt(2.0 * math.pi * np.power(sigma, 2))
