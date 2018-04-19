#USAGE
'''
Run script.
To begin recording, left click on very top left of screen. Recording will begin {DELAY} seconds after the click.
To end recording, right click the very top left of screen.
Results will be stored in whatever directory the script is run
*Ensure grid size is correct before running
'''

import wx
from pynput import mouse
from pynput import keyboard
import timeit
import time
import math
import sqlite3

#db setup
conn = sqlite3.connect('example.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS USER
             (userID INTEGER PRIMARY KEY, 
			 name text)''')
c.execute('''CREATE TABLE IF NOT EXISTS MOUSE_DATA
             (leftClick real, 
			 rightClick real, 
			 time real, 
			 movementSpeeds text,
			 userID INTEGER, 
			 FOREIGN KEY(userID) REFERENCES USER(userID))''')


#forces game to wait until left click on top left of screen
startGame = False

#the number of quadrants is the square of this number
gridSize = 5
delay = 4 #set delay for recording after top-left click

#stores current position of mouse and time since last quadrant transfer
pos = -1
timeSinceLastMove = -1

#for storing result data
movement = []
movement_speed = []
leftClicks = 0
rightClicks = 0

#defines screen size
app = wx.App(False)
screen_width = wx.GetDisplaySize()[0]
screen_height = wx.GetDisplaySize()[1]

#records beginning and end of game (measures length of game in time)
startTime = 0
endTime = 0

#used to count occurrences
DISTANCE = 7

#removes all entries in a dictionary which have a second value of 0
def removeZeroes(d):
	newD = {}
	for i in range(1, 10001):
		if(d[str(i)] != 0):
			newD.update({str(i) : d[str(i)]})
	return newD

def counter_cosine_similarity(c1, c2): #find similarity score between two dictionaries
    terms = set(c1).union(c2)
    dotprod = sum(c1.get(k, 0) * c2.get(k, 0) for k in terms)
    magA = math.sqrt(sum(c1.get(k, 0)**2 for k in terms))
    magB = math.sqrt(sum(c2.get(k, 0)**2 for k in terms))
    return round((dotprod / (magA * magB)), 2)


def countOccurrences(s): #count number of occurences in string (s), based on distance of (DISTANCE), returns dictionary
	#global DISTANCE
	r = []
	for i in range(0, len(s)):
		if(len(str(s[i:(i+DISTANCE)])) == DISTANCE):
			r.append(str(s[i:(i+DISTANCE)]))
	r2 = {}
	for i in r:
		r2.update({str(i) : r.count(i)})
	results = {}
	r3 = sorted(r2.items(), key=lambda r2: r2[1])
	for t in r3:
		results.update({t[0] : t[1]})
	return results


def updatePos(newPos): #updates the new position and saves it to "movement", and saves it's speed from the last quadrant to "movement speed"
	global pos
	global timeSinceLastMove
	if pos != newPos:
		pos = newPos
		movement.append(pos) #save position
		print("Moved to pos: " + str(pos))
		timeChange = timeit.default_timer() - timeSinceLastMove
		movement_speed.append(timeChange) #save time
		timeSinceLastMove = timeit.default_timer()


def on_move(x, y): #detects movement between quadrants
	if startGame:
		squareSizeX = screen_width/gridSize #specifies quadrant size
		squareSizeY = screen_height/gridSize
		posMovedTo = 0
		for i in range(1,gridSize+1):
			for k in range(1,gridSize+1):
				if x <= squareSizeX*k and y <= squareSizeY*i and x >= (squareSizeX*(k-1)) and y >= (squareSizeY*(i-1)):
					updatePos(posMovedTo+1)
				posMovedTo += 1


def recordResults():
	global startTime
	global endTime
	overallTime = endTime - startTime
	average_movement = {}
	#records every mouse movement as string
	f = open("mouse_movements.txt", "w+")
	for i in range(0, len(movement)):
		if i != len(movement) - 1:
			f.write(str(movement[i]))
		else:
			f.write(str(movement[i]))
	#records average usage of each quadrant
	#divides each quadrant with a value > 0 by the total number of quadrants with a value > 0
	movement_count = {}
	for i in range(1, gridSize**2 + 1):
		movement_count.update({str(i) : movement.count(i)}) #counts number of times quadrant accessed
	for i in range(1, gridSize**2 + 1):
		if(movement_count[str(i)] != 0): #can be modified to accept only higher values, removes all values that = 0 from movement_count
			average_movement.update({str(i) : movement_count[str(i)]})
	#average movement is now a dict of strings and their counts, with all 0's removed
	nAvgMovement = {}
	for i in average_movement:
		nAvgMovement.update({str(i) : average_movement[str(i)]/len(average_movement)})
		
	f.write("\nLocation Frequency: " + str(nAvgMovement))
	f.close()

	#records number of clicks
	f2 = open("clicks.txt", "w+")
	if leftClicks == 0 and rightClicks == 0:
		f2.write("Left Clicks: 0\n")
		f2.write("Right Clicks: 0\n")
	else:
		f2.write("Left Clicks: " + str((leftClicks)/(leftClicks + rightClicks)) + "\n")
		f2.write("Right Clicks: " + str((rightClicks)/(leftClicks + rightClicks)) + "\n")
	f2.close()

	#records mouse speed between quadrants
	#find value by dividing sum of all movement speeds with the number of movement speeds recorded
	f3 = open("mouse_speed.txt", "w+")
	movement_speed.pop(0) #remove first element, because it's the first time and is always incorrect
	for i in movement_speed:
		f3.write(str(i) + "\n")
	f3.write("Average Time: " + str(sum(movement_speed)/len(movement_speed)))
	f3.close()

	#records all above results 
	f4 = open("all_results.txt", "w+")
	finalResults = nAvgMovement
	if leftClicks == 0 and rightClicks == 0:
		finalResults.update({"leftClicks" : 0})
		finalResults.update({"rightClicks" : 0})
	else:
		finalResults.update({"leftClicks" : (leftClicks)/(leftClicks + rightClicks)})
		finalResults.update({"rightClicks" : (rightClicks)/(leftClicks + rightClicks)})
	finalResults.update({"time" : sum(movement_speed)/len(movement_speed)})
	f4.write(str(finalResults))
	f4.close()


def on_click(x, y, button, pressed): #starts/stops game and records mouse clicks
	global leftClicks
	global rightClicks
	global startGame
	global startTime
	global endTime
	if button == mouse.Button.left:
		leftClicks += 1
	if button == mouse.Button.right:
		rightClicks += 1
	if x == 0 and y == 0 and button == mouse.Button.left: #starts recording
		leftClicks -= 1
		startTime = timeit.default_timer()
		startGame = True
		time.sleep(delay)
	if x == 0 and y == 0 and button == mouse.Button.right: #ends recording
		rightClicks -= 1
		endTime = timeit.default_timer()
		return False


#collects mouse events until released
with mouse.Listener(
		on_move=on_move,
		on_click=on_click) as listener:
	listener.join()

#save results
recordResults()