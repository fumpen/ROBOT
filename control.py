import robot
import moves
import sensor

frindo = robot.Robot()
BATTERY = 1


def trial_forward_func(cm):
    moves.scale(cm, frindo, BATTERY)