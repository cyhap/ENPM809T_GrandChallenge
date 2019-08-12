import matplotlib.pyplot as plt
import pickle
import numpy as np
from retrieval import convertMeters2In

trajData = pickle.load(open("selectedMoves_20190811-154306.pkl", "rb"))
allXPos = np.zeros((len(trajData), 1))
allYPos = np.zeros((len(trajData), 1))
cnt = 0
for pos, orient in trajData:
	xPos = convertMeters2In(pos[0])
	yPos = convertMeters2In(pos[1])
	allXPos[cnt] = xPos
	allYPos[cnt] = yPos
	cnt += 1

print(allXPos)
print(allYPos)
plt.plot(allXPos, allYPos, 'r-x')
plt.show()
#print(position)
