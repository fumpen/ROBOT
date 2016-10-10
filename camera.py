from picamera.array import PiRGBArray
import picamera
import cv2
import numpy as np
import time

# The box size in cm.
# Used to calculate the focal length

SIZE_BOX = 27.5


# File name on the files
# used to calculate focal length.

distances = ['3m', '2_75m', '2_5m', '2_25m', '2m', '1_75m', '1_5m', '1_25m']

#Colors
greenLower = np.array([40, 100, 50])
greenUpper = np.array([89, 255, 255])



def capturePerm(name):

    file = "image/" + name + '.png'
    print("Taking picture")

    with picamera.PiCamera() as camera:
	with picamera.array.PiRGBArray(camera) as output:
	    
            time.sleep(1)

	    camera.framerate = 30
	    camera.shutter_speed = camera.exposure_speed
	    camera.exposure_mode = 'off'

            gain = camera.awb_gains
            camera.awb_mode='off'
	    gain = (1.5, 1.5)
            camera.awb_gains = gain

	    camera.capture(output, format="bgr")
	    img = output.array


    	    cv2.imwrite(file, img)

	    output.truncate(0)
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

		if radius > 15:
		    cv2.circle(mask, (int(x), int(y)), int(radius),
					(0, 255, 255), 2)
		    cv2.circle(mask, center, 5, (100, 100, 100), -1)

            cv2.imwrite(file, img)
            cv2.imwrite(file2, mask)

	    output.truncate(0)
    print(center)
    return center[0]


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


def pixels(name):

    img = cv2.imread("imgTest/" + name + '.png')

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=4)
    mask = cv2.dilate(mask, None, iterations=4)


    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None

    vertical = 0

    if(len(cnts) > 0):
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
	
	if radius > 20:
		min_y = np.min(np.min(c, axis=1), axis=0)[1]
		max_y = np.max(np.max(c, axis=1), axis=0)[1]
		
		vertical = max_y - min_y
	
	

    return vertical




def focalLength(pixel, distance, boxSize):
	focal = (pixel * distance) / boxSize
	
	return focal



def distance(boxSize, focal, pixel):
	distance = (boxSize * focal) / pixel
	
	return distance


# Calculate the average pixel
# Used to calculate the average focal length

def averagePix(name):
    N = len(name)
    pix_sum = 0

    for i in distances:
        pix_sum += pixels(i)		

    return (pix_sum / N)

print(averagePix(distances))

# Makes a list of pixel size

def listPix(ls):
    pix_list = []
    pix_sum = 0

    for i in ls:
        pix_list.append(pixels(i))

    return pix_list



def statistic_Distance(files):
	pix_avg = averagePix(files)
	average_distance = 212

	listx = listPix(files)
	foc = focalLength(pix_avg, average_distance, 27.5)

	print("Measure\t\tCalculated\tDifference")

	total = 325
	step = 25

	for i in listx:
		total -= step
		calc = distance(SIZE_BOX, foc, i)
		diff = calc - total
		print("%i\t\t%.2f\t\t%.2f" % (total, calc, diff))



