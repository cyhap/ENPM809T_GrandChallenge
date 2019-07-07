# HW 6 Gripper Time Lapse Video
import time
import os
import sys
import cv2
import glob
sys.path.insert(0, '/home/pi/enpm809T/gripper_toolbox/')
import gripper as grip

# create a unique folder to store images in
today = time.strftime("%Y%m%d-%H%M%S")
print(today)
os.system("sudo mkdir " + today)

# define the codec and create VideoWriter object
fps_out = 1
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(today + ".avi", fourcc, fps_out, (1280, 720))

myGrip = grip.gripper()
myGrip.init()
currDirStr = os.getcwd()+"/"
for i in range(3,10):
	myGrip.move2Pos(i)
		
	image = "sudo raspistill -w 1280 -h 720 -hf -vf -o " + currDirStr + today + "/" + str(i) + ".jpg"
	os.system(image)
	print("Saved image: ", i)
	time.sleep(0.1)
	
	image_out = cv2.imread(currDirStr + today + "/" + str(i) + ".jpg")
	
	dutyStr = "Duty: %0.1f %%" % i
	font = cv2.FONT_HERSHEY_SIMPLEX
	cv2.putText(image_out, dutyStr, (10, 40), font, 1, (255, 0, 0), 2, cv2.LINE_AA)
	#cv2.imshow("P", image_out)
	#cv2.waitKey(0)
	out.write(image_out)
	
print("Video: " + today + ".avi is now ready for viewing!")

