import numpy as np
import cv2
import imutils
import math

from picamera.array import PiRGBArray
from picamera import PiCamera
# Initialize the RPi Cam
camera = PiCamera()
camera.resolution = (640, 480)
camera.start_preview()

camera.capture("scriptIm.jpg")
orig_image = cv2.imread("scriptIm.jpg")
input(type(orig_image))
orig_image = imutils.resize(orig_image, width=400)
"""
# Draw a circle around the region of interest.
red = (0,0,255)
image = orig_image.copy()
ROI = (120, 170)
circleSize = 7
cv2.circle(image, ROI, circleSize, red, 1)
cv2.imshow("Orig w/ ROI", image)
#cv2.waitKey(0)
"""
circleSize = 7
#Convert image to HSV
hsvImage = cv2.cvtColor(orig_image, cv2.COLOR_BGR2HSV)
#print(hsvImage.shape)

# 3 Sigma is 98 % of a gaussian distribution	

minH = 50 #max(0,(avgH - hBuff))
minS = 50 #max(0,(avgS - sBuff))
minV = 140 #max(0,(avgV - vBuff))
maxH = 125 #min(255,(avgH + hBuff))
maxS = 225 #min(255,(avgS + sBuff))
maxV = 190 #min(255,(avgV + vBuff))
# May potentially allow for V to be 0 - 255 so that 
# light has nothing to do with the mask.
minHsv = np.array([minH, minS, minV])
maxHsv = np.array([maxH, maxS, maxV])
print(minHsv)
print(maxHsv)
mask = cv2.inRange(hsvImage, minHsv, maxHsv)
masked = cv2.bitwise_and(orig_image, orig_image, mask=mask)
"""
print(orig_image.shape)
print(hsvImage.shape)
print(mask.shape)
print(masked.shape)
"""
results = np.hstack([orig_image, hsvImage, masked])
cv2.imshow("Results", results)

cv2.waitKey(0)
cv2.imwrite("Part1_Results.jpg", results)
