import math

def getMean(aList):
	return float(sum(aList)/len(aList))

def calcArrowOrient(crnrs):
	allXs = []
	allYs = []
	pnts  = []
	for aCnr in crnrs:
		x,y = aCnr.ravel()
		allXs.append(x)
		allYs.append(y)
		pnts.append((x,y))
	centerPtX = getMean(allXs)
	centerPtY = getMean(allYs)
	centerPt = (centerPtX, centerPtY)
	
	# Find the point that does not have a symmetric distance
	allDistances = []
	for aPnt in pnts:
		allDistances.append(normL2(centerPt, aPnt))
	eps = 2
	PntIdx = 0 # FIXME Determine what default Index should be
	for i in range(len(allDistances)):
		#print(allDistances[i])
		noPairs = True
		for j in range(len(allDistances)):
			if not (i==j) and (epsilonEq(allDistances[i],
										 allDistances[j], eps)):
				noPairs = False
		if (noPairs):
			PntIdx = i
	(x,y) = pnts[PntIdx]
	xDist = x - centerPtX
	yDist = y - centerPtY
	
	# Need -y since the y axis was going down for images instead of up
	# Add 180 degrees to make it go from 0 to 360
	orientDeg = math.atan2(-1*yDist, xDist) / math.pi *180
	if orientDeg < 0 :
		orientDeg += 360
	#print(orientDeg)
	return orientDeg
						
	
# Returns the L2 Norm
def normL2(ptA, ptB):
	return ((ptB[1] - ptA[1])**2 + (ptB[0] - ptA[0])**2)**0.5
	
# Returns true if values are within epsilon of each other.
def epsilonEq(valA, valB, ep):
	if valA < valB + ep and valA > valB - ep:
		return True
	else:
		return False
