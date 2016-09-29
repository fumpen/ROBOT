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
greenLower = np.array([58, 100, 50])
greenUpper = np.array([89, 255, 255])



def findColor(name):
    img = cv2.imread("image/" + name + '.png')
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)   
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    
    cv2.imwrite('image/' + name + 'Color.png', mask)


findColor('first');
findColor('sec');
findColor('third');
findColor('fourth');
findColor('test5');
findColor('test6');
findColor('test7');
findColor('test8');

