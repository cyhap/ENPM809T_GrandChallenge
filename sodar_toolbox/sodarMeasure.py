import RPi.GPIO as gpio
import time

def getMean(aList):
	return float(sum(aList)/len(aList))

class sodar:
	def __init__(self, trigPin=16, echoPin=18):
		self.trigPin = trigPin
		self.echoPin = echoPin
		gpio.setmode(gpio.BOARD)
		gpio.setup(trigPin, gpio.OUT)
		gpio.setup(echoPin, gpio.IN)
		print("Sodar Created.")
		
	def __del__(self):
		# Clearnup gpio pins and return distance estimate
		gpio.cleanup()
		print("Pins properly reset. Sodar Destroyed")
	
	# Returns distance in cm
	# Use the average over the number of trials
	def distance(self, numTrials = 1):
		allDistances = []
		for i in range(numTrials):
			#Ensure the pin is low
			gpio.output(self.trigPin, False)
			time.sleep(0.1)

			#Generate trigger (or active) pulse
			gpio.output(self.trigPin, True)
			time.sleep(0.00001)
			gpio.output(self.trigPin, False)

			#Wait for Generate echo time signal
			while gpio.input(self.echoPin) ==  False:
				pulse_start = time.time()
			while gpio.input(self.echoPin) == True:
				pulse_end = time.time()

			# Why do we want the pulse duration for?
			pulse_duration = pulse_end-pulse_start

			# Convert time to distance
			distance = pulse_duration*17150
			allDistances.append(round(distance, 2))
		retDistance = getMean(allDistances)
		return retDistance
	
if __name__ ==  "__main__" :
	# Define Trigger and Echo Pin Numbers
	trig = 16
	echo = 18
	mySodar = sodar(trig, echo)
	while (True):
		print("Distance:", mySodar.distance(), "cm")
