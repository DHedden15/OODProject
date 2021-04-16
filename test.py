#!/Users/will/.pyenv/shims/python3
import tkinter as tk
from tkinter import filedialog, font
from tkinter.font import Font
from tkinter import ttk
import time
from threading import *
import pkg_resources
import pickle
import multiprocessing
from jellyfish import *
from textblob import Word
import enchant
from numpy import exp
import numpy as np
from spellchecker import SpellChecker
import pkg_resources
import re
from copy import deepcopy
from wordfreq import word_frequency
import math

class DocumentEditor:
	def __init__(self, root, content=''):
		self.root = root
		self.frame = tk.Frame(self.root, height=500,width=500)
		self.frame.grid_propagate(False)

		self.font = Font(family='Times New Roman',size=20)

		self.frame.grid_rowconfigure(0,weight=0)
		self.frame.grid_rowconfigure(1,weight=0)
		self.frame.grid_rowconfigure(2,weight=1)
		self.frame.grid_columnconfigure(0,weight=1)

		self.scrollbar = tk.Scrollbar(self.frame)
		self.scrollbar.grid(row=2,column=1,sticky='NSEW')

		menubar = tk.Menu(self.root)
		self.root.config(menu=menubar)

		fileMenu = tk.Menu(menubar)
		menubar.add_cascade(label="File",menu=fileMenu)

		self.settingsFrame = tk.Frame(self.frame)
		self.settingsFrame.grid(row=0,column=0,sticky='E')
		fonts = font.families()
		self.fontvariable = tk.StringVar(self.frame)
		self.fontvariable.set('Times New Roman')
		self.fontvariable.trace('w',self.fontchange)
		self.fontMenu = tk.OptionMenu(self.settingsFrame,self.fontvariable,*fonts)
		self.fontMenu.grid(row=0,column=0)

		sizes = range(1,101)
		self.fontsize = tk.IntVar(self.frame)
		self.fontsize.set(50)
		self.fontsize.trace('w', self.sizechange)
		self.sizeMenu = tk.OptionMenu(self.settingsFrame,self.fontsize,*sizes)
		self.sizeMenu.grid(row=0,column=1)

		self.corrected = ''

		self.line = ttk.Separator(self.frame,orient=tk.HORIZONTAL)
		self.line.grid(row=1,column=0,sticky='EW')

		fileMenu.add_command(label="Save as...",command=self.save)
		fileMenu.add_command(label="Correct Spelling...",command=self.handle,accelerator="Cmd+G")
		fileMenu.add_command(label="Main Menu",command=self.menu)

		self.text = tk.Text(self.frame,borderwidth=3)
		self.text.insert("1.0",content)
		self.text.grid(row=2,column=0,sticky='NSEW')
		self.scrollbar.config(command=self.text.yview)
		self.text.config(font=self.font,undo=True,yscrollcommand=self.scrollbar.set)

		self.text.bind('<period>',self.handle)
		self.frame.pack(fill='both',expand=True)
		self.frame.pack_propagate(0)

	def sizechange(self,*args):
		self.font.config(size=self.fontsize.get())

	def fontchange(self,*args):
		self.font.config(family=self.fontvariable.get())

	def menu(self):
		self.newWindow = tk.Toplevel(self.root)
		self.app = MainMenu(self.newWindow)

	def save(self):
		i = self.text.get("1.0","end-1c")
		filename = filedialog.asksaveasfilename(initialdir = "./",title = "Select file",filetypes = (("PhonetikWrite files","*.pwf"),("all files","*.*")))
		if filename == '':
			return None
		f = open(filename,'w')
		f.write(i)
		f.close()

	def parse_chunk(self,i,returns,j,mutex):
		# Chunk is array of 100 word strings.
		chunk = i[j]
		mutex.acquire()
		e = enchant.Dict('en')
		mutex.release()
		out = []
		for i in range(0,len(chunk)):
			if chunk[i] != '':
				a = Algo(chunk[i],e,mutex)
				out.append(a.out)
		returns[j] = out

	def handle(self,event=None):
		current = self.text.index(tk.CURRENT)
		self.correct()

	def whitespace(self,inp):
		whitespace = []
		for word in inp:
			try:
				index = re.search('\s+', word).start()
				spaces = re.findall('\s+',word)[0]
				whitespace.append([index,spaces])
			except:
				whitespace.append([False,False])
		return whitespace

	def correct(self):
		original = self.text.get("1.0","end-1c")
		pos = deepcopy(tk.CURRENT)
		orig = deepcopy(original)
		if orig != self.corrected:
			i = deepcopy(orig)
			caps = [x for x in i.split(' ') if x != '']
			whitespace = self.whitespace(caps)
			i = [x.lower() for x in caps]
			i = [i[a:a + 100] for a in range(0, len(i), 100)]
			returns = {}
			threads = []
			mutex = Lock()
			for j in range(0,len(i)):
				t = Thread(target=self.parse_chunk,args=(i,returns,j,mutex))
				threads.append(t)
			for thread in threads:
				thread.start()
			for thread in threads:
				thread.join()
			out = ''
			next = 0
			sortedKeys = sorted(returns.keys())
			words = [j for sub in [returns.get(x) for x in sortedKeys] for j in sub]
			out = ''
			for i in range(0,len(words)):
				# or if first word
				isFirst = True if i == 0 or '.' in caps[i-1] else False
				if isFirst:
					period = '.' if '.' in caps[i] and not '.' in words[i] else ''
					w = words[i][0].upper() + words[i][1:] + period + " "
					if whitespace[i][0] != False:
						if whitespace[i][0] != 0:
							w += whitespace[i][1]
						else:
							w = whitespace[i][1] + w
					out += w
				elif caps[i].lower() != caps[i]:
					out += caps[i] + " "
				else:
					period = '.' if '.' in caps[i] and not '.' in words[i] else ''
					w = words[i] + period + " "
					if whitespace[i][0] != False:
						if whitespace[i][0] != 0:
							w += whitespace[i][1]
						else:
							w = whitespace[i][1] + w
					out += w

			out = re.sub('[\n\t\s]+\.','.',out)#.rstrip()
			current = self.text.index("current")
			self.text.mark_set("insert",float(current))
			self.text.delete('1.0', tk.END)
			self.text.insert("1.0", out)
			self.corrected = out

class MainMenu:
	def __init__(self,root):
		self.root = root
		self.root.title("PhonetikWrite")

		new_button = tk.Button(self.root, text="New Document", command=self.new)
		new_button.pack()

		open_button = tk.Button(self.root, text="Open Document", command=self.open)
		open_button.pack()

	def new(self,content='',title='New Document'):
		self.newWindow = tk.Toplevel(self.root)
		self.newWindow.title = title
		self.app = DocumentEditor(self.newWindow,content)
		self.root.withdraw()

	def open(self):
		filename = filedialog.askopenfilename()
		if filename == '':
			return None
		f = open(filename,'r')
		i = f.read()
		f.close()
		self.new(i,filename.split('.')[0])

	def run(self):
		self.root.mainloop()

class Algo:
	def __init__(self,inp,e,mutex):
		##pdb.set_trace()
		self.inp = inp
		self.out = self.inp
		####### IMPORTANT
		mutex.acquire()
		correct = e.check(self.inp)
		mutex.release()
		if not correct:
			self.correct_word(e,mutex)

	def correct_word(self,e,mutex):
		mutex.acquire()
		self.candidates = e.suggest(self.inp)
		mutex.release()
		self.options = []
		for option in self.candidates:
			comparison = soundex(option) == soundex(self.inp)
			comparison = comparison and not bool([x for x in [' ','-'] if x in option])
			if comparison and option[0].islower():
				self.options = self.options + [option]

		init = False
		distances = None
		for option in self.options:
			count = self.options.count(option)
			done = option in distances[:,0] if init == True else False
			if count >= 1 and not done:
				dist = -1 * levenshtein_distance(self.inp,option)
				dist = dist + jaro_distance(self.inp,option)
				dist = dist * self.options.count(option)
				pair = np.array([[option,dist]])
				if init == False:
					distances = pair
					init = True
				else:
					distances = np.concatenate((distances,pair))
		if init == True:
			distances[:,1] = self.softmax(distances[:,1])
			self.out = distances[np.argmax(distances,axis=0)[1]][0]
		else:
			self.out = self.inp

	def softmax(self,arr):
		arr = exp(arr.astype(float))
		arr = arr / arr.sum()
		return arr

root = tk.Tk()

gui = MainMenu(root)

gui.run()
