import sys
import threading
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import cv2

class Window(QtGui.QMainWindow):
	def __init__(self, outsideThread, parent = None):
		QMainWindow.__init__(self, parent)
		
		#self.window = QtGui.QMainWindow()
		self.setGeometry(100, 100, 820, 620)
		self.setWindowTitle("Gesture translator")
		
		self.cameraPic = QtGui.QLabel(self)
		self.cameraPic.setGeometry(10, 10, 640, 480)
		
		self.gesturePic = QtGui.QLabel(self)
		self.gesturePic.setGeometry(660, 10, 150, 150)
		self.gesturePic.setStyleSheet("QLabel { background-color: #000 }")
		
		self.cutoutPic = QtGui.QLabel(self)
		self.cutoutPic.setGeometry(660, 170, 150, 150)
		self.cutoutPic.setStyleSheet("QLabel { background-color: #000 }")
		
		self.textBox = QtGui.QLineEdit(self)
		self.textBox.setGeometry(10, 500, 800, 50)
		self.textBox.setReadOnly(True)
		
		self.buttonRed = QtGui.QPushButton("Detect RED", self)
		self.buttonRed.setGeometry(660, 330, 150, 30)
		self.buttonRed.clicked.connect(self.handlePushRed)
		self.buttonRed.setStyleSheet("QPushButton { background-color: #888 }")
		
		self.buttonSkin = QtGui.QPushButton("Detect SKIN", self)
		self.buttonSkin.setGeometry(660, 370, 150, 30)
		self.buttonSkin.clicked.connect(self.handlePushSkin)
		self.buttonSkin.setStyleSheet("QPushButton { background-color: #0f0 }")
		
		self.outsideThread = outsideThread
		#self.window.show()
		
		# control signals for outside of main thread
		self.connect(outsideThread, QtCore.SIGNAL("updateCameraImage(PyQt_PyObject)"), self.updateCameraImage)
		self.connect(outsideThread, QtCore.SIGNAL("updateCutoutImage(PyQt_PyObject)"), self.updateCutoutImage)
		self.connect(outsideThread, QtCore.SIGNAL("updateGestureImage(PyQt_PyObject)"), self.updateGestureImage)
		self.connect(outsideThread, QtCore.SIGNAL("updateText(PyQt_PyObject)"), self.updateText)
		
	def handlePushRed(self):
		self.outsideThread.emit(QtCore.SIGNAL("useRedColor(PyQt_PyObject)"), 'red')
		self.buttonSkin.setStyleSheet("QPushButton { background-color: #888 }")
		self.buttonRed.setStyleSheet("QPushButton { background-color: #0f0 }")
		
	def handlePushSkin(self):
		self.outsideThread.emit(QtCore.SIGNAL("useSkinColor(PyQt_PyObject)"), 'skin')
		self.buttonSkin.setStyleSheet("QPushButton { background-color: #0f0 }")
		self.buttonRed.setStyleSheet("QPushButton { background-color: #888 }")
			
	def keyPressEvent(self, event):
		self.outsideThread.emit(QtCore.SIGNAL("keyPressed(PyQt_PyObject)"), event)
		
	def updateCameraImage(self, img):
		self.showPicture(self.cameraPic, img, 640, 480)
		
	def updateGestureImage(self, img):
		self.showPicture(self.gesturePic, img, 150, 150)
		
	def updateCutoutImage(self, img):
		self.showPicture(self.cutoutPic, img, 150, 150)
	
	def showPicture(self, pic, img, width=None, height=None):
		if width != None and height != None:
			img = cv2.resize(img, (width, height))
		
		#print 'current thread name 2 = ', threading.current_thread()

		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB, img)
		height, width, channels = img.shape
		bytesPerLine = channels * width
		qImg = QtGui.QImage(img.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
		pixmap = QtGui.QPixmap.fromImage(qImg)
		pic.setPixmap(QtGui.QPixmap(pixmap))
		pic.show()
		pic.update()
		
	def updateText(self, string):
		self.textBox.setText(string)
		font = QtGui.QFont()
		font.setPointSize(24)
		self.textBox.setFont(font)