import cv2
import numpy as np
import util as ut

svm_params = dict(kernel_type = cv2.SVM_RBF,
                    svm_type = cv2.SVM_C_SVC,
                    C=2.67, gamma=5.383)
					
class StatModel(object):
    def load(self, fn):
        self.model.load(fn)  #python rapper bug
    def save(self, fn):
        self.model.save(fn)

class SVM(StatModel):
    def __init__(self):
        self.model = cv2.SVM()

    def train(self, samples, responses):
        self.model.train(samples,  responses, params = svm_params) # inbuilt training function 

    def predict(self, samples):
        return self.model.predict_all(samples).ravel()

def preprocessAllImages(digits):
    samples = []
    for img in digits:
        hist = ut.hogImage(img)
        samples.append(hist)
    return np.float32(samples)
	
def preprocessAllImagesLight(hists):
    samples = []
    for hist in hists:
        samples.append(hist)
    return np.float32(samples)
	
def trainSVM(num):
	imgs=[]
	
	for letter in range(num):
		for counter in range(ut.getTrainDataCount()):
			char = unichr(letter + 1 + 64)
			print 'loading class ', char, ' counter ', counter
			fileName = 'TrainData/' + char + '_' + str(counter + 1) + '.jpg'
			print 'loading file: ', fileName
			imgs.append(cv2.imread(fileName, 0))  # all images saved in a list
			
	labels = np.repeat(np.arange(1, num + 1), ut.getTrainDataCount()) # label for each corresponding image saved above
	samples = preprocessAllImages(imgs)                # images sent for pre processeing using hog which returns features for the images 
	print len(labels)
	print len(samples)
	print 'Loaded ', ut.getTrainDataCount(), ' images for ', num, ' letters. Processig model. Please wait...'
	model = SVM() 
	model.train(samples, labels)  # features trained against the labels using svm
	return model
	
def trainSVMLight(num):
    imgs=[]

    for letter in range(num):
        for counter in range(ut.getTrainDataCount() - 1):
            char = unichr(letter + 64)
            fileName = 'TrainData/' + char + '_' + str(counter + 1) + '.npy'

            if (counter == 0):
                print 'loading class: ', char, ' counter ', counter
                print 'loading file: ', fileName

            imgs.append(np.load(fileName))  # all images saved in a list

    labels = np.repeat(np.arange(0, num), ut.getTrainDataCount() - 1)   # label for each corresponding image saved above
    samples = preprocessAllImagesLight(imgs)
    print len(imgs)
    print len(samples)
    print len(labels)
    print 'Loaded ', ut.getTrainDataCount(), ' images for ', num, ' letters. Processig model. Please wait...'
    model = SVM()
    model.train(samples, labels)  # features trained against the labels using svm
    return model
	
def predict(model, img):
    hist = ut.hogImage(img)
    samples = np.float32([hist])
    resp = model.predict(samples)
    return resp
	
#Get Gesture Image by prediction
def getGestureImg(contour, inputImage, inputMask, model):
    x, y, w, h = cv2.boundingRect(contour)
    #x, y, w, h = cv2.minAreaRect(contour)
    #cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
    
    imgT = inputImage[y:y+h, x:x+w] #crop input image using contour bounds
    width, height, channels = imgT.shape
    
    mask = inputMask[y:y+h, x:x+w] #crop input mask using contour bounds
    widthx, heightx = mask.shape
    
    #print 'width=', width, ' height=', height, ' widthx=', widthx, ' heightx=', heightx
    
    if width != widthx or height != heightx:
        print width, widthx, height, heightx
        return inputImage, imgT, '', 1, 1, 1, 1
        #return cv2.imread('TrainData/A_2.jpg'), 'A'
    
    #print 'draw rectangle: ', x, y, w, h
    #cv2.rectangle(img,(50,50),(100,100),(0,255,0),2)
    #cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)

    imgT = cv2.bitwise_and(imgT, imgT, mask)
    #imgT = cv2.resize(imgT, (200, 200)) # resize to size of train data
    #imgTG = cv2.cvtColor(imgT, cv2.COLOR_BGR2GRAY)
    resp = predict(model, imgT)
    char = unichr(int(resp[0])+64)
    predictedFileName = 'TrainData/img/' + char + '_0.jpg'
    gesture = cv2.imread(predictedFileName)
    #print "resp = ", resp[0] , ' detected class = ', char, ' fileName = ', predictedFileName
    return gesture, mask, char, x, y, w, h