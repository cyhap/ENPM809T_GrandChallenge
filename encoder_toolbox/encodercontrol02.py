import RPi.GPIO as gpio
import time
import numpy as np

#Uses the Encoder Ticks for a Duration instead of Time
# TODO Add boolean to use encoder ticks instead of time!
class motorControl:
	def __init__(self, IN_1=31, IN_2=33, IN_3=35, IN_4=37, frontLeftEnc=7, backRightEnc=12):
		self.IN_1 = IN_1 #Left Wheels
		self.IN_2 = IN_2 #Left Wheels
		self.IN_3 = IN_3 #Right Wheels
		self.IN_4 = IN_4 #Right Wheels
		self.frontLeftEnc = frontLeftEnc
		self.backRightEnc = backRightEnc
		self.Mode = 1 #TODO Add Enumerations 0 is use time 1 is use Encoder Ticks
		
	def init(self):
		gpio.setmode(gpio.BOARD)
		gpio.setup(self.IN_1, gpio.OUT)
		gpio.setup(self.IN_2, gpio.OUT)
		gpio.setup(self.IN_3, gpio.OUT)
		gpio.setup(self.IN_4, gpio.OUT)
		gpio.setup(self.frontLeftEnc, gpio.IN, pull_up_down = gpio.PUD_UP)
		gpio.setup(self.backRightEnc, gpio.IN, pull_up_down = gpio.PUD_UP)

		
	def gameover(self):
		gpio.output(self.IN_1, False)
		gpio.output(self.IN_2, False)
		gpio.output(self.IN_3, False)
		gpio.output(self.IN_4, False)

	#FIXME UPDATE LATER
	def forward(self, time_sec, dutyCyclePcnt = 14):
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
	myMotor = motorControl()
	myMotor.init()
	
	counterFL = np.uint64(0)
	counterBR = np.uint64(0)
	
	buttonFL = int(0)
	buttonBR = int(0)
	
	#Initialize pwm signal to control motor
	pwm_R = gpio.PWM(myMotor.IN_4, 50)
	pwm_L = gpio.PWM(myMotor.IN_1, 50)
	val = 14
	pwm_R.start(val)
	pwm_L.start(val)
	time.sleep(0.1)
	
	f_BR = open("BR_Statees2.txt", 'w')
	f_FL = open("FL_Statees2.txt", 'w')

	for i in range(0,100000):
		print("Counter FL: ", counterFL, "GPIO State FL: ", gpio.input(7), "Counter BR: ", counterBR ,"GPIO State BR: ", gpio.input(12))
		
		f_BR.write(str(buttonBR)+str("\n"))
		f_FL.write(str(buttonFL)+str("\n"))

		if int(gpio.input(7)) != int(buttonFL):
			buttonFL = int(gpio.input(7))
			counterFL+=1

		if int(gpio.input(12)) != int(buttonBR):
			buttonBR = int(gpio.input(12))
			counterBR+=1
		
		if counterBR >= 960:
			myMotor.gameover()
			print("One Revolution Complete")
			break
