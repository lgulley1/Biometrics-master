import face_recognition
import cv2
from cv2 import *
import time
import os

#db setup
conn = sqlite3.connect('example.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS FACE_DATA
             (score real,
			 userID INTEGER,
			 FOREIGN KEY(userID) REFERENCES USER(userID))''')


def compareTwoImages(img1, img2): #returns similarity score between two jpeg images
	if img1[len(img1)-4:] != ".jpg" and img1[len(img1)-4:] != ".jpeg":
		img1 += ".jpg"
	if img2[len(img2)-4:] != ".jpg" and img2[len(img2)-4:] != ".jpeg":
		img2 += ".jpg"
	img1_loaded = face_recognition.load_image_file(img1)
	img2_loaded = face_recognition.load_image_file(img2)
	img1_encoded = [face_recognition.face_encodings(img1_loaded)[0]]
	img2_encoded = face_recognition.face_encodings(img2_loaded)[0]
	face_distance = face_recognition.face_distance(img1_encoded, img2_encoded)
	return 1-face_distance[0]

def captureImage(): #capture faces from webcam and save in format userX.jpg
	fileExists = True
	i = 0
	while(fileExists):
		if os.path.isfile("user" + str(i) + ".jpg") or os.path.isfile("user" + str(i) + ".jpeg"):
			i += 1
		else:
			fileExists = False
	cam = cv2.VideoCapture(0)
	s, img = cam.read()
	imwrite("user" + str(i) + ".jpg", img)
	cam.release()