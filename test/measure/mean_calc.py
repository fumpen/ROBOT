import os
import math
import numpy as np
import argparse as ap

#program arguments
parser = ap.ArgumentParser(description='process sensor data.')
parser.add_argument('sensor', help='sensor data to process')
args = parser.parse_args()

if args.sensor == "front" or "left" or "right" or "driveFront" or "driveLeft" or "driveRight":
  print "processing data from ", args.sensor, " sensor"
else:
  print "program takes 'front', 'left' or 'right' as input"

mean_ir_vals = []

for fn in os.listdir('.'):
  if os.path.isfile(fn) and fn.startswith(args.sensor) and fn != 'ir_plot.py':
    print fn
    f = open(fn, 'r')
    nums = [int(n) for n in f.read().split()]
    f.close()
    mean = np.mean(nums)
    mean_ir_vals.append(mean)

print "means:", mean_ir_vals

