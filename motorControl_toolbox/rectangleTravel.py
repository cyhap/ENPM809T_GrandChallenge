import motorControl

myMotor = motorControl.motorControl()
for i in range(0,4):
	myMotor.forward(.45, 35)
	myMotor.pivotLeftAng(90, 75)
#myMotor.pivotLeftAng(90, 75)

