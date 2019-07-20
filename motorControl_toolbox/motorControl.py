import RPi.GPIO as gpio
import time
import numpy as np
import math
import sys
sys.path.insert(0, '/home/pi/enpm809T/email_toolbox/')
import email01
import pickle

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
		self.wheelDiameter_m = 0.065
		self.distBetweenWheels_m = 0.24
		self.Mode = 1 #TODO Add Enumerations 0 is use time 1 is use Encoder Ticks
		self.PathCommands = []
		timeNow = time.strftime("%Y%m%d-%H%M%S")
		out_file = "selectedMoves_" + timeNow + ".pkl"
		self.fptr = open(out_file, "wb")
		
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
	def forward(self, control, dutyCyclePcnt):
		pins = [self.IN_4, self.IN_1] # Right Pin the Left Pin
		self.drive(pins, control, dutyCyclePcnt)
		self.PathCommands.append(("FWD", control))
		
	def reverse(self, control, dutyCyclePcnt):
		pins = [self.IN_3, self.IN_2]
		self.drive(pins, control, dutyCyclePcnt)
		self.PathCommands.append(("RVS", control))
		
	def pivotLeft(self, control, dutyCyclePcnt):
		pins = [self.IN_4, self.IN_2]
		self.drive(pins, control, dutyCyclePcnt)
		self.PathCommands.append(("P_Lft", control))
		
	def pivotRight(self, control, dutyCyclePcnt):
		pins = [self.IN_3, self.IN_1]
		self.drive(pins, control, dutyCyclePcnt)
		self.PathCommands.append(("P_Rgt", control))
		
	def pivotLeftAng(self, ang_deg, dutyCyclePcnt):
		self.Mode = 1
		circumference_m = self.distBetweenWheels_m*math.pi
		dist_m = circumference_m*ang_deg/360
		self.pivotLeft(dist_m, dutyCyclePcnt)
		self.PathCommands.append(("P_Lft_Ang", ang_deg))

		
	def pivotRightAng(self, ang_deg, dutyCyclePcnt):
		self.Mode = 1
		circumference_m = self.distBetweenWheels_m*math.pi
		dist_m = circumference_m*ang_deg/360
		self.pivotRight(dist_m, dutyCyclePcnt)
		self.PathCommands.append(("P_Rgt_Ang", ang_deg))

	
	def drive(self, pins, control, dutyCyclePcnt):
		if self.Mode == 0:
			self.moveMotorsTime(pins, control, dutyCyclePcnt)
		elif self.Mode == 1:
			self.moveMotorsDist(pins, control, dutyCyclePcnt)
		
	def moveMotorsDist(self, pins, distance_m, dutyCyclePcnt):
		
		numWheelRevs = distance_m/(self.wheelDiameter_m*np.pi)
		numTicks = int(np.ceil(numWheelRevs*960))
		self.init()
		
		counterFL = np.uint64(1)
		counterBR = np.uint64(1)
		lastUpdateBR = np.uint64(1)
		lastUpdateFL = np.uint64(1)
		
		buttonFL = int(0)
		buttonBR = int(0)

		dc_R = dutyCyclePcnt
		dc_L = dutyCyclePcnt
		
		saveStates = True
		if saveStates:
			statesFL = np.zeros((1000000, 1))
			statesBR = np.zeros((1000000, 1))
		
		#Initialize pwm signal to control motor
		pwm_R = gpio.PWM(pins[0], 50)
		pwm_L = gpio.PWM(pins[1], 50)
		pwm_R.start(dutyCyclePcnt)
		pwm_L.start(dutyCyclePcnt)
		time.sleep(0.01)
			
		# 1 Second will go through this loop ~4250 times
		lastTime = time.time()
		buff = 0
		gain = 750
		minCheckTime = 0.007
		for i in range(0,1000000):
			if saveStates:
				#print("Counter FL: ", counterFL, "GPIO State FL: ", gpio.input(self.frontLeftEnc), "Counter BR: ", counterBR ,"GPIO State BR: ", gpio.input(self.backRightEnc))
				statesFL[i] = buttonFL
				statesBR[i] = buttonBR
			
			stateChange = False
			if int(gpio.input(self.frontLeftEnc)) != int(buttonFL):
				buttonFL = int(gpio.input(self.frontLeftEnc))
				counterFL+=1
				stateChange = True

			if int(gpio.input(self.backRightEnc)) != int(buttonBR):
				buttonBR = int(gpio.input(self.backRightEnc))
				counterBR+=1
				stateChange = True

			#if stateChange:
			timeInterval = time.time() - lastTime
			if (timeInterval > minCheckTime):
				dBR_dt = (counterBR - lastUpdateBR) / timeInterval
				dFL_dt = (counterFL - lastUpdateFL) / timeInterval
				print("counterBR", counterBR)
				print("counterFL", counterFL)
				print("lastUpdateBR", lastUpdateBR)
				print("lastUpdateFL", lastUpdateFL)
				print("Time interval", timeInterval)
				lastUpdateBR = counterBR
				lastUpdateFL = counterFL
				lastTime = time.time()
				diffSpds = dFL_dt - dBR_dt
				print("DiffSpeeds: ", diffSpds)
				diffCnts = counterFL-counterBR
				#Positive means Left has gone faster than right
				#Negaitve Means Right has gone faster than left
				#0 Is ideal
				#"""
				#Method 3
				if (diffSpds > buff):
					gainR = 0
					gainL = -diffSpds/gain
				elif (diffSpds < -buff):
					gainR = diffSpds/gain
					gainL = 0
				else:
					#Scale the same speed up to desired ratio
					#Slower Motor will have a higher duty cycle
					if dc_R > dc_L:
						dc_L = dc_L*dutyCyclePcnt/dc_R
						dc_R = dutyCyclePcnt
					else:
						dc_R = dc_R*dutyCyclePcnt/dc_L
						dc_L = dutyCyclePcnt
					gainR = 0
					gainL = 0
					
				dc_R = min(dc_R + gainR, 100)
				dc_L = min(dc_L + gainL, 100)
				print("DC_L: ", dc_L)
				print("DC_R: ", dc_R)
				
			"""
			#print("Reduced rate: ", reducedRate)
			print("RatioR: ", ratioR)
			print("RatioL: ", ratioL)
			last_ratioR = ratioR
			last_ratioL = ratioL
			dc_R = min(dutyCyclePcnt*ratioR, 100)
			dc_L = min(dutyCyclePcnt*ratioL, 100)
			"""
			pwm_R.ChangeDutyCycle(dc_R)
			pwm_L.ChangeDutyCycle(dc_L)
			
			if (max(counterBR, counterFL) >= numTicks):
				breakIdx = i
				print("Break Idx: ", breakIdx)
				break
				
		pwm_R.stop()
		pwm_L.stop()
		self.gameover()
		print("Distance Covered: ", distance_m, "(m)")
		print("Corresponding Encoder Ticks: ", numTicks)
		if saveStates:
			statesBR = statesBR[:breakIdx]
			statesFL = statesFL[:breakIdx]
			np.save(file = "statesBR", arr = statesBR)
			np.save(file = "statesFL", arr = statesFL)
			
	def moveMotorsTime(self, pins, time_sec, dutyCyclePcnt):	
		self.init()
		
		#Initialize pwm signal to control motor
		pwm_R = gpio.PWM(pins[0], 50)
		pwm_L = gpio.PWM(pins[1], 50)
		pwm_R.start(dutyCyclePcnt)
		pwm_L.start(dutyCyclePcnt)
		time.sleep(time_sec)
				
		pwm_R.stop()
		pwm_L.stop()
		self.gameover()
		print("Time Traveled: ", time_sec, "(sec)")

					
	def __del__(self):
		# Clearnup gpio pins
		gpio.cleanup()
		#pickle.dump(self.PathCommands, self.fptr)
		self.fptr.close()
		
		print("Pins properly reset. Teleop Controls Destroyed")		
	
	def key_input(self, event):
		self.init()
		print("Key: ", event)
		event = event.lower()
		if event == "w":
			dutyCyclePercent = 35
			dist_m = float(input("Going forward. Please Input Desired Distance (m)"))
			self.forward(dist_m, dutyCyclePercent)
		elif event == "a":
			dutyCyclePercent = 75
			rotAng = float(input("Pivoting Left. Please Input Desired Angle (deg)"))
			self.pivotLeftAng(rotAng, dutyCyclePercent)
		elif event == "s":
			dutyCyclePercent = 75
			rotAng = float(input("Pivoting Right. Please Input Desired Angle (deg)"))
			self.pivotRightAng(rotAng, dutyCyclePercent)
		elif event == "z":
			dutyCyclePercent = 35
			dist_m = float(input("Going in Reverse. Please Input Desired Distance (m)"))
			self.reverse(dist_m, dutyCyclePercent)
		elif event == "pic":
			email01.main()
		else:
			print( "Invalid Key Pressed")


			
		
if __name__ == "__main__":
	myMotor = motorControl()
	"""
	dist_m = 0.9144
	#dist_m = 0.15
	dutyCyclePercent = 75
	startTime = time.time()
	#myMotor.forward(dist_m, dutyCyclePercent)
	#myMotor.reverse(dist_m, dutyCyclePercent)
	print("Elapsed Time: ", time.time()-startTime)
	rotAng = 90
	#myMotor.pivotLeftAng(rotAng, dutyCyclePercent)
	#myMotor.pivotRightAng(rotAng, dutyCyclePercent)
	"""
	key = 'l'
	while key != 'p':
		key = input("Input Control: \n")
		myMotor.key_input(key)
