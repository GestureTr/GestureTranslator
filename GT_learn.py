import sys
sys.path.append('C:/Python27/Lib/site-packages');
import cv2
import numpy as np
import util as ut

trainDataFolder = 'TrainData/'
imgFolder = 'TrainData/img/'

letter=0
counter=0
recording=False

cam=int(0)
cap=cv2.VideoCapture(cam)
#cap.set(3, 640)
#cap.set(4, 480)
#cap.set(6, 30)

def nothing(x) :
    pass

# cv2.namedWindow('trackbar')
# cv2.createTrackbar('Y_min','trackbar',0,255,nothing)
# cv2.createTrackbar('Y_max','trackbar',0,255,nothing)
# cv2.createTrackbar('Cr_min','trackbar',0,255,nothing)
# cv2.createTrackbar('Cr_max','trackbar',0,255,nothing)
# cv2.createTrackbar('Cb_min','trackbar',0,255,nothing)
# cv2.createTrackbar('Cb_max','trackbar',0,255,nothing)
while(cap.isOpened()):
	# Y_min = cv2.getTrackbarPos('Y_min','trackbar')
	# Y_max = cv2.getTrackbarPos('Y_max','trackbar')
	# Cr_min = cv2.getTrackbarPos('Cr_min','trackbar')
	# Cr_max = cv2.getTrackbarPos('Cr_max','trackbar')
	# Cb_min = cv2.getTrackbarPos('Cb_min','trackbar')
	# Cb_max = cv2.getTrackbarPos('Cb_max','trackbar')
	_, img = cap.read()
	img = ut.initializeInputImage(img)
	
	#cv2.rectangle(img,(900,100),(1300,500),(255,0,0),3)
	#img1=img[100:500,900:1300]
	#img_ycrcb = cv2.cvtColor(img1, cv2.COLOR_BGR2YCR_CB)
	#blur = cv2.GaussianBlur(img_ycrcb,(11,11),0)
	# skin_ycrcb_min = np.array((Y_min,Cr_min,Cb_min))
	# skin_ycrcb_max = np.array((Y_max,Cr_max,Cb_max))

	imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

	#mask = ut.maskImageSkin(imgHSV)
	mask = ut.maskImage(imgHSV)
	
	#gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	#ret,mask = cv2.threshold(gray.copy(),20,255,cv2.THRESH_BINARY)
	contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
	#cnt=getMaxContour(contours,4000)
	if len(contours) != 0:
		biggestContour = ut.getBiggestContour(contours)
		x,y,w,h = cv2.boundingRect(biggestContour)
		croppedFrame=img[y:y+h,x:x+w]
		croppedFrame=cv2.bitwise_and(croppedFrame,croppedFrame,mask=mask[y:y+h,x:x+w])
		#croppedFrame=cv2.resize(croppedFrame,(200,200))
		cv2.imshow('Trainer',croppedFrame)
	cv2.imshow('Frame',img)
	cv2.imshow('Thresh',mask)
	
	k = 0xFF & cv2.waitKey(10)
	
	if k == 13:
		print 'enter pressed?'
		recording = True
	
	if recording == True:
		fileName = str(unichr(letter+64) + "_" + str(counter))
		
		#croppedFrame = cv2.cvtColor(croppedFrame, cv2.COLOR_BGR2GRAY)
		print 'saving image to: ', fileName
		
		if counter == 0:
			cv2.imwrite(imgFolder + fileName + '.jpg', croppedFrame)
		
		#hist = ut.hogImage(croppedFrame)
		#print 'hist old = ', type(hist), ' ', type(hist[0]), ' ', len(hist)
		hist = ut.hogImage2(croppedFrame)
		#hist = np.asarray(hist)
		#print 'hist = ', type(hist), ' ', type(hist[0]), ' ', len(hist)
		
		np.save(trainDataFolder + fileName + '.npy', hist)
		#np.savetxt(trainDataFolder + fileName + '.txt', hist)
		
		counter += 1
		
		if counter == ut.getTrainDataCount():
			counter = 0
			letter += 1
			recording = False

cap.release()        
cv2.destroyAllWindows()