import cv2
import numpy as np

#Port on camera
CAMPORT = 0

# Open camera device for capturing
camera = cv2.VideoCapture(CAMPORT);


def cap_image(name):
    
    file = "image/" + name + '.png'
    print("Taking picture")
    
    retval, im = camera.read()
    cv2.imwrite(file, im)
    
    print("Location: " + file)



def findLines(name):
    img = cv2.imread("image/" + name + '.png')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize = 3)

    minLineLength = 100
    maxLineGap = 10

    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength, maxLineGap)

    for x1,y1,x2,y2 in lines[0]:
        cv2.line(img, (x1, y1), (x2, y2), (0,255,0), 2)

    cv2.imwrite('image/' + name + 'Lines.png', img)






del(camera)
