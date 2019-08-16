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
import time
#For tracing segmentation faults
import faulthandler; faulthandler.enable()
import pickle

def computeDesOrient(currPos, desPos):
	xDif = desPos[0] - currPos[0]
	yDif = desPos[1] - currPos[1]
	#print("yDif: ", yDif, "XDif: ", xDif)
	desiredOrient = math.degrees(math.atan2(yDif, xDif))
	return desiredOrient
		
# Recover position and orientation
fn = "selectedMoves_20190813-200118.pkl"
trajData = pickle.load(open(fn, "rb"))
position, orientation = trajData[-1]
# Starting at 1ft by 1 ft
oneFt = retrieval.convertIn2Meters(12)
startingPos = position
startingOrient = orientation #Deg

#Drop Off Zone Center at 2ft * 10ft
#dropOffPos =  (1*oneFt, 3*oneFt)
dropOffPos =  (1*oneFt,10*oneFt)

#Initialize Components
myGrip = grip.gripper()

myMotor= motors.motorControl(initPosOrient
 = (startingPos[0], startingPos[1], startingOrient))
 
mySodar = sodar.sodar()

maskBoundsRGB  = {}
maskBoundsRGB_orig  = {}

#  Red Block HSV Mask
minH = 0#0 
minS = 142#158
minV = 71#92
maxH = 4#180
maxS = 255#216
maxV = 255#155
minHSV = (minH, minS, minV)
maxHSV = (maxH, maxS, maxV)
#maskBoundsRGB['r'] = (minHSV, maxHSV)
maskBoundsRGB_orig['r'] = (minHSV, maxHSV)

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
maskBoundsRGB_orig['g'] = (minHSV, maxHSV)

#  Blue Block HSV Mask
minH = 95
minS = 154
minV = 35
maxH = 114
maxS = 229
maxV = 211
minHSV = (minH, minS, minV)
maxHSV = (maxH, maxS, maxV)
#maskBoundsRGB['b'] = (minHSV, maxHSV)
maskBoundsRGB_orig['b'] = (minHSV, maxHSV)

#maskBoundsRGB_orig = maskBoundsRGB.copy()

#print("These arre the mask Bounds2", maskBoundsRGB.keys())

myPicTaker = picTaker.camera()

#Explore Algorithm
#corners = [[0,0], [12*oneFt, 0], [12*oneFt, 12*oneFt], [0, 12*oneFt]]
corners = [[12*oneFt, 0], [12*oneFt, 12*oneFt],[12*oneFt, 0], [0,0]]
cornerIdx = 1
blocksFound = {}
numBlocksFound = 0
for i in range(0,5):
	while maskBoundsRGB:
		#print("These are the mask Bounds", maskBoundsRGB.keys())
		# Check t see that its outside the construction zone
		# Check that is not pointed towards the
		
		# This is a check to see if it is in the drop off zone
		#(myMotor.pos[0] < dropOffPos[0]+2*oneFt and myMotor.pos[1] > dropOffPos[1]-2*oneFt):
		print("Looking towards this corner: ", corners[cornerIdx])
		#Look towards a corner
		#Compute angle to that corner
		desiredOrient = computeDesOrient(myMotor.pos, corners[cornerIdx])
		#retrieval.drive2Pos(myMotor, [6, 6])
		retrieval.turn2DesAngle(myMotor, desiredOrient)
		
		print("Searching")
		# At some point decide to execute find and pick up block
		retVal = findAndPickUpBlock(myGrip, myMotor, mySodar, myPicTaker, maskBoundsRGB, maxAttempts=10)
		blockHeld = retVal[0]
		color = retVal[1]
		#FIXME move into a Function
		# Returns the block to drop off zone in the event of no obstacles
		if (blockHeld and color):
			print("Block Found: ", color)
			retrieval.returnBlock2DropZone(myGrip, myMotor, dropOffPos)
			print("Block Returned to Drop Zone")
			numBlocksFound += 1
			# Remove Block that was found
			blocksFound[color] = maskBoundsRGB.pop(color)
			if (numBlocksFound > 4):
				print("Does this help? Sleeping for 5 Seconds")
				time.sleep(5)
		else:
			cornerIdx = (cornerIdx + 1) % len(corners)
		
	# Enforce the search for 1 Red Green or Blue before restarting
	maskBoundsRGB = maskBoundsRGB_orig.copy()
	print("Found one of each should try again.")
	#print("maskBoundsRGB contents: ", maskBoundsRGB)
	#print("maskBoundsRGB_orig contents: ", maskBoundsRGB_orig)
	#print("Sleeping for 3 Seconds to allow cleanup?")
	#time.sleep(3)
