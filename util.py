import cv2 
import numpy as np
from numpy.linalg import norm

def getTrainDataCount():
	return 500

def nothing(x):
    pass
    
def nothing():
    pass
    
def initializeInputImage(inputImage):
	outputImage = cv2.flip(inputImage, 1) # flip image horizontaly (mirror-like)
	#outputImage = cv2.medianBlur(outputImage, 5) # remove noise
	outputImage = cv2.GaussianBlur(outputImage, (5, 5), 0) # smooth the image
	return outputImage
	
def checkEquality(list):
	iterator = iter(list)
	try:
		first = next(iterator)
	except StopIterator:
		return True
	return all(first == rest for rest in iterator)
	
def getBiggestContour(contours):
	c = max(contours, key = cv2.contourArea)
	return c

def filterByValue(expected, letters):
	if len(letters) > 0:
		expectedLetter = letters[0]
		temp = []
		for el in letters:
			#print 'el=', el, 'expectedLetter=', expectedLetter
			if el == expected: temp.append(el)
		return temp
	else: 
		return None

#Here goes my wrappers:
def hogImage(img):
	samples=[]
	imageParams = img.shape
	aspectRatio = float(float(imageParams[0]) / float(imageParams[1]))
	img = cv2.resize(img, (200,200))
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	
	gx = cv2.Sobel(img, cv2.CV_32F, 1, 0)
	gy = cv2.Sobel(img, cv2.CV_32F, 0, 1)
	mag, ang = cv2.cartToPolar(gx, gy)
	bin_n = 16
	bin = np.int32(bin_n*ang/(2*np.pi))
	bin_cells = bin[:100,:100], bin[100:,:100], bin[:100,100:], bin[100:,100:]
	mag_cells = mag[:100,:100], mag[100:,:100], mag[:100,100:], mag[100:,100:]
	hists = [np.bincount(b.ravel(), m.ravel(), bin_n) for b, m in zip(bin_cells, mag_cells)]
	hist = np.hstack(hists)

	# transform to Hellinger kernel
	eps = 1e-7
	hist /= hist.sum() + eps
	hist = np.sqrt(hist)
	hist /= norm(hist) + eps # zmienione
	
	#print ' ', imageParams[0], ' ', imageParams[1], ' ', aspectRatio
	hist *= aspectRatio
	
	return hist
	
def hogImage2(img):
	imageParams = img.shape
	aspectRatio = float(float(imageParams[0]) / float(imageParams[1]))
	
	img = cv2.resize(img, (256, 256))
	#img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	
	winSize = (128, 128)
	blockSize = (16, 16)
	blockStride = (8, 8)
	cellSize = (8, 8)
	nbins = 9
	derivAperture = 1
	winSigma = 4.
	histogramNormType = 0
	l2HysThreshold = 2.0000000000000001e-01
	gammaCorrection = 0
	nlevels = 64
	
	hog = cv2.HOGDescriptor(winSize, blockSize, blockStride, cellSize, nbins, derivAperture, winSigma, histogramNormType, l2HysThreshold, gammaCorrection, nlevels)
	#hog = cv2.HOGDescriptor()
	
	winStride = (8, 8)
	padding = (8, 8)
	locations = ((128, 128),)
	hist = hog.compute(img, winStride, padding, locations)
	#hist = hog.compute(img)
	#hist = np.hstack(hist)
	#print hist
	hist = hist[:,0].astype(float)
	hist = np.hstack(hist)
	
	eps = 1e-7
	hist /= hist.sum() + eps
	hist = np.sqrt(hist)
	hist /= norm(hist) + eps
	
	hist *= aspectRatio
	
	return hist

def getContourProperties(contour):
	area = cv2.contourArea(contour)
	equiDiameter = np.sqrt(4 * area / np.pi)
	
	leftmost = tuple(contour[contour[:, :, 0].argmin()][0])
	rightmost = tuple(contour[contour[:, :, 0].argmax()][0])
	topmost = tuple(contour[contour[:, :, 1].argmin()][0])
	bottommost = tuple(contour[contour[:, :, 1].argmax()][0])
	
	xSubtract = np.subtract(rightmost, leftmost)
	ySubtract = np.subtract(bottommost, topmost)
	
	distance = norm(xSubtract - ySubtract)
	
	return equiDiameter, [leftmost, rightmost, topmost, bottommost], distance
	
def drawExtremes(img, extremes):
	if len(extremes) != 4: # only when 4 points are available
		pass
	
	cv2.circle(img, extremes[0], 2, (0, 255, 0), 2, lineType=8, shift=0)
	cv2.circle(img, extremes[1], 2, (0, 255, 0), 2, lineType=8, shift=0)
	cv2.circle(img, extremes[2], 2, (0, 255, 0), 2, lineType=8, shift=0)
	cv2.circle(img, extremes[3], 2, (0, 255, 0), 2, lineType=8, shift=0)
	
def maskImage(imgHSV):
	lower_red = np.array([0, 100, 100], dtype=np.uint8)
	upper_red = np.array([10, 255, 255], dtype=np.uint8)
	mask1 = cv2.inRange(imgHSV, lower_red, upper_red)
	lower_red = np.array([170, 100, 100], dtype=np.uint8)
	upper_red = np.array([180, 255, 255], dtype=np.uint8)
	mask2 = cv2.inRange(imgHSV, lower_red, upper_red)
	mask = mask1 + mask2

	return mask
	
def maskImageSkin(imgHSV):
	lower_red = np.array([0, 48, 80], dtype=np.uint8)
	upper_red = np.array([20, 255, 255], dtype=np.uint8)
	mask = cv2.inRange(imgHSV, lower_red, upper_red)
	
	return mask