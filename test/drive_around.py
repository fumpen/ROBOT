import hacked_path
import moves as mv

while True:
    mv.forward_stop()

    if mv.rightSensor() > mv.leftSensor():
        mv.turn_left_stop()
    else:
        mv.turn_right_stop()
