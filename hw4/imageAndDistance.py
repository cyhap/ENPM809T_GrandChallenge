import sys
sys.path.insert(0, '/home/pi/enpm809T/sodar_toolbox/')
import sodarMeasure
import os
import cv2
import imutils

# Take a picture
os.system('raspistill -o stillIm.jpg')

orig_im = cv2.imread('stillIm.jpg')
orig_im = imutils.resize(orig_im, width=400)

trig = 16
echo = 18
mySodar = sodarMeasure.sodar(trig, echo)
distance = mySodar.distance(numTrials = 10)

distanceStr = "Distance: %0.3f cm" % distance
font = cv2.FONT_HERSHEY_SIMPLEX
cv2.putText(orig_im, distanceStr, (10, 40), font, 1, (255, 0, 0), 2, cv2.LINE_AA)


cv2.imshow("Still Image", orig_im)
cv2.waitKey(0)

cv2.imwrite("Pi_Distance.jpg", orig_im)
print("Image Successfully Saved")	
