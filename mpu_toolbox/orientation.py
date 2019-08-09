import sys
sys.path.insert(0, '/home/pi/mpu_toolbox/mpu9250-master/')
from mpu9250.mpu9250 import mpu9250
import numpy as np
import time

class orientComp:
	def __init__ (self, numSamples = 50):
		# Get measurements of the orientation change to account for bias
		self.mpu = mpu9250()
		# Make sure to use the minimum sampling rate
		self.sampleTime = 1/200
		self.biasCalculated = False
		
		xDps = np.zeros((numSamples, 1))
		yDps = np.zeros((numSamples, 1))
		zDps = np.zeros((numSamples, 1))
		
		takenCnt = 0
		for i in range(0,numSamples):
			gReading = self.getGyro()
			xDps[i] = gReading[0]
			yDps[i] = gReading[1]
			zDps[i] = gReading[2]
			
		self.xBias = np.average(xDps)
		self.yBias = np.average(yDps)
		self.zBias = np.average(zDps)
		self.biasCalculated = True
		
	def getGyro(self):
		self.lastTime = time.time()
		updateReady = False
		while not updateReady:
			if (time.time() - self.lastTime < self.sampleTime):
				updateReady = True
		tRet = list(self.mpu.gyro)
		if self.biasCalculated:
			tRet[0] = tRet[0] - self.xBias
			tRet[1] = tRet[1] - self.yBias
			tRet[2] = tRet[2] - self.zBias
			
		return tRet
		
if __name__ == "__main__":
	print("Calling Orientation Comp")
	myOrientComp = orientComp()
	for i in range(0,50):
		print(myOrientComp.getGyro())
