import numpy as np
import cv2
import imutils
import time

from picamera.array import PiRGBArray
from picamera import PiCamera

def findGreenCirc(orig_image):
	red = (0,0,255)
	blue = (255, 0, 0)
	#Convert image to HSV
	hsvImage = cv2.cvtColor(orig_image, cv2.COLOR_BGR2HSV)

	# May potentially allow for V to be 0 - 255 so that 
	# light has nothing to do with the mask.
	# Values from the test image dont work very well in the video
	# Additional Buffer
	minHsv = np.array([  50, 50, 140])
	maxHsv = np.array([ 125, 225, 190])
	#print(minHsv)
	#print(maxHsv)
	mask = cv2.inRange(hsvImage, minHsv, maxHsv)
	kernelSize = 5
	mask = cv2.blur(mask, (kernelSize,kernelSize))
	masked = cv2.bitwise_and(orig_image, orig_image, mask=mask)

	newIm, contours, h = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	imWCirc = orig_image.copy()
	#results = np.hstack([orig_image, hsvImage, masked])
	#cv2.imshow("Results", results)

#	print(len(contours))
	# Logic to figure out ROI given multiple contours found.
	circs = []
	for aCnt in contours:
		arcLen = cv2.arcLength(aCnt, True)
		numVertices = len(cv2.approxPolyDP(aCnt, 0.10*arcLen, True))
		#print(numVertices)
		#Grab the moments
		moments = cv2.moments(aCnt)
		#print(moments['m00'])
		if numVertices > 3 and moments['m00'] > 150:
			circs.append(aCnt)
			
	#print(len(circs))
	for aCirc in circs:
		ROI = aCirc

		(x, y), rad = cv2.minEnclosingCircle(ROI)
		center = (int(x), int(y))
		rad = int(rad)
		cv2.circle(imWCirc, center, rad, red, 2)
		cv2.circle(imWCirc, center, 2, blue, -1)
		
	return imWCirc


"""
#Debug code
orig_image = cv2.imread("trainingImage2.jpg")
orig_image = imutils.resize(orig_image, width=400)
findGreenCirc(orig_image)
"""

# Initialize the RPi Cam
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 10
rawCapture = PiRGBArray(camera, size=(640, 480))

# Allow camera warmup
time.sleep(0.1)

# Save video
# Create the components necessary to save.
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('circleTracking.avi', fourcc, camera.framerate, (640, 480))
f = open("timeData.txt", 'w')
#Video Length
myTime = 30 #Seconds
maxFrames = myTime*camera.framerate
frameCount = 0
# Loop
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=False):
	start = time.time()
	frameCount += 1
	# Grab Current Frame
	im = frame.array
	#im = imutils.resize(im, width=400)
	# Show the modified frame to our screen
	imWCirc = findGreenCirc(im)
	cv2.imshow("Green Light Identified", imWCirc)
	key = cv2.waitKey(1) & 0xFF
	
	# Clear the stream in preparation for the next frame
	rawCapture.truncate(0)
	
	# Actually write the image to a file
	out.write(imWCirc)
	
	myEnd= time.time()
	timeElapsed = myEnd-start
	f.write(str(timeElapsed)+str("\n"))
	print(timeElapsed)
	# Press 'q' to Stop recording video
	if key == ord("q") or maxFrames < frameCount:
		break

print("Done Saving Video... Bye")
