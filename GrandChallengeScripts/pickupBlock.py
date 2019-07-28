import os
import sys
import cv2
sys.path.insert(0, '/home/pi/enpm809T/image_toolbox/')
sys.path.insert(0, '/home/pi/enpm809T/email_toolbox/')
import email01
import picTaker
import time
# Routine to Use the Camera to Find the Block and Pick it up

def findAndPickUpBlock(grip, motors, sodar, picTaker, maskBoundsRGB, maxAttempts = 25):
	
	# Max Allowable Distance
	maxDistAllowed_m = 8*0.0254 # 8  Inches
	# Start the read distance outside the max distance allowed
	distance_m  = maxDistAllowed_m+1
	while (distance_m > maxDistAllowed_m):
		success = centerOnBlock(maxAttempts, maskBoundsRGB, picTaker, motors)
		# Stop now if we were not able to find anything or center within
		# Max attempts
		if not success:
				print("Unsuccessful Centering on Block")
				return success
		# Measure the Distance to the Block
		# Get the Distance as an avg over 10 measurements
		distance_m = sodar.distance(10) / 100
		# Subtract dist for  the gripper
		distance_m = distance_m - 4*0.0254
		if (distance_m > maxDistAllowed_m):
			motors.forward(maxDistAllowed_m, 40)
		print("Distance_m: ", distance_m)
		print("Max Distance Allowed: ", maxDistAllowed_m)
		#input("Continue?")
	
	# Open the Gripper
	grip.openGrip()
	#time.sleep(1)
	# Go Forward The Previously Meausred Distance
	motors.forward(distance_m, 35) # Fixme Determine Duty Cycle
	# Close the Gripper.
	grip.closeGrip()
	
	email01.main(picTaker)
	return success
	
	# ENSURE THAT THE BLOCK IS IN OUT GRASP?!

	# End Routine
	
def centerOnBlock(maxAttempts, maskBoundsRGB, picTaker, motors):
	# Image is (640, 480) so Center is (320, 240)
	CenterIm = (320, 240)
	success = False
	#BEGIN LOOP
	for i in range(0, maxAttempts):
		# Take an image of the immediate surroundings and get the centroid
		largestArea = 0
		largestY = 0
		COI = []
		orig_im = picTaker.getIm()
		#Crop Image to remove the gripper
		#orig_im = orig_im[0:240, 0:640]
		for maskBounds in maskBoundsRGB:
			cntrs, areas = picTaker.centroidAndArea(maskBounds, orig_im)
			# Only Care about the largest (closest block)
			if len(areas) > 1:
				print("WARNING MORE THAN ONE DETECTED")
			if areas:
				method = 2
				if method == 1:
					maxIdx = areas.index(max(areas))
					if largestArea < areas[maxIdx]:
						COI = cntrs[maxIdx]
						largestArea  = areas[maxIdx]
				elif method == 2:
					for cntr in cntrs:
						#print(cntr[1])
						if largestY < cntr[1]:
							COI = cntr
							largestY = cntr[1]
					#input("Continue?")
			#input("Continue? ")
		if COI:
			# COI is the center we care about as it is the closest block.
			#Compute the angle needed to turn given the distance from center
			pixelDist = abs(COI[0] - CenterIm[0])
			# Rotate in Small increments until the block is centered in the image
			bufX = 5# Allow X Pixels of error
			# Block is to the Left of Center Screen
			# Use different turning amounts so it doesn't get stuck going back
			# and forth
			if COI[0] < CenterIm[0] - bufX:
				deg2Center = pixelDist*0.061
				motors.pivotLeftAng(deg2Center, 75) # Pivot X Degrees Using 75% DC
			elif COI[0] > CenterIm[0] + bufX:
				deg2Center = pixelDist*0.061
				motors.pivotRightAng(deg2Center, 75) # Pivot X Degrees Using 75% DC
			else:
				success = True
				break
	return success
	print("Center on Block: Success:" , success)
	
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
	maskBoundsRGB  = []
	#  Red Block HSV Mask
	minH = 0#0 
	minS = 70#158
	minV = 50#92
	maxH = 10#180
	maxS = 255#216
	maxV = 255#155
	minHSV = (minH, minS, minV)
	maxHSV = (maxH, maxS, maxV)
	maskBoundsRGB.append((minHSV, maxHSV))
	#  Green Block HSV Mask
	minH = 30#43 
	minS = 100#23
	minV = 50#27
	maxH = 90#74
	maxS = 255#243
	maxV = 255#156
	minHSV = (minH, minS, minV)
	maxHSV = (maxH, maxS, maxV)
	maskBoundsRGB.append((minHSV, maxHSV))
	#  Blue Block HSV Mask
	minH = 107 
	minS = 132
	minV = 61
	maxH = 121
	maxS = 234
	maxV = 120
	minHSV = (minH, minS, minV)
	maxHSV = (maxH, maxS, maxV)
	#maskBoundsRGB.append((minHSV, maxHSV))
	
	myPicTaker = picTaker.camera()
	findAndPickUpBlock(myGrip, myMotor, mySodar, myPicTaker, maskBoundsRGB, maxAttempts=25)

	#  Black Block HSV Mask
	minH = 0 
	minS = 0
	minV = 0
	maxH = 208
	maxS = 83
	maxV = 113
	minHSV = (minH, minS, minV)
	maxHSV = (maxH, maxS, maxV)
	maskBoundsRGB.append((minHSV, maxHSV))
