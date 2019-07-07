# HW 6 Gripper Time Lapse Video
import time
import os
import sys
import cv2
import glob
sys.path.insert(0, '/home/pi/enpm809T/gripper_toolbox/')
sys.path.insert(0, '/home/pi/enpm809T/teleop_toolbox/')
sys.path.insert(0, '/home/pi/enpm809T/sodar_toolbox/')
import gripper as grip
import teleop as tele
import sodarMeasure as sodar

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

myTeleOp = tele.teleop()

mySodar = sodar.sodar()

key = "z"
imNum = 0
currDirStr = os.getcwd()+"/"
while not key=="p":
	imNum += 1
	# Control the Gripper
	gripInp = input("Please input Duty Cycle Percentage: ")
	try:
		gripInp = float(gripInp)
		myGrip.move2Pos(gripInp)
		time.sleep(1)
	except ValueError:
		if not gripInp=="p":
			print("This is not a number.")
	# Control the Motors
	key = input("Select Driving Mode: ")
	if not key == "p":
		myTeleOp.key_input(key)
		
		# Get a Distance Measurement (Based off of 10 measurements)
		distance = mySodar.distance(10)
		
		image = "sudo raspistill -w 1280 -h 720 -hf -vf -o " + currDirStr + today + "/" + str(imNum) + ".jpg"
		os.system(image)
		print("Saved image: ", imNum)
		time.sleep(0.1)
		
		orig_im = cv2.imread(currDirStr + today + "/" + str(imNum) + ".jpg")
		
		dutyStr = "Duty: %0.1f %%" % gripInp
		font = cv2.FONT_HERSHEY_SIMPLEX
		cv2.putText(orig_im, dutyStr, (10, 40), font, 1, (255, 0, 0), 2, cv2.LINE_AA)
		
		distanceStr = "Distance: %0.3f cm " % distance
		font = cv2.FONT_HERSHEY_SIMPLEX
		cv2.putText(orig_im, distanceStr, (10, 80), font, 1, (255, 0, 0), 2, cv2.LINE_AA)
		
		out.write(orig_im)
	


