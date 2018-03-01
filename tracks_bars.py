import sys
import cv2

def nothing(x) :
    pass

def showTrackBars(window_name):
	cv2.namedWindow(window_name)
	cv2.resizeWindow(window_name, 400,800)

	# create trackbars for color change
	cv2.createTrackbar('r1', window_name, 0, 255,nothing)
	cv2.createTrackbar('g1',window_name,0,255,nothing)
	cv2.createTrackbar('b1',window_name,75,255,nothing)
	cv2.createTrackbar('r2',window_name,45,255,nothing)
	cv2.createTrackbar('g2',window_name,25,255,nothing)
	cv2.createTrackbar('b2',window_name,255,255,nothing)

	#cv2.createTrackbar('r3', window_name, 255, 255,nothing)
	#cv2.createTrackbar('g3',window_name,85,255,nothing)
	#cv2.createTrackbar('b3',window_name,85,255,nothing)
	#cv2.createTrackbar('r4',window_name,255,255,nothing)
	#cv2.createTrackbar('g4',window_name,255,255,nothing)
	#cv2.createTrackbar('b4',window_name,255,255,nothing)
def getTrackBarValues(trackbarWindowName):	r1 = cv2.getTrackbarPos('r1',  trackbarWindowName)	g1 = cv2.getTrackbarPos('g1', trackbarWindowName)	b1 = cv2.getTrackbarPos('b1', trackbarWindowName)	r2 = cv2.getTrackbarPos('r2', trackbarWindowName)	g2 = cv2.getTrackbarPos('g2', trackbarWindowName)	b2 = cv2.getTrackbarPos('b2', trackbarWindowName)	return r1, g1, b1, r2, g2, b2