import matplotlib.pyplot as plt
import pickle
import numpy as np
from retrieval import convertMeters2In
"""
from tkinter import filedialog
from tkinter import *
import os

currDir = os.system("pwd")
root = Tk()
root.filename = filedialog.askopenfilename(initialdir = currDir, title = "Select File", filetypes = ("all files", "*.*"))
print(root.filename)
"""
fn = "selectedMoves_20190812-181135.pkl"
trajData = pickle.load(open(fn, "rb"))
allXPos = np.zeros((len(trajData), 1))
allYPos = np.zeros((len(trajData), 1))
allOrients = np.zeros((len(trajData),1))
cnt = 0
for pos, orient in trajData:
	xPos = convertMeters2In(pos[0])
	yPos = convertMeters2In(pos[1])
	allXPos[cnt] = xPos
	allYPos[cnt] = yPos
	allOrients[cnt] = orient
	cnt += 1

#print(allXPos)
#print(allYPos)
plt.figure(1)
#plt.hold(True)
colorCycle = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

for i in range(1,len(allXPos)-1):
	plt.plot(allXPos[i-1:i+1], allYPos[i-1:i+1], linestyle = '-', c = colorCycle[(i+6)%7])

for j in range (0, len(allOrients)):
	plt.plot(allXPos[j], allYPos[j],
	#marker = "o", markerSize = 20, c = colorCycle[j%7]) 
	marker = (3, 0, allOrients[j]), markerSize = 8, c = colorCycle[j%7]) 

plt.axis('equal')
plt.grid(True)
plt.title('Robot Trajectory')
plt.show()
#print(position)
