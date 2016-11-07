import sensor as s
import datetime
import robot

frindo = robot.Robot()

q = 0.0
for x in range(0, 1000):
    asd = datetime.datetime.now()
    s.allSensor_gear(frindo, 3)
    qwe = datetime.datetime.now()
    q += (qwe - asd).total_seconds()

print q

q = 0.0
for x in range(0, 1000):
    asd = datetime.datetime.now()
    s.allSensor_gear(frindo, 3)
    qwe = datetime.datetime.now()
    q += (qwe - asd).total_seconds()

print q
