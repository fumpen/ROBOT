import numpy as np
import cv2

def focalLength (Z, H, h):
    return (Z * h)/(H)

def distToBox (f, H, h):
    return f*H/h

def distToUnknownBox(D, p1, p2):
    return D*p1/(p2-p1)

a = focalLength(3, 0.31, 40)
print distToBox(a, 0.31, 40)
print distToUnknownBox(0.2, 350, 351)
