import numpy as np
import cv2
import imutils
import math

from picamera.array import PiRGBArray
from picamera import PiCamera
# Initialize the RPi Cam
camera = PiCamera()
camera.resolution = (640, 480)

camera.capture("scriptIm.jpg")
orig_image = cv2.imread("scriptIm.jpg")
orig_image = imutils.resize(orig_image, width=400)
red = (0,0,255)
blue = (255, 0, 0)
"""
# Draw a circle around the region of interest.
image = orig_image.copy()
ROI = (235, 230)
circleSize = 7
cv2.circle(image, ROI, circleSize, red, 1)
#cv2.imshow("Orig w/ ROI", image)

# Use the ROI to obtain min and max values
allHs = []
allSs = []
allVs = []
shift = circleSize//2
for i in np.arange(0,circleSize):
	for j in np.arange(0,circleSize):
		myX = ROI[0] + i - shift
		myY = ROI[1] + j - shift
		(currH, currS, currV) = hsvImage[myX][myY]
		allHs.append(currH)
		allSs.append(currS)
		allVs.append(currV)

# 3 Sigma is 98 % of a gaussian distribution	
hBuff = np.std(allHs)*3
sBuff = np.std(allSs)*3
vBuff = np.std(allVs)*3
avgH = np.mean(allHs)
avgS = np.mean(allSs)
avgV = np.mean(allVs)
"""

#Convert image to HSV
hsvImage = cv2.cvtColor(orig_image, cv2.COLOR_BGR2HSV)

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
#print(minHsv)
#print(maxHsv)
mask = cv2.inRange(hsvImage, minHsv, maxHsv)
masked = cv2.bitwise_and(orig_image, orig_image, mask=mask)
"""
print(orig_image.shape)
print(hsvImage.shape)
print(mask.shape)
print(masked.shape)
"""
newIm, contours, h = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
orig_image = cv2.drawContours(orig_image, contours, -1, blue, 3)
imWCirc = orig_image.copy()
results = np.hstack([orig_image, hsvImage, masked])
cv2.imshow("Results", results)

print("Number of Contours found: "+str(len(contours)))
# Logic to figure out ROI given multiple contours found.
circs = []
for aCnt in contours:
	arcLen = cv2.arcLength(aCnt, True)
	output = cv2.approxPolyDP(aCnt, 0.04*arcLen, True)
	numVertices = len(cv2.approxPolyDP(aCnt, 0.04*arcLen, True))
	print("Number of vertices: " + str(numVertices))
	#input(output)
	#Grab the moments
	moments = cv2.moments(aCnt)
	#print(moments['m00'])
	if numVertices > 5 and moments['m00'] > 200:
		circs.append(aCnt)
		
print("Number Circles Found: "+str(len(circs)))
for aCirc in circs:
	ROI = aCirc

	(x, y), rad = cv2.minEnclosingCircle(ROI)
	center = (int(x), int(y))
	rad = int(rad)
	cv2.circle(imWCirc, center, rad, red, 2)
	cv2.circle(imWCirc, center, 2, blue, -1)
	#Compare center values
	"""
	moments = cv2.moments(ROI)
	cx = moments['m10']/moments['m00']
	cy = moments['m01']/moments['m00']
	print(center) # Center from moments
	print(cx, cy) # Center of the min enclosing circle
	"""
	#cv2.drawContours(imWCirc, contours, -1, red, 2)
cv2.imshow("Green Light Identified", imWCirc)
#else:
#	cv2.imshow("Green Light Unidentified", orig_image)
cv2.waitKey(0)

