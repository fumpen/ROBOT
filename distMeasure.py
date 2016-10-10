import numpy as np
import cv2

def focalLength (Z, h, H):
    return (Z * h)/(H)

print focalLength(3, 40, 0.31)
