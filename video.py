# Example showing how to grab frames using the PiCamera module instead of OpenCV
# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from fractions import *
import numpy as np
import time
import cv2
import robot
import moves
import sensor

frindo = robot.Robot()

BATTERY = 1

SIZE_BOX = 27.5

AVG_PIX = 88
AVG_DISTANCE = 212

FOCAL = (AVG_PIX * AVG_DISTANCE) / SIZE_BOX

#Colors
greenLower = np.array([43, 72, 35])
greenUpper = np.array([85, 255, 255])
# initialize the camera and grab a reference to the raw camera capture

camera = PiCamera()
time.sleep(1) # Wait for camera

camera.resolution = (736, 480)
camera.framerate = 30

camera.shutter_speed = camera.exposure_speed
camera.exposure_mode = 'off'

gain = camera.awb_gains
camera.awb_mode='off'
#gain = (Fraction(2,1), Fraction(1,1))
#gain = (1.5, 1.5)
camera.awb_gains = gain

print "shutter_speed = ", camera.shutter_speed
print "awb_gains = ", gain

rawCapture = PiRGBArray(camera, size=camera.resolution)

# Open a window
# WIN_RF = "Frame";
# cv2.namedWindow(WIN_RF);
# cv2.moveWindow(WIN_RF, 100       , 100);

# allow the camera to warmup
time.sleep(0.1)
def video():
	# capture frames from the camera
	for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		# grab the raw NumPy array representing the image
		image = frame.array

		hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
		mask = cv2.inRange(hsv, greenLower, greenUpper)
		mask = cv2.erode(mask, None, iterations=4)
		mask = cv2.dilate(mask, None, iterations=4)

		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
		center = (0, 0)

		if(len(cnts) > 0):
		    c = max(cnts, key=cv2.contourArea)
		    ((x, y), radius) = cv2.minEnclosingCircle(c)

		    if radius > 20:
		        M = cv2.moments(c)
		        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

			cv2.circle(mask, (int(x), int(y)), int(radius),
						(0, 255, 255), 2)
			cv2.circle(mask, center, 5, (100, 100, 100), -1)

			min_y = np.min(np.min(c, axis=1), axis=0)[1]
			max_y = np.max(np.max(c, axis=1), axis=0)[1]

			vertical = max_y - min_y

			distance = (SIZE_BOX * FOCAL) / vertical

		if sensor.frontSensor(frindo) < 300 and \
		   sensor.rightSensor(frindo) < 300 and \
		   sensor.leftSensor(frindo) < 300:

			if(center[0] == 0):
			    moves.turn_left(frindo, 50, BATTERY)
			    time.sleep(0.2)
			elif(center[0] > 0 and center[0] < 340):
				z = np.divide(50, 368.) * (368 - center[0])

				print("Calibrating center")
				moves.turn_left(frindo, int(z), BATTERY)
			elif(center[0] > 396):
				z = np.divide(50, 368.) * (center[0] - 368)

				print("Calibrating center")
				moves.turn_right(frindo, int(z), BATTERY)
			else:
				print(distance)
				moves.forwardv2(frindo, 25, BATTERY)
		else:
			print("Destination arrived!")

		# show the frame
		# cv2.imshow(WIN_RF, mask)
		# key = cv2.waitKey(4) & 0xFF

		# clear the stream in preparation for the next frame
		# rawCapture.truncate(0)

		# if the `q` key was pressed, break from the loop
		#if key == ord("q"):
		#	break



video()
