import os
import sys
import cv2
sys.path.insert(0, '/home/pi/enpm809T/image_toolbox/')
import picTaker
import time
# Routine to Use the Camera to Find the Block and Pick it up

def findAndPickUpBlock(grip, motors, sodar, picTaker, maskBoundsRGB):
	# Image is (640, 480) so Center is (320, 240)
	CenterIm = (320, 240)
	success = False
	maxAttempts = 50
	#BEGIN LOOP
	for i in range(0, maxAttempts):
		# Take an image of the immediate surroundings and get the centroid
		largestArea = 0
		for maskBounds in maskBoundsRGB:
			cntrs, areas = picTaker.centroidAndArea(maskBounds)
			# Only Care about the largest (closest block)
			if len(areas) > 1:
				print("WARNING MORE THAN ONE DETECTED")
			maxIdx = areas.index(max(areas))
			if largestArea < areas[maxIdx]:
				COI = cntrs[maxIdx]
				largestArea  = areas[maxIdx]
		# COI is the center we care about as it is the closest block.
		
		# Rotate in Small increments until the block is centered in the image
		bufX = 5# Allow X Pixels of error
		# Block is to the Left of Center Screen
		# Use different turning amounts so it doesn't get stuck going back
		# and forth
		if COI[0] < CenterIm[0] - bufX:
			motors.pivotRightAng(3, 75) # Pivot X Degrees Using 75% DC
		elif COI[0] > CenterIm[0] + bufX:
			motors.pivotLeftAng(5, 75) # Pivot X Degrees Using 75% DC
		else:
			success = True
			break
		#END LOOP
	# Stop now if we were not able to find anything or center within
	# Max attempts
	if not success:
			return success
	
	# Measure the Distance to the Block
	# Get the Distance as an avg over 10 measurements
	distance_m = sodar.distance(10) / 100
	# Open the Gripper
	grip.openGrip()
	time.sleep(1)
	# Go Forward The Previously Meausred Distance
	motors.forward(distance_m, 40) # Fixme Determine Duty Cycle
	# Close the Gripper.
	grip.closeGrip()
	time.sleep(1)

	# ENSURE THAT THE BLOCK IS IN OUT GRASP?!

	# End Routine
	
if __name__ == "__main__":
	sys.path.insert(0, '/home/pi/enpm809T/gripper_toolbox/')
	sys.path.insert(0, '/home/pi/enpm809T/motorControl_toolbox/')
	sys.path.insert(0, '/home/pi/enpm809T/sodar_toolbox/')
	import gripper as grip
	import motorControl as motors
	import sodarMeasure as sodar
	myGrip = grip.gripper()
	myMotor= motors.motorControl()
	mySodar = sodar.sodar()
	# Note the test code is only for a red block
	minH = 0 
	minS = 135
	minV = 92
	maxH = 204
	maxS = 217
	maxV = 255
	minHSV = (minH, minS, minV)
	maxHSV = (maxH, maxS, maxV)
	maskBoundsRGB  = []
	maskBoundsRGB.append((minHSV, maxHSV))
	myPicTaker = picTaker.camera()
	findAndPickUpBlock(myGrip, myMotor, mySodar, myPicTaker, maskBoundsRGB)
