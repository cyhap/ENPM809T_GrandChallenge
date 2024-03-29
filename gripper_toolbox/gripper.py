import RPi.GPIO as gpio
import time
#For tracing segmentation faults
import faulthandler; faulthandler.enable()

class gripper:
	def __init__(self, OUTPUT_PIN=36):
		self.OUTPUT_PIN = OUTPUT_PIN
		self.changedVal = False
		# These Positions are Duty Cycle Percentages
		self.gripperMaxPos = 10
		self.gripperMinPos = 6
		self.init()
	
	def init(self):
		gpio.setmode(gpio.BOARD)
		gpio.setup(self.OUTPUT_PIN, gpio.OUT)
		self.pwm = gpio.PWM(self.OUTPUT_PIN,  50) #50 Hz
		self.currVal = 0
		

	def checkBounds(self, aPos):
		if (aPos > self.gripperMaxPos or  aPos < self.gripperMinPos):
			aPos = (self.gripperMaxPos+self.gripperMinPos)/2 
			# FIXME Determine what this values should be set to
			print("Value Provided Exceeds Bounds. Setting to safe Value: " + str(aPos))

		return aPos

	def move2Pos(self, aPos):
		#print("In move2Pos")
		if not (self.currVal == aPos):
			if not self.changedVal:
				aPos = self.checkBounds(aPos)
				self.pwm.start(aPos)
				self.changedVal = True
			else:
				aPos = self.checkBounds(aPos)
				self.pwm.ChangeDutyCycle(aPos)
			self.currVal = aPos
				
			time.sleep(2)
		"""
		self.init()
		aPos = self.checkBounds(aPos)
		self.pwm.start(aPos)
		#time.sleep(2)
		self.cleanup()
		#time.sleep(2)
		"""
	def openGrip(self):
		self.move2Pos(self.gripperMaxPos)
		#time.sleep(2)
		
	def closeGrip(self):
		self.move2Pos(self.gripperMinPos)
		#time.sleep(2)
		
	def cleanup(self):
		self.pwm.stop()
		gpio.cleanup()
		
	def __del__(self):
		self.pwm.stop()
		gpio.cleanup()
		print("Gripper Pins Cleaned Up Properly")

if __name__ ==  "__main__":
	myGrip = gripper()
	myGrip.init()
	key = "z"
	while not key=="p":
		key = input("Please input control Time: ")
		try:
			key = float(key)
			myGrip.move2Pos(key)
			time.sleep(1)
		except ValueError:
			if not key=="p":
				print("This is not a number.")

