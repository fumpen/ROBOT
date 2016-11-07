import sensor as s
import datetime
import robot

frindo = robot.Robot()

for x in range(0, 7):
    asd = datetime.datetime.now()
    s.allSensor_gear(frindo, 3)
    qwe = datetime.datetime.now()

    print (qwe - asd).total_seconds()
