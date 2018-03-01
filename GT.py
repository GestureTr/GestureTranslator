import sys
import threading
from threading import Thread
from PyQt4 import QtCore
from PyQt4.QtCore import QThread
from PyQt4 import QtGui
sys.path.append('C:/Python27/Lib/site-packages');
import collections
import Queue
import numpy as np
import cv2
import util as ut
import svm as st 
import re
import tracks_bars as tb
import gui
import detection as det
from gui import Window

FRAMES = Queue.Queue(10)
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
TRAIN_LETTERS = 27
CAMERA_INDEX = 0
actualCameraWidth = CAMERA_WIDTH
actualCameraHeight = CAMERA_HEIGHT

class CameraConsumer(QThread):
	def __init__(self, parent = None):
		QThread.__init__(self)
		
		self.run = True
		self.skinMask = True
		
		self.connect(self, QtCore.SIGNAL("stopConsumer()"), self.stopConsumer)
		self.connect(self, QtCore.SIGNAL("keyPressed(PyQt_PyObject)"), self.keyPressed)
		self.connect(self, QtCore.SIGNAL("useRedColor(PyQt_PyObject)"), self.useRedColor)
		self.connect(self, QtCore.SIGNAL("useSkinColor(PyQt_PyObject)"), self.useSkinColor)
		
	def stopConsumer(self):
		self.run = False
			
	def keyPressed(self, event):
		if event.key() == QtCore.Qt.Key_Return:
			self.skinMask = not self.skinMask
			print 'use skin mask = ', self.skinMask
			
	def useSkinColor(self):
		print "using skin color."
		self.skinMask = True
		
	def useRedColor(self):
		print "using red color."
		self.skinMask = False
		
	def run(self):		
		while (self.run):
			img = FRAMES.get(block = True)
			
			imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
			
			# red color mask
			if self.skinMask == True:
				mask = ut.maskImageSkin(imgHSV)
			else:
				mask = ut.maskImage(imgHSV)
			
			#contours,hierarchy = cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL, 2) 
			#contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
			contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
			cutout = None

			if len(contours) != 0:
				biggestContour = ut.getBiggestContour(contours)
					
				diameter, extremes, distance = ut.getContourProperties(biggestContour)
				#print 'diameter = ', diameter, ' extremes = ', extremes, ' distance = ', distance
				minDiameter = (0.2) * ((actualCameraWidth + actualCameraHeight) / 2)
				minDistance = (0.1) * ((actualCameraWidth + actualCameraHeight) / 2)
				#print "minDistance = ", minDistance, " minDiameter = ", minDiameter
				
				if diameter > minDiameter and distance > minDistance:
					gesture, cutout, predicted, recx, recy, recw, rech = st.getGestureImg(biggestContour, img, mask, model)   # passing the trained model for prediction and fetching the result
					
					# draw rectangle showing detection range
					cv2.rectangle(img, (recx, recy), (recx + recw, recy + rech), (0, 255, 0), 1)
					
					if predicted != '' and np.any(gesture): #some letter was detected 
						#cv2.imshow('PredictedGesture', gesture) # showing the best match or prediction
						#window.updateGestureImage(gesture)
						self.emit(QtCore.SIGNAL("updateGestureImage(PyQt_PyObject)"), gesture)
						detection.addLetter(predicted)
					else:
						print "WARNING: invalid area"
						#cv2.destroyWindow('PredictedGesture')
						#print 'predicted = ', predicted 
						#print 'gesture = ', gesture
						#print 'recx=', recx
						#print 'recy=', recy
						#print 'recw=', recw
						#print 'rech=', rech
				else: # contour too small
					detection.noLetterDetected()
					#cv2.destroyWindow('PredictedGesture')
					
				ut.drawExtremes(img, extremes)
			
			else: # no contour detected
				detection.noLetterDetected()
				
			#cv2.putText(img, detection.getLettersString(), (10, 200), font, 1, (0, 0, 255), 1) # show predicted letters flow
			#cv2.putText(img, detection.getSentenceString(), (10, 300), font, 3, (0, 255, 0), 1) # show predicted letters flow
			#cv2.putText(img, predicted, (10, 100), font, 4, (255, 0, 0), 2)  # show predicted letter
			
			###
			#window.updateCameraImage(img)
			self.emit(QtCore.SIGNAL("updateCameraImage(PyQt_PyObject)"), img)
			###
			
			#cv2.imshow('Frame original', img) # show unprocessed image
			#det = cv2.bitwise_and(img, img, mask = mask) # process image 
			
			if np.any(cutout):
				#cutout = cv2.cvtColor(cutout, cv2.COLOR_RGB2BGR)
				#cutout = ut.maskImage(cutout)
				cutout = cv2.cvtColor(cutout, cv2.COLOR_GRAY2BGR)
				self.emit(QtCore.SIGNAL("updateCutoutImage(PyQt_PyObject)"), cutout)
				#cv2.imshow('Frame detection', cutout) # show processed image (detection)
			#else:
				#cv2.destroyWindow('Frame detection')
				
			#cv2.imshow('Mask', mask) # show mask
			#print 'updating...'
			#window.updateText(detection.getSentenceString())
			self.emit(QtCore.SIGNAL("updateText(PyQt_PyObject)"), detection.getSentenceString())
			
class CameraProducer(QThread):
	def __init__(self, cap, parent = None):
		QThread.__init__(self)
		
		self.run = True
		self.cap = cap
		
		self.connect(self, QtCore.SIGNAL("stopProducer()"), self.stopProducer)
		
	def stopProducer(self):
		self.run = False
			
	def run(self):		
		while (self.run and self.cap.isOpened()):
			ret, img = self.cap.read()
			
			if ret:
				img = ut.initializeInputImage(img)
				FRAMES.put(img)

def exitHandler():
	print 'exiting...'
	print 'closing threads...'
	consumerThread.emit(QtCore.SIGNAL("stopConsumer()"))
	producerThread.emit(QtCore.SIGNAL("stopProducer()"))
	
	print 'releasing camera...'
	cap.release()        
	cv2.destroyAllWindows()
	
	print 'exited.'
	
# main function
if __name__ == "__main__":
	# initialize font
	font = cv2.FONT_HERSHEY_PLAIN

	# track bars
	trackbarWindowName = 'color range parameter'
	
	# word detection 
	detection = det.Detection()

	#train SVM model
	model = st.trainSVMLight(TRAIN_LETTERS)
	#model.save("model.dat")
	#model = st.SVM()
	#model.load("model.dat")

	# open camera (default is 0)
	#cam=int(raw_input("Enter Camera number: "))
	cam = int(CAMERA_INDEX)
	cap = cv2.VideoCapture(cam)
	cap.set(3, CAMERA_WIDTH)
	cap.set(4, CAMERA_HEIGHT)
	
	actualCameraWidth = cap.get(3)
	actualCameraHeight = cap.get(4)

	#display track bars
	#tb.showTrackBars(trackbarWindowName)

	app = QtGui.QApplication(sys.argv)
	app.aboutToQuit.connect(exitHandler)
	
	consumerThread = CameraConsumer()
	producerThread = CameraProducer(cap)
		
	window = Window(consumerThread)
	window.setFocus(True)
	window.show()
	
	producerThread.start()
	consumerThread.start()

	sys.exit(app.exec_())

	###########

