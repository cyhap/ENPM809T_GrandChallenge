import RPi.GPIO as gpio

class gripper:
	# These Positions are Duty Cycle Percentages
	gripperMaxPos = 10
	gripperMinPos = 4 # FIXME Update with Actual Bounds
	def __init__(self, OUTPUT_PIN=36):
		self.OUTPUT_PIN = OUTPUT_PIN
		self.changedVal = False
	def init(self):
		gpio.setmode(gpio.BOARD)
		gpio.setup(self.OUTPUT_PIN, gpio.OUT)
		self.pwm = gpio.PWM(self.OUTPUT_PIN,  50) #50 Hz

	def checkBounds(self, aPos):
		if (aPos > gripperMaxPos or  aPos < gripperMinPos):
			aPos = (gripperMaxPos+gripperMinPos)/2 # FIXME Determine what this values should be set to
			print("Value Provided Exceeds Bounds. Setting to safe Value")

		return aPos

	def move2Pos(self, aPos):
		if not self.changedVal:
			aPos = self.checkBounds(aPos)
			self.pwm.start(aPos)
			self.changedVal = True
		else:
			self.pwm.ChangeDutyCycle(aPos)

	def __del__(self):
		self.pwm.stop()
		gpio.cleanup()
		print("Gripper Pins Cleaned Up Properly")

if __name__ ==  "__main__":
	myGrip = gripper()
	myGrip.init()
	key = "z"
	while not key=="p":
		key = input("Please input control Time")
		#try:
		key = int(key)
		myGrip.move2Pos(key)
			#time.sleep(1)
		#except:
		#	print("This is not a number.")

