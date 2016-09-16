import os
import argparse as ap
import matplotlib.pyplot as plt

#program arguments
parser = ap.ArgumentParser(description='process sensor data.')
parser.add_argument('sensor', help='sensor data to process')
args = parser.parse_args()

if args.sensor == "front" or "left" or "right":
  print "processing data from ", args.sensor, " sensor"
else:
  print "program takes 'front', 'left' or 'right' as input"

mean_ir_vals = []
distance = [10, 20, 30, 40, 50, 60, 70, 80]

for fn in os.listdir('.'):
  if os.path.isfile(fn) and fn.startswith(args.sensor) and fn != 'ir_plot.py':
    print fn
    f = open(fn, 'r')
    nums = f.read().split()
    f.close()
    avg = sum([int(n) for n in nums]) / len(nums)
    mean_ir_vals.append(avg)
print mean_ir_vals
plt.plot(mean_ir_vals, distance)
plt.xlabel("sensor output")
plt.ylabel("distance")
plt.show()

#front sensor function: 7.377335+211.937*e^(-0.01906072*x)

