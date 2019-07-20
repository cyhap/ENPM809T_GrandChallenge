import RPi.GPIO as gpio
import numpy as np

#Initialize GPIO pins#
class encoder:
	def __init__(self):
		self.inputPin = 12
		
	def init(self):
		gpio.setmode(gpio.BOARD)
		gpio.setup(self.inputPin, gpio.IN, pull_up_down = gpio.PUD_UP)
		
	def gameover(self):
		gpio.cleanup()
	
#Main Code#
myEncoder = encoder()

myEncoder.init()

counter = np.uint64(0)
button = int(0)

while True:
	if int(gpio.input(myEncoder.inputPin)) != int(button):
		button = int(gpio.input(myEncoder.inputPin))
		counter+=1
		print(counter)
	
	if counter >= 960:
		myEncoder.gameover()
		print("One Revolution Complete")
		break
