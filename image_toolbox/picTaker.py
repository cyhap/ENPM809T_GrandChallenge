# Take a Picture with Py Cam and Use the Mask bounds to identify
# an object. Return the centroid of the corresponding object if
# one exists. Otherwise return []
import picamera
import picamera.array
import time
import cv2

class camera:
	def __init__(self):
		self.cam = picamera.PiCamera()
		self.cam.resolution = (640, 480)
		self.cam.start_preview()
		time.sleep(2)
		
	def getIm(self):
		with picamera.array.PiRGBArray(self.cam) as stream:
			self.cam.capture(stream, format = "bgr")
			return stream.array
	def centroidAndArea(self, maskBounds):
		orig_im = self.getIm()
		hsv_im = cv2.cvtColor(orig_im, cv2.COLOR_BGR2HSV)

		# Apply Mask to the Image. Identify 1 Object
		minHsv = maskBounds[0]
		maxHsv = maskBounds[1]
		mask = cv2.inRange(hsv_im, minHsv, maxHsv)
		kernelSize = 5
		mask = cv2.blur(mask, (kernelSize,kernelSize))
		masked = cv2.bitwise_and(orig_im, orig_im, mask=mask)
		#cv2.imshow("Mask", mask)
		#cv2.waitKey(0)
		
		newIm, contours, h = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		
		cnters = []
		areas = []
		for conts in contours:
			M = cv2.moments(conts)
			if (M["m00"] > 150):
				cx = int(M["m10"]/M["m00"])
				cy = int(M["m01"]/M["m00"])
				cnters.append((cx, cy))
				areas.append((M["m00"]))
			
		return (cnters, areas)
		
		
	def __del__(self):
		self.cam.close()
		print("Camera Properly Closed.")
