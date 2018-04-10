from pynput import mouse
from pynput import keyboard
import timeit

leftClicks = 0
rightClicks = 0
movement = []
movement_speed = []
pos = -1
time = -1
def updatePos(newPos):
	global movement_speed
	global pos
	global time
	if pos != newPos:
		pos = newPos
		movement.append(pos)
		if time == -1:
			time = timeit.default_timer()
		else:
			timeChange = timeit.default_timer() - time
			movement_speed.append(timeChange)
			time = timeit.default_timer()


def on_move(x, y):
	#top 3 boxes
	if x < 426 and y < 266:
		updatePos(1)
	elif x < 852 and y < 266:
		updatePos(2)
	elif x < 1280 and y < 266:
		updatePos(3)
	#middle 3 boxes
	elif x < 426 and y < 533:
		updatePos(4)
	elif x < 852 and y < 533:
		updatePos(5)
	elif x < 1280 and y < 533:
		updatePos(6)
	#bottom 3 boxes
	elif x < 426 and y < 800:
		updatePos(7)
	elif x < 852 and y < 800:
		updatePos(8)
	elif x < 1280 and y < 800:
		updatePos(9)


def recordResults():
	f = open("mouse_movements.txt", "w+")
	for i in movement:
		f.write(str(i))
	f.close()
	f2 = open("clicks.txt", "w+")
	f2.write("Left Clicks: " + str(leftClicks/2) + "\n")
	f2.write("Right Clicks: " + str(rightClicks/2))
	f2.close()
	f3 = open("mouse_speed.txt", "w+")
	for i in movement_speed:
		f3.write(str(i) + "\n")
	f3.close()


def on_click(x, y, button, pressed):
	global leftClicks
	global rightClicks
	if button == mouse.Button.left:
		leftClicks += 1
	if button == mouse.Button.right:
		rightClicks += 1
	if x == 0 and y == 0 and button == mouse.Button.left:
		leftClicks -= 1
		recordResults()
		return False


def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))


key_listener = keyboard.Listener(on_release=on_press)


# Collect events until released
with mouse.Listener(
		on_move=on_move,
		on_click=on_click) as listener:
	listener.join()
