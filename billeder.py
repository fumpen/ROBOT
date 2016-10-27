import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
import numpy as np
import argparse
import cv2

# construct the argument parse and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", help="path to the image")
# args = vars(ap.parse_args())

# load the image
# image = cv2.imread(args["image"])
image = cv2.imread('hej5.png')

boundaries = [([0, 30, 0], [30, 250, 30])]
#([0, 102, 51], [51, 255, 51])

# loop over the boundaries
for (lower, upper) in boundaries:
    # create NumPy arrays from the boundaries
    # lower = np.array(lower, dtype="uint8")
    # upper = np.array(upper, dtype="uint8")
    lower = np.array(lower)
    upper = np.array(upper)

res_arr = []
tem_arr = []
len = 480
q_2 = 0
for x in image:
    z_1 = 0
    q_1 = 0
    l_1 = 0
    for y in x:
        if lower[0] <= y[0] <= upper[0] and\
           lower[1] <= y[1] <= upper[1] and\
           lower[2] <= y[2] <= upper[2]:
            z_1 += 1
        if q_2 == 0:
            if q_1 == 20:
                tem_arr.append(z_1)
                q_1 = 0
                z_1 = 0
                l_1 += 1
        else:
            if q_1 == 20:
                tem_arr[l_1] += z_1
                q_1 = 0
                z_1 = 0
                l_1 += 1
        q_1 += 1
    q_2 +=1
    if q_2 == 20:
        res_arr.append(tem_arr)
        tem_arr = []
        q_2 = 0

for o in res_arr:
    print o

    # find the colors within the specified boundaries and apply
    # the mask
    # mask = cv2.inRange(image, lower, upper)
    # output = cv2.bitwise_and(image, image, mask=mask)

    # show the images
    # cv2.imshow("images", np.hstack([image, output]))
    # cv2.waitKey(0)