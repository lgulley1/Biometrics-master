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
import random
import ast

#classes
class MouseData:
	leftclick = -1
	rightclick = -1
	time = {}
	movemementSpeed = -1
	username = ""

	def newMD(self, l, r, t, m, u):
		self.leftclick = l
		self.rightclick = r
		self.time = t
		self.movemementSpeed = m
		self.username = u
		return self


#DEBUG
username = str(random.randint(0,3242342352))

#db setup
conn = sqlite3.connect('test.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS USER
             (username TEXT PRIMARY KEY)''')
c.execute('''CREATE TABLE IF NOT EXISTS MOUSE_DATA
             (leftClick real, 
			 rightClick real, 
			 time real, 
			 movementSpeeds text,
			 username TEXT, 
			 FOREIGN KEY(username) REFERENCES USER(username))''')

#determine if user exists
def userExists(name):
	c.execute('''SELECT EXISTS(SELECT * FROM USER WHERE username=?)''', (name,))
	exists = c.fetchone()
	return (exists == 1)

#get data from database
#returns an array of MouseData objects
def getAllMouseData():
	data = []
	dataObjs = []
	c.execute('''SELECT * FROM MOUSE_DATA''')
	data = c.fetchall()
	for row in data:
		stringFreq = row[2]
		freq = ast.literal_eval(stringFreq)
		dataObject = MouseData().newMD(row[0], row[1], freq, row[3], row[4])
		dataObjs.append(dataObject)
	return dataObjs




#add user if they dont already exist
if(userExists(username) == False):
	c.execute('''INSERT INTO USER(username) VALUES(?)''', (username,))
	

#forces game to wait until left click on top left of screen
startGame = False

#the number of quadrants is the square of this number
gridSize = 5
delay = 0 #set delay for recording after top-left click

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

#weights for similarity score
leftClickWeight = .1
rightClickWeight = .1
timeFreqWeight = .6
movementSpeedWeight = .2
#add user if they dont already exist and start game
username = input("Please enter a username: ")
while(True):
	try:
		if(userExists(username) == False):
			c.execute('''INSERT INTO USER(username) VALUES(?)''', (username,))
			break
	except:
		username = input("Username invalid, choose another: ")

print("Recording starting in " + str(delay) + " seconds...")
startTime = timeit.default_timer()
time.sleep(delay)
startGame = True

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


#create similarity scores for all values based on current data retrieved during execution
#return weighted similarity score along with username (username, score)
def createScoresFor(currentData: MouseData):
	scores = {}
	score = 0
	data = getAllMouseData()
	for d in data:	
		lDiff = abs(currentData.leftclick - d.leftclick)
		rDiff = abs(currentData.rightclick - d.rightclick)
		print(currentData.time)
		print(d.time)
		tDiff = counter_cosine_similarity(currentData.time, d.time)
		mDiff = abs(currentData.movemementSpeed - float(d.movemementSpeed))
		scores.update({d.username: [lDiff, rDiff, tDiff, mDiff]})
	#do the comparisons and give ranks for each metric
	for user in scores:
		print(scores[user][0])

	userFinalRanks = {}

	for user in scores:
		finalRank = scores[user][0]*leftClickWeight + scores[user][1]*rightClickWeight + scores[user][2]*timeFreqWeight + scores[user][3]*movementSpeedWeight
		userFinalRanks.update({user : finalRank})

	sortedRanks = sorted(userFinalRanks.items(), key=lambda x:x[1])
	return sortedRanks


	


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
	global startGame
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
	global leftClicks
	global rightClicks
	global movement_speed

	#divides each quadrant with a value > 0 by the total number of quadrants with a value > 0
	movement_count = {}
	average_movement = {}
	nAvgMovement = {}
	for i in range(1, gridSize**2 + 1):
		movement_count.update({str(i) : movement.count(i)}) #counts number of times quadrant accessed
	for i in range(1, gridSize**2 + 1):
		if(movement_count[str(i)] != 0): #can be modified to accept only higher values, removes all values that = 0 from movement_count
			average_movement.update({str(i) : movement_count[str(i)]})
	#average movement is now a dict of strings and their counts, with all 0's removed
	#total count is the total number of times every quadrant has been visited, combined
	totalCount = 0
	for k in average_movement:
		totalCount += average_movement[str(k)]
	for i in average_movement:
		nAvgMovement.update({str(i) : average_movement[str(i)]/totalCount})

	quadFreqString = str(nAvgMovement) #db ref
	safeFreq = nAvgMovement

	#records number of clicks
	totalClicks = leftClicks + rightClicks
	if leftClicks == 0 and rightClicks == 0:
		leftClicks = 0
		rightClicks = 0
	else:
		leftClicks = (leftClicks)/(totalClicks) #db ref
		rightClicks = (rightClicks)/(totalClicks) #db ref

	#records mouse speed between quadrants
	#find value by dividing sum of all movement speeds with the number of movement speeds recorded
	movement_speed.pop(0) #remove first element, because it's the first time and is always incorrect
	movement_speed = sum(movement_speed)/totalCount #db ref

	#records all above results
	#Save to the database
	c.execute('''INSERT INTO MOUSE_DATA(leftClick, rightClick, time, movementSpeeds, username) VALUES(?,?,?,?,?)''',
	 (leftClicks, rightClicks, quadFreqString, movement_speed, username ))
	conn.commit()
	curr = MouseData().newMD(leftClicks, rightClicks, safeFreq, movement_speed, username)
	print(createScoresFor(curr))
	conn.close()
	


def on_click(x, y, button, pressed): #starts/stops game and records mouse clicks
	global leftClicks
	global rightClicks
	global startGame
	global startTime
	global endTime
	if button == mouse.Button.left:
		leftClicks += 0.5
	if button == mouse.Button.right:
		rightClicks += 0.5
	if x == 0 and y == 0 and button == mouse.Button.right: #ends recording
		rightClicks -= 0.5
		endTime = timeit.default_timer()
		return False


#collects mouse events until released
with mouse.Listener(
		on_move=on_move,
		on_click=on_click) as listener:
	listener.join()

#save results
recordResults()