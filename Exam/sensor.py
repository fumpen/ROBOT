SENSOR_GEAR = {1: 300,
               2: 290,
               3: 280,
               4: 270,
               5: 260,
               6: 250,
               7: 240}

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

def allSensor(frindo):
    return (rightSensor(frindo) < 350 and
            frontSensor(frindo) < 350 and
            leftSensor(frindo) < 350)


def allSensor_gear(frindo, gear):
    g = SENSOR_GEAR[gear]
    if (rightSensor(frindo) < g and frontSensor(frindo) < g
        and leftSensor(frindo) < g):
        return True
    else:
        return False

# Returns true for each sensor within range of an object
def determine_way_around(frindo):
    right = False
    left = False
    forward = False
    if rightSensor(frindo) > 280:
        right = True
    if frontSensor(frindo) > 280:
        forward = True
    if leftSensor(frindo) > 280:
        left = True
    print 'Right: ' + str(right) + ', Left: ' + str(left) + ', Forward: ' + str(forward)
    return right, left, forward
