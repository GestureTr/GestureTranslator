import sys
import collections
import util as ut

letterSpace = '@'
letterNewWord = ". "

class Detection:
	def __init__(self):
		self.queueSize = 15 # maximum letters in detection
		self.letters = collections.deque(maxlen=self.queueSize) # collection of detected letters 
		self.sentence = [] # detected, accepted prediction list
		
		self.noLetterCounterMax = self.queueSize * 2
		self.noLetterCounter = 0
		
		pass
		
	def addLetter(self, letter):
		self.letters.append(letter) # add letter to list
		
		allEquals = ut.checkEquality(self.letters)
		
		if not allEquals: # collect again
			self.letters.clear()
			pass
		
		listFull = len(self.letters) == self.queueSize
		
		if listFull: # list is full and all letters are the same (multiple success detection)
			print "Accepted letter: ", letter
			self.noLetterCounter = 0
			if letter == letterSpace:
				letter = ' '
			self.rememberLetter(letter)
	
	def getLettersString(self):
		return " ".join(self.letters)
		
	def getSentenceString(self):
		return "".join(self.sentence)
		
	def rememberLetter(self, letter):
		self.sentence.append(letter) # remember as a letter in word 
		self.letters.clear() # clear all previous letters
		
	def noLetterDetected(self):
		self.noLetterCounter += 1
		
		if self.noLetterCounter == self.noLetterCounterMax and len(self.sentence) > 0:
			self.rememberLetter(letterNewWord)
			print "New word detected."