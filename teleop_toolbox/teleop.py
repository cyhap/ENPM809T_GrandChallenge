import RPi.GPIO as gpio
import time

class teleop:
	def __init__(self, IN_1=31, IN_2=33, IN_3=35, IN_4=37):
		self.IN_1 = IN_1
		self.IN_2 = IN_2
		self.IN_3 = IN_3
		self.IN_4 = IN_4
		
	def init(self):
		gpio.setmode(gpio.BOARD)
		gpio.setup(self.IN_1, gpio.OUT)
		gpio.setup(self.IN_2, gpio.OUT)
		gpio.setup(self.IN_3, gpio.OUT)
		gpio.setup(self.IN_4, gpio.OUT)
		
	def gameover(self):
		gpio.output(self.IN_1, False)
		gpio.output(self.IN_2, False)
		gpio.output(self.IN_3, False)
		gpio.output(self.IN_4, False)

	def forward(self, time_sec):
		self.init()
		#Left Wheels
		gpio.output(self.IN_1, True)
		gpio.output(self.IN_2, False)
		#Right Wheels
		gpio.output(self.IN_3, False)
		gpio.output(self.IN_4, True)		
		#Wait
		time.sleep(time_sec)
		#Set Low and Cleanup
		self.gameover()
		
	def reverse(self, time_sec):
		self.init()
		#Left Wheels
		gpio.output(self.IN_1, False)
		gpio.output(self.IN_2, True)
		#Right Wheels
		gpio.output(self.IN_3, True)
		gpio.output(self.IN_4, False)		
		#Wait
		time.sleep(time_sec)
		#Set Low and Cleanup
		self.gameover()

	def pivotLeft(self, time_sec):
		self.init()
		#Left Wheels
		gpio.output(self.IN_1, False)
		gpio.output(self.IN_2, True)
		#Right Wheels
		gpio.output(self.IN_3, False)
		gpio.output(self.IN_4, True)		
		#Wait
		time.sleep(time_sec)
		#Set Low and Cleanup
		self.gameover()
		
	def pivotRight(self, time_sec):
		self.init()
		#Left Wheels
		gpio.output(self.IN_1, True)
		gpio.output(self.IN_2, False)
		#Right Wheels
		gpio.output(self.IN_3, True)
		gpio.output(self.IN_4, False)		
		#Wait
		time.sleep(time_sec)
		#Set Low and Cleanup
		self.gameover()
		
	def key_input(self, event):
		self.init()
		print("Key: ", event)
		event = event.lower()
		time_sec = 0.25
		if event == "w":
			self.forward(time_sec)
		elif event == "a":
			self.pivotLeft(time_sec)
		elif event == "s":
			self.pivotRight(time_sec)
		elif event == "z":
			self.reverse(time_sec)
		else:
			print( "Invalid Key Pressed")
			
	def __del__(self):
		# Clearnup gpio pins
		gpio.cleanup()
		print("Pins properly reset. Teleop Controls Destroyed")
			
		
if __name__ == "__main__":
	myTele = teleop()
	while True:
		key = input("Select Driving Mode: ")
		if key == "p":
			break
		myTele.key_input(key)
