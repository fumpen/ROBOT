from picamera.array import PiRGBArray
import picamera
import cv2
import numpy as np
import time


#cam = PiCamera()
#rawCapture = PiRGBArray(cam)


def capturePerm(name):
    file = "image/" + name + '.png'
    print("Taking picture")

    with picamera.PiCamera() as camera:
	with picamera.array.PiRGBArray(camera) as output:
	    camera.capture(output, format="bgr")
	    img = output.array
    
    
    cv2.imwrite(file, img)
    
    print("Location: " + file)


def capture(name, name2):

    file = "image/" + name + '.png'
    file2 = "image/" + name2 + '.png'
    
    with picamera.PiCamera() as camera:
	with picamera.array.PiRGBArray(camera) as output:
	    camera.capture(output, format="bgr")
	    img = output.array

	    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)   
	    mask = cv2.inRange(hsv, greenLower, greenUpper)
	    mask = cv2.erode(mask, None, iterations=4)
	    mask = cv2.dilate(mask, None, iterations=4)   
	    
	    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
	    center = (0, 0)

	    if(len(cnts) > 0):
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		
		if radius > 10:
		    cv2.circle(mask, (int(x), int(y)), int(radius),
					(0, 255, 255), 2)
		    cv2.circle(mask, center, 5, (100, 100, 100), -1) 
            
            cv2.imwrite(file, img)
            cv2.imwrite(file2, mask)
	    
	    output.truncate(0)
    print(center)
    return center[0]

#Colors
greenLower = np.array([35, 90, 50])
greenUpper = np.array([89, 255, 255])



def findColor(name):
    img = cv2.imread("image/" + name + '.png')
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)   
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=4)
    mask = cv2.dilate(mask, None, iterations=4)   
    
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None

    if(len(cnts) > 0):
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        
        if radius > 10:
            cv2.circle(mask, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
	    cv2.circle(mask, center, 5, (100, 100, 100), -1)
	
    cv2.imwrite('image/' + name + 'Color.png', mask)
    
    
    return center

capturePerm('new4')
