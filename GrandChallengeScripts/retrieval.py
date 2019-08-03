# Grand Challenge Master Script (No Obstacles Iteration)
import math
import time

def convertIn2Meters(distIn):
	return 0.0254*distIn

def drive2Pos(myMotor, dropOffPos):
	#Compute the Angle to the Drop off point
	xDif = dropOffPos[0] - myMotor.pos[0]
	yDif = dropOffPos[1] - myMotor.pos[1]
	print("Current X Pos: ", myMotor.pos[0])
	print("Current Y Pos: ", myMotor.pos[1])
	print("Drop off X Pos: ", dropOffPos[0])
	print("Drop off Y Pos: ", dropOffPos[1])
	print("yDif: ", yDif, "XDif: ", xDif)
	desiredOrient = math.degrees(math.atan2(yDif, xDif))
	# Determine if which direction is better to pivot towards
	currOrient = myMotor.orient %360
	print("Current Orient: ", currOrient)
	print("Desired Orient: ", desiredOrient)
	
	turnAng = currOrient - desiredOrient
	print("Turn Angle before check: ", turnAng)
	if abs(turnAng) > 180:
		residAng = turnAng - 180
		turnAng = -1*(turnAng - 2*residAng)
	print("Turn Angle after check: ", turnAng)
	if turnAng > 0:
		myMotor.pivotRightAng(abs(turnAng), 75)
	elif turnAng < 0:
		myMotor.pivotLeftAng(abs(turnAng), 75)
		
	# Go to drop zone
	myMotor.forward((xDif**2 + yDif**2)**0.5, 40)
		
def returnBlock2DropZone(myGrip, myMotor, dropOffPos):
	
	drive2Pos(myMotor, dropOffPos)
	# Release Block and back away
	myGrip.openGrip()
	myMotor.reverse(convertIn2Meters(7), 35)
	time.sleep(1)
	myGrip.closeGrip()
	# Now go back to exploring

if __name__ ==  "__main__":
	import sys
	sys.path.insert(0, '/home/pi/enpm809T/gripper_toolbox/')
	sys.path.insert(0, '/home/pi/enpm809T/motorControl_toolbox/')
	sys.path.insert(0, '/home/pi/enpm809T/sodar_toolbox/')
	sys.path.insert(0, '/home/pi/enpm809T/image_toolbox/')
	#sys.path.insert(0, '/home/pi/enpm809T/GrandChallengeScripts/')
	import picTaker
	import gripper as grip
	import motorControl as motors
	import sodarMeasure as sodar
	from pickupBlock import findAndPickUpBlock	
	# Starting at 1ft by 1 ft
	oneFt = convertIn2Meters(12)
	startingPos = (oneFt, oneFt)
	startingOrient = 0 #Deg

	#Drop Off Zone Center at 2ft * 10ft
	dropOffPos =  (oneFt, oneFt)
	#dropOffPos =  (2*oneFt,10*oneFt)
	
	#Initialize Components
	myGrip = grip.gripper()

	myMotor= motors.motorControl(initPosOrient
	 = (startingPos[0], startingPos[1], startingOrient))
	 
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
	maxH = 79074
	maxS = 255#243
	maxV = 255#156
	minHSV = (minH, minS, minV)
	maxHSV = (maxH, maxS, maxV)
	maskBoundsRGB.append((minHSV, maxHSV))

	#  Blue Block HSV Mask
	minH = 78 
	minS = 147
	minV = 97
	maxH = 147
	maxS = 255
	maxV = 255
	minHSV = (minH, minS, minV)
	maxHSV = (maxH, maxS, maxV)
	maskBoundsRGB.append((minHSV, maxHSV))

	myPicTaker = picTaker.camera()

	#Explore Algorithm
	#TODO

	# At some point decide to execute find and pick up block
	blockHeld = findAndPickUpBlock(myGrip, myMotor, mySodar, myPicTaker, maskBoundsRGB, maxAttempts=25)

	#FIXME move into a Function
	# Returns the block to drop off zone in the event of no obstacles
	if (blockHeld):
		returnBlock2DropZone(myGrip, myMotor, dropOffPos)
