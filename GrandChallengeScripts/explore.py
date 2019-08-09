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
import retrieval
import math
#For tracing segmentation faults
import faulthandler; faulthandler.enable()

# Starting at 1ft by 1 ft
oneFt = retrieval.convertIn2Meters(12)
startingPos = (oneFt, oneFt)
startingOrient = 0 #Deg

#Drop Off Zone Center at 2ft * 10ft
dropOffPos =  (1*oneFt, 3*oneFt)
#dropOffPos =  (1*oneFt,10*oneFt)

#Initialize Components
myGrip = grip.gripper()

myMotor= motors.motorControl(initPosOrient
 = (startingPos[0], startingPos[1], startingOrient))
 
mySodar = sodar.sodar()

maskBoundsRGB  = {}

#  Red Block HSV Mask
minH = 0#0 
minS = 70#158
minV = 50#92
maxH = 10#180
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
inS = 147
minV = 97
maxH = 147
maxS = 255
maxV = 255
minHSV = (minH, minS, minV)
maxHSV = (maxH, maxS, maxV)
maskBoundsRGB['b'] = (minHSV, maxHSV)

maskBoundsRGB_orig = maskBoundsRGB

#print("These arre the mask Bounds2", maskBoundsRGB.keys())

myPicTaker = picTaker.camera()

#Explore Algorithm
#TODO
blocksFound = {}
for i in range(0,3):
	while maskBoundsRGB:
		#print("These are the mask Bounds", maskBoundsRGB.keys())
		# Check t see that its outside the construction zone
		# Check that is not pointed towards the
		
		# This is a check to see if it is in the drop off zone
		#(myMotor.pos[0] < dropOffPos[0]+2*oneFt and myMotor.pos[1] > dropOffPos[1]-2*oneFt):
		print("Looking towards the Center!")
		#Look towards the center
		#Compute angle to center
		centerArea = [6*oneFt, 6*oneFt]
		xDif = centerArea[0] - myMotor.pos[0]
		yDif = centerArea[1] - myMotor.pos[1]
		#print("Current X Pos: ", myMotor.pos[0])
		#print("Current Y Pos: ", myMotor.pos[1])
		#print("Drop off X Pos: ", centerArea[0])
		#print("Drop off Y Pos: ", centerArea[1])
		#print("yDif: ", yDif, "XDif: ", xDif)
		desiredOrient = math.degrees(math.atan2(yDif, xDif))
		
		#retrieval.drive2Pos(myMotor, [6, 6])
		retrieval.turn2DesAngle(myMotor, desiredOrient)
		
		print("Searching")
		# At some point decide to execute find and pick up block
		retVal = findAndPickUpBlock(myGrip, myMotor, mySodar, myPicTaker, maskBoundsRGB, maxAttempts=15)
		blockHeld = retVal[0]
		color = retVal[1]
		#FIXME move into a Function
		# Returns the block to drop off zone in the event of no obstacles
		if (blockHeld and color):
			print("Block Found: ", color)
			retrieval.returnBlock2DropZone(myGrip, myMotor, dropOffPos)
			print("Block Returned to Drop Zone")
			# Remove Block that was found
			#blocksFound[color] = maskBoundsRGB.pop(color)
		
	# Enforce the search for 1 Red Green or Blue before restarting
	maskBoundsRGB = maskBoundsRGB_orig.copy()
