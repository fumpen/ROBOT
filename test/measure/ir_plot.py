import os
import math
import numpy as np
import argparse as ap
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

#program arguments
parser = ap.ArgumentParser(description='process sensor data.')
parser.add_argument('sensor', help='sensor data to process')
args = parser.parse_args()

if args.sensor == "front" or "left" or "right" or "driveFront" or "driveLeft" or "driveRight":
  print "processing data from ", args.sensor, " sensor"
else:
  print "program takes 'front', 'left' or 'right' as input"

mean_ir_vals = []
var_ir_vals = []
distance = np.array([10, 20, 30, 40, 50, 60, 70, 80])

for fn in os.listdir('.'):
  if os.path.isfile(fn) and fn.startswith(args.sensor) and fn != 'ir_plot.py':
    print fn
    f = open(fn, 'r')
    nums = [int(n) for n in f.read().split()]
    f.close()
    mean = np.mean(nums)
    var = np.var(nums)
    mean_ir_vals.append(mean)
    var_ir_vals.append(var)
mean_np = np.array(mean_ir_vals)
print "means:", mean_ir_vals
print "variances:", var_ir_vals
def func(x, a, c, d):
    return a*np.exp(-c*x)+d

popt, pcov = curve_fit(func, mean_np, distance, p0=(1, 1e-6, 1))
print "a:", popt[0], "\nb:", popt[1], "\nc:", popt[2]
print "function: a*exp(-b*x)+c"
xx = np.linspace(50, 450, 1000)
yy = func(xx, *popt)

plt.plot(mean_ir_vals, distance, 'ko')
plt.plot(xx,yy)
plt.title(args.sensor + " sensor")
plt.xlabel("sensor output")
plt.ylabel("distance (cm)")
plt.xlim([50,450])
plt.ylim([5,85])
plt.show()
