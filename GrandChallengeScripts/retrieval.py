# Grand Challenge Master Script (No Obstacles Iteration)
sys.path.insert(0, '/home/pi/enpm809T/gripper_toolbox/')
sys.path.insert(0, '/home/pi/enpm809T/motorControl_toolbox/')
sys.path.insert(0, '/home/pi/enpm809T/sodar_toolbox/')
sys.path.insert(0, '/home/pi/enpm809T/image_toolbox/')
import picTaker
import gripper as grip
import motorControl as motors
import sodarMeasure as sodar
from pickUpBlock import findAndPickUpBlock

import math

def convertIn2Meters(distIn):
	return 0.0254*distIn
	
# Starting at 1ft by 1 ft
oneFt = convertIn2Meters(12)
startingPos = (oneFt, oneFt)
startingOrient = 90 #Deg

#Drop Off Zone Center at 2ft * 10ft
dropOffPos =  (2*oneFt, 10*oneFt)

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
maskBoundsRGB.append((minHSV, maxHSV))

myPicTaker = picTaker.camera()

#Explore Algorithm

#TODO
blockHeld = findAndPickUpBlock()

#FIXME move into a Function
# Returns the block to drop off zone in the event of no obstacles
if (blockHeld):
	#Compute the Angle to the Drop off point
	xDif = myMotor.pos[0] - dropOffPos[0]
	yDif = myMotor.pos[1] - dropOffPos[1]
	desiredOrient = math.degrees(math.atan2(yDif, xDif))
	# Determine if which direction is better to pivot towards
	currOrient = myMotor.orient % 360
	pRight = abs(currOrient - desiredOrient)
	pLeft = abs(currOrient+360 - desiredOrient)
	if pRight <= pLeft:
		myMotor.pivotRightAng(pRight, 75)
	else:
		myMotor.pivotLeftAng(pLeft, 75)
	myMotor.forward((xDif**2 + yDif**2)**0.5)
	myGrip.open()
	myMotor.reverse(convertIn2Meters(7), 45)
	# Now go back to exploring
