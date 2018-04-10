import face_recognition
import cv2
import time

video_capture = cv2.VideoCapture(0)

trump1 = face_recognition.load_image_file("trump1.jpg")
trump2 = face_recognition.load_image_file("trump2.jpg")
biden = face_recognition.load_image_file("biden.jpg")

trump1_encoding = face_recognition.face_encodings(trump1)[0]
trump2_encoding = face_recognition.face_encodings(trump2)[0]
biden_encoding = face_recognition.face_encodings(biden)[0]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

known_face_encodings = [
	trump1_encoding,
	trump2_encoding,
	biden_encoding
]

known_face_names = [
	"Trump1",
	"Trump2",
	"Biden"
]

def isRegistered():
	global process_this_frame
	# Grab a single frame of video
	ret, frame = video_capture.read()
	
	# Resize frame of video to 1/4 size for faster face recognition processing
	small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
	
	# Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
	rgb_small_frame = small_frame[:, :, ::-1]
	
	# Only process every other frame of video to save time
	if process_this_frame:
		# Find all the faces and face encodings in the current frame of video
		face_locations = face_recognition.face_locations(rgb_small_frame)
		face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
	
		face_names = []
		time.sleep(3)
		for face_encoding in face_encodings:
			# See if the face is a match for the known face(s)
			matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
	
			# If a match was found in known_face_encodings, just use the first one.
			video_capture.release()
			cv2.destroyAllWindows()
			if True in matches:
				return True
			else:
				return False
	
	process_this_frame = not process_this_frame

if(isRegistered()):
	print("Accepted")
else:
	print("Rejected")