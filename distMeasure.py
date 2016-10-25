from  __future__ import division
import numpy as np
import camera
import cv2

def focalLength (Z, H, h):
    return float(Z * h)/float(H)

def distToBox (f, H, h):
    return float(f*H)/float(h)

def distToUnknownBox(D, p1, p2):
    return D*p1/(p2-p1)

pics = ["1_25m", "1_5m", "1_75m", "2m", "2_25m", "2_5m", "2_75m", "3m"]
dist = [1.25, 1.50, 1.75, 2.00, 2.25, 2.50, 2.75, 3.00]
focal = []
pixel = []

dummy = "demo"

camera.capturePerm(dummy)

camera.findColor(dummy)

pix = camera.pixels(dummy)
#print pix

#foc = focalLength(, 31, pix)
#print foc

focal = 623.991935484

avg_foc = 0


for item in pics:
    pix_tmp = camera.pixels(item)
    pixel.append(pix_tmp)

for i in range(0, len(pics)):
    tmp = focalLength(dist[i], 0.31, pixel[i])
    #print tmp
    avg_foc += tmp

avg_foc /= len(pics)

#avg_foc =  camera.statistic_Distance(pics)

print avg_foc

print distToBox(avg_foc, 0.295, pix)
# print distToUnknownBox(50, pixel[7], pixel[5])
