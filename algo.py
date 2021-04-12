from jellyfish import *
from textblob import Word
import enchant
from numpy import exp
import numpy as np
from symspellpy import SymSpell, Verbosity
import pkg_resources

class Algo:
	def __init__(self,inp,symspell):
		self.inp = inp
		self.candidates = [x for x,_ in Word(inp).spellcheck()]
		self.candidates = self.candidates + enchant.Dict('en').suggest(inp)
		self.candidates = self.candidates + [x.term for x in symspell.lookup(inp,Verbosity.ALL,max_edit_distance=2)]
		
		self.options = []
		for option in self.candidates:
			comparison = soundex(option) == soundex(inp)
			comparison = comparison and not bool([x for x in [' ','-'] if x in option])
			if comparison and option[0].islower():			
				self.options = self.options + [option]
		
		init = False
		distances = None
		for option in self.options:
			count = self.options.count(option)
			done = option in distances[:,0] if init == True else False
			if count >= 2 and not done:
				dist = -1 * levenshtein_distance(inp,option)
				dist = dist + jaro_distance(inp,option)
				dist = dist * self.options.count(option)
				pair = np.array([[option,dist]])
				if init == False:
					distances = pair
					init = True
				else:
					distances = np.concatenate((distances,pair))	
		if init == True:
			distances[:,1] = self.softmax(distances[:,1])	
			print(distances)
			self.out = distances[np.argmax(distances,axis=0)[1]][0]	
		else:
			self.out = self.inp
	def softmax(self,arr):
		arr = exp(arr.astype(float))
		arr = arr / arr.sum()
		return arr
