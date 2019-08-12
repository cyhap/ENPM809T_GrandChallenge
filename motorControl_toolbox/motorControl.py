import RPi.GPIO as gpio
import time
import numpy as np
import math
import sys
sys.path.insert(0, '/home/pi/enpm809T/email_toolbox/')
sys.path.insert(0, '/home/pi/enpm809T/mpu_toolbox/')
sys.path.insert(0, '/home/pi/enpm809T/GrandChallengeScripts/')
from orientation import orientComp
from retrieval import convertIn2Meters
import email01
import pickle
import faulthandler; faulthandler.enable()

#Uses the Encoder Ticks for a Duration instead of Time
# TODO Add boolean to use encoder ticks instead of time!
class motorControl:
	def __init__(self, IN_1=31, IN_2=33, IN_3=35, IN_4=37, frontLeftEnc=7, backRightEnc=12, initPosOrient = (0,0,0)):
		self.IN_1 = IN_1 #Left Wheels
		self.IN_2 = IN_2 #Left Wheels
		self.IN_3 = IN_3 #Right Wheels
		self.IN_4 = IN_4 #Right Wheels
		self.frontLeftEnc = frontLeftEnc
		self.backRightEnc = backRightEnc
		self.wheelDiameter_m = 0.065
		self.distBetweenWheelsL_m = 0.242 #0.24 orig
		self.distBetweenWheelsR_m = 0.2453 #0.24 orig
		self.Mode = 1 #TODO Add Enumerations 0 is use time 1 is use Encoder Ticks
		self.PathCommands = []
		self.countsBR = []
		self.countsFL = []
		self.timeUpdates = []
		self.pos = [initPosOrient[0], initPosOrient[1]]
		self.orient = initPosOrient[2]
		self.actPos = [initPosOrient[0], initPosOrient[1]]
		self.actOrient = initPosOrient[2]
		self.mpu = orientComp(100)
		timeNow = time.strftime("%Y%m%d-%H%M%S")
		out_file = "selectedMoves_" + timeNow + ".pkl"
		self.fptr = open(out_file, "wb")
		self.minTurnAng = 2.5 # Deg
		self.init()
		
	def init(self):
		gpio.setmode(gpio.BOARD)
		gpio.setup(self.IN_1, gpio.OUT)
		gpio.setup(self.IN_2, gpio.OUT)
		gpio.setup(self.IN_3, gpio.OUT)
		gpio.setup(self.IN_4, gpio.OUT)
		gpio.setup(self.frontLeftEnc, gpio.IN, pull_up_down = gpio.PUD_UP)
		gpio.setup(self.backRightEnc, gpio.IN, pull_up_down = gpio.PUD_UP)

		
	def gameover(self):
		gpio.setmode(gpio.BOARD)
		gpio.output(self.IN_1, False)
		gpio.output(self.IN_2, False)
		gpio.output(self.IN_3, False)
		gpio.output(self.IN_4, False)
		#gpio.cleanup()

	#FIXME UPDATE LATER
	def forward(self, control, dutyCyclePcnt):
		pins = [self.IN_4, self.IN_1] # Right Pin the Left Pin
		self.turning = False
		self.drive(pins, control, dutyCyclePcnt, self.actOrient)
		#self.PathCommands.append(("FWD", control))
		self.pos[0] += math.cos(math.radians(self.orient))*control
		self.pos[1] += math.sin(math.radians(self.orient))*control
		self.PathCommands.append((self.pos.copy(), self.orient))
		#print("Current X Pos: ", self.pos[0])
		#print("Current Y Pos: ", self.pos[1])
		
	def reverse(self, control, dutyCyclePcnt):
		pins = [self.IN_3, self.IN_2]
		self.turning = False
		self.drive(pins, control, dutyCyclePcnt, self.actOrient)
		self.pos[0] -= math.cos(math.radians(self.orient))*control
		self.pos[1] -= math.sin(math.radians(self.orient))*control
		self.PathCommands.append((self.pos.copy(), self.orient))
		#print("Current X Pos: ", self.pos[0])
		#print("Current Y Pos: ", self.pos[1])
		
	def pivotLeft(self, control, dutyCyclePcnt, desiredAng = None):
		pins = [self.IN_4, self.IN_2]
		self.turning = True
		self.drive(pins, control, dutyCyclePcnt, desiredAng)
		#self.PathCommands.append(("P_Lft", control))
		
	def pivotRight(self, control, dutyCyclePcnt, desiredAng = None):
		pins = [self.IN_3, self.IN_1]
		self.turning = True
		self.drive(pins, control, dutyCyclePcnt, desiredAng)
		#self.PathCommands.append(("P_Rgt", control))
		
	def pivotLeftAng(self, ang_deg, dutyCyclePcnt):
		self.Mode = 1
		circumference_m = self.distBetweenWheelsL_m*math.pi
		dist_m = circumference_m*ang_deg/360
		desiredAng = self.actOrient+ang_deg
		self.pivotLeft(dist_m, dutyCyclePcnt, desiredAng)
		if ang_deg > self.minTurnAng:
			self.orient += ang_deg
		self.PathCommands.append((self.pos.copy(), self.orient))
		print("Current Orientation: ", self.orient)
		
	def pivotRightAng(self, ang_deg, dutyCyclePcnt):
		self.Mode = 1
		circumference_m = self.distBetweenWheelsR_m*math.pi
		dist_m = circumference_m*ang_deg/360
		desiredAng = self.actOrient+ang_deg
		self.pivotRight(dist_m, dutyCyclePcnt, desiredAng)
		#Ignoring small angles
		if ang_deg > self.minTurnAng:
			self.orient -= ang_deg
		self.PathCommands.append((self.pos.copy(), self.orient))
		print("Current Orientation: ", self.orient)
	
	def drive(self, pins, control, dutyCyclePcnt, desiredAng):
		#self.init()
		if self.Mode == 0:
			self.moveMotorsTime(pins, control, dutyCyclePcnt, desiredAng)
		elif self.Mode == 1:
			#print("pins: ", pins, "control: ", control, "dutyCyclePcnt: ", dutyCyclePcnt, "desiredAng: ", desiredAng)
			self.moveMotorsDist(pins, control, dutyCyclePcnt, desiredAng)
		#self.gameover()
		
	def moveMotorsDist(self, pins, distance_m, dutyCyclePcnt, desiredAng):
		#Added these to keep track of when different moves start
		self.countsBR.append(-1)
		self.countsFL.append(-1)
		self.timeUpdates.append(-1)
		
		if desiredAng is None:
			print("Error! No Desired Ang is not yet handled")
			return
		#FIXME ADD CODE FROM HERE FOR IMU SENSOR
		# Remove 2 Inches due to momentum
		print("Distance was: ", distance_m)
		if not self.turning:
			distance_m = max(distance_m - convertIn2Meters(2), 0.01)
		
		numWheelRevs = distance_m/(self.wheelDiameter_m*np.pi)
		numTicks = int(np.ceil(numWheelRevs*960))
		#self.init()
		
		counterFL = np.uint64(1)
		counterBR = np.uint64(1)
		lastUpdateBR = np.uint64(1)
		lastUpdateFL = np.uint64(1)
		
		buttonFL = int(0)
		buttonBR = int(0)

		dc_R = dutyCyclePcnt
		dc_L = dutyCyclePcnt
		orig_pcnt = dutyCyclePcnt
		
		saveStates = False
		if saveStates:
			statesFL = np.zeros((1000000, 1))
			statesBR = np.zeros((1000000, 1))
		
		#Initialize pwm signal to control motor
		time.sleep(.25)
		pwm_R = gpio.PWM(pins[0], 50)
		pwm_L = gpio.PWM(pins[1], 50)
		#Placed the start below
		#pwm_R.start(dutyCyclePcnt)
		#pwm_L.start(dutyCyclePcnt)
		#time.sleep(0.01)
			
		# 1 Second will go through this loop ~4250 times
		lastTime = time.time()
		buff = 0
		gain = 350#750
		minCheckTime = 0.007
		for i in range(0,1000000):
			if i == 0:
				pwm_R.start(dutyCyclePcnt)
				pwm_L.start(dutyCyclePcnt)
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
				"""
				print("counterBR", counterBR)
				print("counterFL", counterFL)
				print("lastUpdateBR", lastUpdateBR)
				print("lastUpdateFL", lastUpdateFL)
				print("Time interval", timeInterval)
				"""
				#self.countsBR.append(counterBR)
				#self.countsFL.append(counterFL)
				#self.timeUpdates.append(timeInterval)

				lastUpdateBR = counterBR
				lastUpdateFL = counterFL
				lastTime = time.time()
				diffSpds = dFL_dt - dBR_dt
				#print("DiffSpeeds: ", diffSpds)
				diffCnts = counterFL-counterBR
				#Positive means Left has gone faster than right
				#Negaitve Means Right has gone faster than left
				#0 Is ideal
				#"""
				"""
				# Slow down as we get close to the end
				avgCnt = (counterBR+counterFL)/2
				if (avgCnt/numTicks > .6):
					dc_L = dc_L*.1
					dc_R = dc_R*.1
				"""
					
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
				
				"""
				if (diffSpds > buff):
					gainR = 7
					gainL = -7
				elif (diffSpds < -buff):
					gainR = -7
					gainL = 7
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
				"""
					
				dc_R = max(min(dc_R + gainR, 100), 1)
				dc_L = max(min(dc_L + gainL, 100), 1)
				#print("DC_L: ", dc_L)
				#print("DC_R: ", dc_R)
				
			"""
			#print("Reduced rate: ", reducedRate)
			print("RatioR: ", ratioR)
			print("RatioL: ", ratioL)
			last_ratioR = ratioR
			last_ratioL = ratioL
			dc_R = min(dutyCyclePcnt*ratioR, 100)
			dc_L = min(dutyCyclePcnt*ratioL, 100)
			"""
			# May Remove this
			if counterBR >= numTicks:
				dc_R = 0
			if counterFL >= numTicks:
				dc_L = 0
				
			pwm_R.ChangeDutyCycle(dc_R)
			pwm_L.ChangeDutyCycle(dc_L)
			
			if (counterBR >= numTicks and counterFL >= numTicks):
			#Old Statement
			#(max(counterBR, counterFL) >= numTicks):
				breakIdx = i
				print("Counter BR: ", counterBR)
				print("Counter FL: ", counterFL)
				print("Num ticks: " , numTicks)
				#print("Break Idx: ", breakIdx)
				break
				
		pwm_R.stop()
		pwm_L.stop()
		self.gameover()
		#print("Distance Covered: ", distance_m, "(m)")
		#print("Corresponding Encoder Ticks: ", numTicks)
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
		#writeOut = (self.PathCommands, self.countsBR, self.countsFL, self.timeUpdates)
		#TODO Figure this out
		#print("This is what was saved to a file:")
		#print(self.PathCommands)
		pickle.dump(self.PathCommands, self.fptr)
		self.fptr.close()
		
		print("Pins properly reset. Teleop Controls Destroyed")		
	
	def key_input(self, event):
		self.init()
		print("Key: ", event)
		event = event.lower()
		if event == "w":
			dutyCyclePercent = 90
			dist_In = float(input("Going forward. Please Input Desired Distance (In)"))
			dist_m = convertIn2Meters(dist_In)
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
			dutyCyclePercent = 90
			dist_In = float(input("Going in Reverse. Please Input Desired Distance (In)"))
			dist_m = convertIn2Meters(dist_In)
			self.reverse(dist_m, dutyCyclePercent)
		elif event == "pic":
			email01.main()
		else:
			print( "Invalid Key Pressed")


			
		
if __name__ == "__main__":
	sys.path.insert(0, '/home/pi/enpm809T/gripper_toolbox/')
	import gripper as grip

	myMotor = motorControl()
	myGrip = grip.gripper()
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
		
		#gripperPos = float(input("Please Enter the gripper position."))
		#myGrip.move2Pos(gripperPos)
