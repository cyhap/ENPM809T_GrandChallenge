import numpy as np
import cv2
import imutils
import time
import sys
sys.path.insert(0, '/home/pi/enpm809T/image_toolbox/')
import calcArrowOrient as cao

from picamera.array import PiRGBArray
from picamera import PiCamera

	
def mapAngle2Direction(aAng_deg):
	retStr = "Unknown"
	if (aAng_deg <= 45  and aAng_deg > 315):
		retStr = "EAST"
	elif (aAng_deg > 45 and aAng_deg <= 135):
		retStr = "NORTH"
	elif (aAng_deg > 135 and aAng_deg <= 215):
		retStr = "WEST"
	elif (aAng_deg > 215 and aAng_deg <= 315):
		retStr = "SOUTH"
	return retStr


# Initialize the RPi Cam
camera = PiCamera()
camera.resolution = (640, 480)
camera.start_preview()

camera.capture("scriptIm.jpg")
orig_im = cv2.imread("scriptIm.jpg")

#orig_im = cv2.imread("trainingImg.jpg")
(h,w) = orig_im.shape[:2]
center = (w/2, h/2)
angle90 = -13.70
scale = 1.0
M = cv2.getRotationMatrix2D(center, angle90, scale)
orig_im = cv2.warpAffine(orig_im, M, (h,w))

orig_im = imutils.resize(orig_im, width=400)

hsv_im = cv2.cvtColor(orig_im, cv2.COLOR_BGR2HSV)

minHsv = np.array([  24, 108, 64])
maxHsv = np.array([ 80, 184, 255])

mask = cv2.inRange(hsv_im, minHsv, maxHsv)
kernelSize = 5
mask = cv2.blur(mask, (kernelSize,kernelSize))
masked = cv2.bitwise_and(orig_im, orig_im, mask=mask)
#cv2.imshow("Mask", mask)
#cv2.waitKey(0)

corners = cv2.goodFeaturesToTrack(mask, 5, 0.01, 10)

#May want the values before they are turned into ints
corners = np.int0(corners)

orientation = cao.calcArrowOrient(corners)

for aCrnr in corners:
	x,y = aCrnr.ravel()
	cv2.circle(orig_im, (x,y), 3, 255, -1)
	
orientStr = "Orientation: %0.3f deg (X right Y Up)" % orientation
font = cv2.FONT_HERSHEY_SIMPLEX
cv2.putText(orig_im, orientStr, (10, 40), font, 1, (255, 0, 0), 2, cv2.LINE_AA)

dirStr = mapAngle2Direction(orientation)
cv2.putText(orig_im, dirStr, (10, 80), font, 1, (255, 0, 0), 2, cv2.LINE_AA)

cv2.imshow("Corners", orig_im)
cv2.waitKey(0)
