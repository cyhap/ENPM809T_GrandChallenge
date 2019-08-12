import sys
sys.path.insert(0, '/home/pi/enpm809T/image_toolbox/')
import picTaker
import cv2
#For tracing segmentation faults
import faulthandler; faulthandler.enable()

maskBoundsRGB  = {}

#  Red Block HSV Mask
minH = 0#0 
minS = 142#158
minV = 71#92
maxH = 4#180
maxS = 255#216
maxV = 255#155
minHSV = (minH, minS, minV)
maxHSV = (maxH, maxS, maxV)
maskBoundsRGB['r'] = (minHSV, maxHSV)

#  Green Block HSV Mask
minH = 30#43 
minS = 100#23
minV = 50#27
maxH = 79#74
maxS = 255#243
maxV = 255#156
minHSV = (minH, minS, minV)
maxHSV = (maxH, maxS, maxV)
maskBoundsRGB['g'] = (minHSV, maxHSV)

#  Blue Block HSV Mask
minH = 95
minS = 154
minV = 35
maxH = 114
maxS = 229
maxV = 211
minHSV = (minH, minS, minV)
maxHSV = (maxH, maxS, maxV)
maskBoundsRGB['b'] = (minHSV, maxHSV)

maskBoundsRGB_orig = maskBoundsRGB

#print("These arre the mask Bounds2", maskBoundsRGB.keys())

myPicTaker = picTaker.camera()

maskBoundsRGB_orig

orig_im = myPicTaker.getIm()
cv2.imshow("Orig Im", orig_im)
cv2.waitKey(0)
for key, maskBounds in maskBoundsRGB.items():
	hsv_im = cv2.cvtColor(orig_im, cv2.COLOR_BGR2HSV)
		
	# Apply Mask to the Image. Identify 1 Object
	minHsv = maskBounds[0]
	maxHsv = maskBounds[1]
	mask = cv2.inRange(hsv_im, minHsv, maxHsv)
	kernelSize = 5
	mask = cv2.blur(mask, (kernelSize,kernelSize))
	masked = cv2.bitwise_and(orig_im, orig_im, mask=mask)
	cv2.imshow("Mask", masked)
	cv2.waitKey(0)
	#Plot a dot at object center
	#cv2.circle(orig_image, COI, 10, (255, 0, 0), -1)
	
	#cv2.imshow("Results", masked)
	#key  = cv2.waitKey(1) & 0xFF 	
ans = input("Save Image?")
if ans =='y':
	cv2.imwrite("evalMask.jpg", orig_im)
	print("Image Saved")
