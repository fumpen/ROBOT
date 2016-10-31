import robot
import moves

def frontSensor(frindo):
    return frindo.read_front_ir_sensor()

def rightSensor(frindo):
    return frindo.read_right_ir_sensor()

def leftSensor(frindo):
    return frindo.read_left_ir_sensor()

def allSensorBoundary(frindo):
    while (rightSensor(frindo) < 300 and
           frontSensor(frindo) < 300 and
           leftSensor(frindo) < 300):
        continue
    return 0

<<<<<<< HEAD
=======
def allSensor(frindo):
    return (rightSensor(frindo) < 350 and
            frontSensor(frindo) < 350 and
            leftSensor(frindo) < 350)


>>>>>>> 7870ac77d37b39928fc8f3998011584099dc4cb6
def rightSensorBoundary(frindo):
    while rightSensor(frindo) < 300:
        continue
    return 0

def frontSensorBoundary(frindo):
    while frontSensor(frindo) < 300:
        continue
    return 0

def leftSensorBoundary(frindo):
    while leftSensor(frindo) < 300:
        continue
    return 0

def rightSensorFree(frindo):
    while rightSensor(frindo) > 325:
        continue
    return 0

def frontSensorFree(frindo):
    while frontSensor(frindo) > 325:
        continue
    return 0

def leftSensorFree(frindo):
    while leftSensor(frindo) > 325:
        continue
    return 0

def obstacle_ident(frindo):
    if frontSensor(frindo) >= frontSensorBoundary(frindo):
        if rightSensor(frindo) >= rightSensorBoundary(frindo):
            if leftSensor(frindo) >= leftSensorBoundary(frindo):
                return 0


<<<<<<< HEAD
def forward_stop(frindo):
=======
def forward_stop(frindo, timer):
>>>>>>> 7870ac77d37b39928fc8f3998011584099dc4cb6
    """The robot drives straight forward until being within 10 cm of an
    opstackle, then stopping in place
    :return: nothing
    """
<<<<<<< HEAD
    if moves.BATTERY:

        frindo.go_diff(102,123,1,1)
        allSensorBoundary(frindo)
=======

    if moves.BATTERY:

        #frindo.go_diff(102,123,1,1)
        start = time.time()
        while not allSensor(frindo) and (time.time() - start) < timer:
            continue
>>>>>>> 7870ac77d37b39928fc8f3998011584099dc4cb6
        print "Found Object"

    else:

        frindo.go_diff(66,83,1,1)
        allSensorBoundary(frindo)
        print "Found Object"


    frindo.stop()
    moves.pause()

#
def turn_right_stop(frindo):
    """Rotates clockwise untill front and left sensor is free,
    making the robot stand parallel with object in front.
    :return: nothing
    """
    if moves.BATTERY:

        frindo.go_diff(100,123,1,0)
        frontSensorFree()
        leftSensorFree()
        print "free"

    else:
        frindo.go_diff(110,128,1,0)

    frindo.stop()
    moves.pause()

def turn_left_stop(frindo):

    if moves.BATTERY:

        frindo.go_diff(100,123,0,1)
        frontSensorFree(frindo)
        rightSensorFree(frindo)
        print "free"

    else:
        frindo.go_diff(110,128,1,0)

    frindo.stop()
    moves.pause()
