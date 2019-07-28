import motorControl

myMotor = motorControl.motorControl()
"""
for i in range(0,4):
	myMotor.forward(.45, 35)
	myMotor.pivotLeftAng(90, 75)
"""
"""
myMotor.pivotLeftAng(90, 75)
myMotor.reverse(.3, 35)
myMotor.pivotRightAng(225, 75)
myMotor.forward(.3, 35)
"""
def convertIn2Meters(distIn):
	return 0.0254*distIn
	
myMotor.forward(convertIn2Meters(8), 35)
myMotor.pivotRightAng(40, 75)
myMotor.reverse(convertIn2Meters(4), 35)
myMotor.pivotLeftAng(90, 75)
myMotor.forward(convertIn2Meters(4), 35)
