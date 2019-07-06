import cv2
import time
from picamera.array import PiRGBArray
from picamera import PiCamera

def makeVideo(aFcn, vidLenSec):
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
	myTime = vidLenSec
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
		im_mod = aFcn(im)
		cv2.imshow("Modified Image", im_mod)
		key = cv2.waitKey(1) & 0xFF
		
		# Clear the stream in preparation for the next frame
		rawCapture.truncate(0)
		
		# Actually write the image to a file
		out.write(im_mod)
		
		myEnd= time.time()
		timeElapsed = myEnd-start
		f.write(str(timeElapsed)+str("\n"))
		print(timeElapsed)
		# Press 'q' to Stop recording video
		if key == ord("q") or maxFrames < frameCount:
			break

def makeVideo2(aFcn, vidLenSec):
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
	myTime = vidLenSec
	maxFrames = myTime*camera.framerate
	frameCount = 0
	# Loop
	for frame in range(int(maxFrames)):
		start = time.time()
		frameCount += 1
		# Grab Current Frame
		camera.capture("lastIm.jpg")
		im = cv2.imread("lastIm.jpg")
		
		#im = imutils.resize(im, width=400)
		# Show the modified frame to our screen
		im_mod = aFcn(im)
		cv2.imshow("Modified Image", im_mod)
		key = cv2.waitKey(1) & 0xFF
		
		# Clear the stream in preparation for the next frame
		rawCapture.truncate(0)
		
		# Actually write the image to a file
		out.write(im_mod)
		
		myEnd= time.time()
		timeElapsed = myEnd-start
		f.write(str(timeElapsed)+str("\n"))
		print(timeElapsed)
		# Press 'q' to Stop recording video
		if key == ord("q") or maxFrames < frameCount:
			break
