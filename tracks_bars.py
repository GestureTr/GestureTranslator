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
