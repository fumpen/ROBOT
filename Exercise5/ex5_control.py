import ex5_i_love_brainz as p
import moves as m
import robot
import camera
import numpy as np
import math

# just for quriosity..
"""
x = p.innit_particles(1000)


z = []
former_weight = 0.0
for y in x:
    f_weight = former_weight
    former_weight += y.getWeight()
    z.append([f_weight, former_weight, y])

q = []
z_len = len(z)
for b in z:
    dicto = {'i': 500,
             'n': 2}
    q.append(p.in_range(z, np.random.uniform(0.0, 1.0), dicto, z_len))
"""
# setup config
frindo = robot.Robot()
cam = camera.Camera(0, 'frindo')

LANDMARK_1 = 0
LANDMARK_2 = 0


def find_landmark(particles, previously_moved=0.0):
    degrees_moved = previously_moved
    move_pr_turn = 45.0
    while degrees_moved <= 360:
        m.turn_baby_turn(move_pr_turn, 'right', frindo)
        degrees_moved += move_pr_turn
        ret = p.update_particles(particles, 0, ((-1.0) * move_pr_turn))
        if ret[1][3]:
            break
        else:
            ret = None
    return [ret, degrees_moved]

particles = p.innit_particles()

print find_landmark(particles)
"""
while True:
    if LANDMARK_1 and LANDMARK_2:
        # go to center
    elif LANDMARK_1 or LANDMARK_2:
    else:
        # find a landmark
"""