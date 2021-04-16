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
from symspellpy import SymSpell, Verbosity
from spellchecker import SpellChecker
import pkg_resources
from copy import deepcopy

class DocumentEditor:
	def __init__(self, root, content=''):
		self.mutex = Lock()
		try:
			self.symspell = pickle.load(open('symspell.pkl','rb'))
		except:
			self.symspell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
			dictionary_path = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt")
			self.symspell.load_dictionary(dictionary_path, term_index=0, count_index=1)
			pickle.dump(self.symspell,open('symspell.pkl','wb'))
		self.e = enchant.Dict('en')
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
		fileMenu.add_command(label="Correct Spelling...",command=self.correct)
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

	def check_word(self,word,mutex,e):
		a = Algo(word,self.symspell,mutex,e)
		return a.out

	def parse(self,inp,returns,thread_n,mutex):
		e = enchant.Dict('en')
		final = inp[-1:]
		to_check = inp if final != '.' else inp[:-1]
		if to_check != '':
			#self.mutex.acquire()
			inp = self.check_word(to_check,mutex,e)
			#self.mutex.release()
		returns[thread_n] = inp

	def parse_chunk(self,chunk,returns,j):
		threads = []
		ret = {}
		mutex = Lock()
		for i in range(0,len(chunk)):
			t = Thread(target=self.parse,args=(chunk[i],ret,i,mutex))
			threads.append(t)
		for thread in threads:
			thread.start()
		for thread in threads:
			thread.join()

		out = list(ret.values())
		returns[j] = out

	def correct(self):
		original = self.text.get("1.0","end-1c")
		orig = deepcopy(original)
		o = deepcopy(orig)
		orig = orig.replace(self.corrected,'')
		i = deepcopy(orig)
		caps = [x for x in i.split(' ') if x != '']
		i = [x.lower() for x in caps]
		#i = [i[j:j+50] for j in range(0,len(i),50)]

		returns = {}
		'''for j in range(0,len(i)):
			t = Thread(target=self.parse_chunk,args=(i[j],returns,j))
			threads.append(t)
			print(f"Launching thread 1.{j}")
		for thread in threads:
			thread.start()
		for thread in threads:
			thread.join()'''


		threads = []
		mutex = Lock()
		for j in range(0,len(i)):
			threads.append(Thread(target=self.parse,args=(i[j],returns,j,mutex)))

		for thread in threads:
			thread.start()

		for thread in threads:
			thread.join()
		out = ''
		for x in range(0,len(i)):
			if (caps[x][0].isupper()):
				out += returns[x].capitalize() + " "
			else:
				out += returns[x] + ' '

		out = deepcopy(self.text.get('1.0','end-1c')).replace(orig,out)
		out = out.replace(' .','.')
		if out[-1:] == ' ':
			out = out[:-1]
		self.text.delete('1.0', tk.END)
		self.text.insert("1.0", out)
		self.corrected = out

	def handle(self,event):
		self.correct()

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
	def __init__(self,inp,symspell,mutex,e):
		self.inp = inp
		self.out = self.inp
		correct = e.check(self.inp)
		if not correct:
			self.correct_word(mutex,symspell,e)

	def correct_word(self,mutex,symspell,e):
		self.candidates = [x for x,_ in Word(self.inp).spellcheck()]
		e = e.suggest(self.inp)
		mutex.acquire()
		s = symspell.lookup(self.inp,Verbosity.ALL,max_edit_distance=2)
		mutex.release()
		self.candidates += e
		self.candidates += [x.term for x in s]

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
			if count >= 2 and not done:
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
			if len(np.unique(distances[:,1])) < len(distances[:,1]):
				# If it's a random choice...
				win = None
				freq = None
				for word in distances[:,0]:
					try:
						c_freq = symspell.words[str(word)]
					except:
						c_freq = 0
					if win == None:
						win = str(word)
						freq = c_freq
					else:
						if freq < c_freq:
							win = str(word)
							freq = c_freq
				self.out = win
			else:
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
