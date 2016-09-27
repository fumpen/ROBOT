from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import time


cam = PiCamera()
rawCapture = PiRGBArray(cam)


def capture(name):

    file = "image/" + name + '.png'
    print("Taking picture")
    
    cam.capture(rawCapture, format="bgr")
    image = rawCapture.array
    cv2.imwrite(file, image)
    
    print("Location: " + file)



#Colors
greenLower = np.array([29, 86, 6])
greenUpper = np.array([64, 255, 255])

lower_blue = np.array([110,50,50])
upper_blue = np.array([130,255,255])


def findColor(name):
    img = cv2.imread("image/" + name + '.png')
    
    blur = cv2.GaussianBlur(img, (5,5), 0)    
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)   
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    
    bmask = cv2.GaussianBlur(mask, (5,5), 0)

    
    cv2.imwrite('image/' + name + 'Color.png', bmask)



