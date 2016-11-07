import numpy as np
import moves as m

def vector_angle(v1, v2):
    l1 = np.sqrt(np.power(v1[0], 2) + np.power(v1[1], 2))
    l2 = np.sqrt(np.power(v2[0], 2) + np.power(v2[1], 2))
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    return np.arccos(np.divide(dot, (l1 * l2)))


def where_to_go(particle, goal):
    """ Takes a particle (which must be our best bet for our actual position)
    and the place we want to be (goal = [x, y])

    returns a list of the length the robot needs to drive, the degrees it
    needs to turn and the direction it needs to turn"""
    ang = vector_angle(particle, goal)
    if ang <= 180:
        turn_dir = 'right'
        turn_deg = ang
    else:
        turn_dir = 'left'
        turn_deg = 180 - ang
    length = np.sqrt(
        np.power((particle[0] - goal[0]), 2) + np.power(
            (particle[0] - goal[1]), 2))
    return [length, turn_dir, turn_deg]

def control_frindo(l, d_t, est_pos, frindo):
    if l[0] == l[1] == 1:
        print "i'm in control -> case: 2 landmarks"
        x = where_to_go(est_pos, [150, 0])
        dist_drive = x[0]
        former_turn = d_t
        if x[1] == 'right':
            deg_turn = x[2]
        elif x[1] == 'left':
            deg_turn = -1.0 * x[2]
        m.turn_baby_turn(x[2], x[1], frindo)
        m.lige_gear(frindo, x[0])

    elif l[0] + l[1] == 1 and d_t > 360:
        print "i'm in control -> case: 1 landmarks"
        raise

    else:
        print "i'm in control -> case: 0 landmarks"
        dist_drive = 0.0
        deg_turn = -10.0
        former_turn = d_t + 10.0
        m.turn_baby_turn(deg_turn, 'left', frindo)

    return [dist_drive, deg_turn, former_turn]
