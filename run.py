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
import tkinter.messagebox as messagebox

class DocumentEditor:
	def __init__(self, root, content='',title='New Document',filename=False):

		self.fonts = ["Times New Roman", "Arial", "Times", "Helvetica", "Courier", "Georgia"]

		self.filename = filename
		self.root = root
		self.title = title
		self.root.title(self.title)
		self.frame = tk.Frame(self.root, height=500,width=500)
		self.root.protocol("WM_DELETE_WINDOW", self.close)
		self.frame.grid_propagate(False)

		self.fontname = 'Times New Roman'
		self.bold_italic_underline = [0,0,0] # set to 1 [b,i,u] for the corresponding
		self.fontsize = 20
		self.font_objs = [Font(family=x,size=self.fontsize) for x in self.fonts]

		self.frame.grid_rowconfigure(0,weight=0)
		self.frame.grid_rowconfigure(1,weight=0)
		self.frame.grid_rowconfigure(2,weight=1)
		self.frame.grid_columnconfigure(0,weight=1)

		self.scrollbar = tk.Scrollbar(self.frame)
		self.scrollbar.grid(row=2,column=1,sticky='NSEW')

		menubar = tk.Menu(self.frame)
		self.root.config(menu=menubar)

		fileMenu = tk.Menu(menubar)
		menubar.add_cascade(label="File",menu=fileMenu)

		self.settingsFrame = tk.Frame(self.frame)
		self.settingsFrame.grid(row=0,column=0,sticky='E')
		self.fontvariable = tk.StringVar(self.frame)
		self.fontvariable.set(self.fontname)
		self.fontvariable.trace('w',self.fontchange)
		self.fontMenu = tk.OptionMenu(self.settingsFrame,self.fontvariable,*self.fonts)
		self.fontMenu.grid(row=0,column=0)

		sizes = range(1,101)
		self.fontsizevar = tk.StringVar(self.frame)
		self.fontsizevar.set(self.fontsize)
		self.fontsizevar.trace('w', self.sizechange)
		self.sizeMenu = ttk.Combobox(self.settingsFrame,textvariable=self.fontsizevar)
		self.sizeMenu['values'] = [str(x) for x in range(1,101)]
		self.sizeMenu.grid(row=0,column=1)

		self.bold_button = tk.Button(self.settingsFrame,text='B',command=self.bold)
		self.bold_button.grid(row=0,column=2)
		self.bold_button = tk.Button(self.settingsFrame,text='I',command=self.italic)
		self.bold_button.grid(row=0,column=3)
		self.bold_button = tk.Button(self.settingsFrame,text='U',command=self.underline)
		self.bold_button.grid(row=0,column=4)

		self.corrected = ''

		self.line = ttk.Separator(self.frame,orient=tk.HORIZONTAL)
		self.line.grid(row=1,column=0,sticky='EW')

		fileMenu.add_command(label="New", command=self.new,accelerator="Cmd+N")
		self.root.bind("<Command-n>",self.new_m)
		fileMenu.add_command(label="Open", command=self.open,accelerator="Cmd+O")
		self.root.bind("<Command-o>",self.open_m)
		fileMenu.add_command(label="Save as...",command=self.save_as,accelerator="Cmd+Shift+S")
		self.root.bind("<Command-Shift-s>",self.save_as)
		fileMenu.add_command(label="Save...",command=self.save_as,accelerator="Cmd+S")
		self.root.bind("<Command-s>",self.save)
		fileMenu.add_command(label="Correct Spelling...",command=self.handle,accelerator="Cmd+G")
		self.root.bind("<Command-g>", self.handle)
		fileMenu.add_command(label="Main Menu",command=self.menu)

		self.text = tk.Text(self.frame,borderwidth=3)
		self.text.insert("1.0",content)
		self.text.grid(row=2,column=0,sticky='NSEW')
		self.scrollbar.config(command=self.text.yview)
		self.text.config(font=(self.fontname,self.fontsize),undo=True,yscrollcommand=self.scrollbar.set)

		self.text.bind('<period>',self.handle)
		self.text.bind('<Key>',self.update_title)
		self.frame.pack(fill='both',expand=True)
		self.frame.pack_propagate(0)
		self.sizeMenu.current(self.fontsize)

	def sizechange(self,*args):
		self.fontsize = self.fontsizevar.get()
		self.text.config(font=(self.fontname,self.fontsize))

	def fontchange(self,*args):
		self.fontname = self.fontvariable.get()
		self.text.config(font=(self.fontname,self.fontsize))

	def update_title(self,key):
		if (key.keycode not in [104,9,100,88,83,85,80,102,98]):
			i = self.text.get('1.0','end-1c')
			if i != self.corrected:
				self.root.title(self.title+" - Unsaved")

	def bold(self):
		i = self.text.tag_names(f'{tk.SEL_LAST} - 1c')
		if ('bold' not in i):
			self.text.tag_configure('bold',font=(self.fontname,self.fontsize,'bold',))
			self.text.tag_add('bold','sel.first','sel.last')
		else:
			self.text.tag_remove('bold','sel.first','sel.last')

	def italic(self):
		i = self.text.tag_names(f'{tk.SEL_LAST} - 1c')
		if ('italic' not in i):
			self.text.tag_configure('italic',font=(self.fontname,self.fontsize,'italic'))
			self.text.tag_add('italic','sel.first','sel.last')
		else:
			self.text.tag_remove('italic','sel.first','sel.last')

	def underline(self):
		i = self.text.tag_names(f'{tk.SEL_LAST} - 1c')
		if ('underline' not in i):
			self.text.tag_configure('underline',font=(self.fontname,self.fontsize,'underline'))
			self.text.tag_add('underline','sel.first','sel.last')
		else:
			self.text.tag_remove('underline','sel.first','sel.last')

	def new_m(self,args):
		self.new()

	def open_m(self,args):
		self.open()

	def close(self):
		if (messagebox.askquestion(title="Save", message="Save file?") != 'no'):
			self.save()
		self.menu()
		self.root.destroy()

	def menu(self):
		self.app = MainMenu(tk.Tk())

	def new(self,content='',title='New Document',filename=False):
		self.newWindow = tk.Tk()
		self.app = DocumentEditor(self.newWindow,content,title,filename)

	def open(self):
		filename = filedialog.askopenfilename()
		if filename == '':
			return None
		f = open(filename,'r')
		i = f.read()
		f.close()
		self.new(i,filename.split('.')[0].split('/')[-1:][0],filename=filename)

	def save(self,args):
		if self.filename == False:
			self.save_as(self)
		else:
			i = self.text.get("1.0","end-1c")
			f = open(self.filename,'w')
			f.write(i)
			f.close()
			self.root.title(self.title)

	def save_as(self, args):
		i = self.text.get("1.0","end-1c")
		filename = filedialog.asksaveasfilename(initialdir = "./",title = "Select file",filetypes = (("PhonetikWrite files","*.pwf"),("all files","*.*")))
		if filename == '':
			return None
		f = open(filename,'w')
		f.write(i)
		f.close()
		self.filename = filename
		self.title = self.filename.split('.')[0].split('/')[-1:][0]
		self.root.title(self.title)

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
		pos = self.text.index(tk.INSERT)
		original = self.text.get("1.0","end-1c")
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

			#out = re.sub('[\n\t\s]+\.','.',out)#.rstrip()
			out = out.rstrip()
			current = self.text.index("current")
			self.text.mark_set("insert",float(current))
			self.text.delete('1.0', tk.END)
			self.text.insert("1.0", out)
			self.text.mark_set(tk.INSERT,pos)
			self.corrected = out

class MainMenu:
	def __init__(self,root):
		self.root = root
		self.root.title("PhonetikWrite")
		self.root.geometry('250x100')

		new_button = tk.Button(self.root, text="New Document", command=self.new)
		new_button.pack()

		open_button = tk.Button(self.root, text="Open Document", command=self.open)
		open_button.pack()

		menubar = tk.Menu(self.root)
		filemenu = tk.Menu(menubar, tearoff=0)
		filemenu.add_command(label="New", command=self.new,accelerator="Cmd+N")
		self.root.bind("<Command-n>",self.new_m)
		filemenu.add_command(label="Open", command=self.open,accelerator="Cmd+O")
		self.root.bind("<Command-o>",self.open_m)
		menubar.add_cascade(label='File',menu=filemenu)

		self.root.config(menu=menubar)

	def new_m(self,args):
		self.new()
	def open_m(self,args):
		self.open()

	def new(self,content='',title='New Document',filename=False):
		self.newWindow = tk.Tk()
		self.app = DocumentEditor(self.newWindow,content,title,filename)

	def open(self):
		filename = filedialog.askopenfilename()
		if filename == '':
			return None
		f = open(filename,'r')
		i = f.read()
		f.close()
		self.new(i,filename.split('.')[0].split('/')[-1:][0],filename=filename)

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
gui = MainMenu(tk.Tk())

gui.run()
