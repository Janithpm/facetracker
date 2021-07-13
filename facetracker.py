import time
from pyfirmata import Arduino, util, SERVO
import cv2
import numpy as np


cou = 0
coubef = 0
blink_threshhold = 10


def initBoard(comPort, sleeptime):
	print("Setting up Arduino....")
	board = Arduino(comPort)
	time.sleep(sleeptime)
	board.digital[9].mode = SERVO
	board.digital[11].mode = SERVO
	board.digital[9].write(90)
	board.digital[11].write(90)
	print("setup Sucsess !")
	return board

def servoX(pos):
	board.digital[9].write(pos)
	
def servoY(pos):
	board.digital[11].write(pos)

def moveServo(x, y, w, h, maxWidth, maxHeight):
	centerX = int(round(x + w/2))
	centerY = int(round(y + h/2))
	serX = int(np.interp(centerX, [0,maxWidth], [30,150]))
	serY = int(np.interp(centerY, [0,maxHeight], [30,150]))
	# print("point - X :" + str(serX) + "  " + "point - Y :" + str(serY) + "  " + "Drowness Detected")
	servoX(180 - serX)
	servoY(180 - serY)
	time.sleep(0.01)	

def servoDefualt(x, y):
	servoX(x)
	servoY(y)
	time.sleep(0.01)
	
board = initBoard('COM4', 3)
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
blink_cascade = cv2.CascadeClassifier('CustomBlinkCascade.xml')

# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
maxWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
maxHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
horLineStartX = int(maxWidth/2) - 20
horLineEndX = int(maxWidth/2) + 20
horLineY = int(maxHeight/2)
virLineStartY = int(maxHeight/2 - 20)
virLineEndY = int(maxHeight/2 + 20)
virLineX = int(maxWidth/2)

while True:
	coubef = cou
	ret, frame = cap.read()
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	faces = face_cascade.detectMultiScale(gray, 1.3, 5)
	for (x,y,w,h) in faces:
		cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)
		cv2.circle(frame, (int(round(x + w/2)),int(round(y + h/2))), 5, (0,0,255), -1)
		roi_gray = gray[y:y+h,x:x+w]
		roi_frame = frame[y:y+h,x:x+w]

		eyes = eye_cascade.detectMultiScale(roi_gray)
		for (ex,ey,ew,eh) in eyes:
			cv2.rectangle(roi_frame, (ex,ey), (ex+ew,ey+eh), (0,255,0), 2)

		blinks = blink_cascade.detectMultiScale(roi_gray)
		for(bx,by,bw,bh) in blinks:
			cv2.rectangle(roi_frame, (bx,by), (bx+bw,by+bh), (255,0,255), 2)
			cou += 1

		if cou >= blink_threshhold:
			board.digital[3].write(1)
			moveServo(x, y, w, h, maxWidth, maxHeight)
			
		else:
			board.digital[3].write(0)
		
		if coubef == cou:
			cou = 0
			servoDefualt(30, 90)
			

	cv2.line(frame, (horLineStartX, horLineY ), (horLineEndX, horLineY), (200,200,200), 2)
	cv2.line(frame, (virLineX, virLineStartY), (virLineX, virLineEndY), (200,200,200), 2)
	cv2.imshow('frame', frame)
	k = cv2.waitKey(5) & 0xff
	if k == 27:
		break

cap.release()
cv2.destroyAllWindows()





