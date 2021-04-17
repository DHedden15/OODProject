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
		self.fontsize = 20

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

		editMenu = tk.Menu(menubar)
		menubar.add_cascade(label="Edit",menu=editMenu)

		self.settingsFrame = tk.Frame(self.frame)
		self.settingsFrame.grid(row=0,column=0,sticky='E')
		self.fontnamevar = tk.StringVar(self.frame)
		self.fontnamevar.set(self.fontname)
		self.fontnamevar.trace('w',self.fontchange)
		self.fontMenu = tk.OptionMenu(self.settingsFrame,self.fontnamevar,*self.fonts)
		self.fontMenu.grid(row=0,column=0)

		sizes = range(1,101)
		self.fontsizevar = tk.StringVar(self.frame)
		self.fontsizevar.set(self.fontsize)
		self.sizeMenu = ttk.Combobox(self.settingsFrame,textvariable=self.fontsizevar)
		self.sizeMenu['values'] = [str(x) for x in range(1,101)]
		self.sizeMenu.current(self.fontsize-1)
		self.fontsizevar.trace('w', self.sizechange)
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
		self.root.bind("<Command-n>",self.new)
		fileMenu.add_command(label="Open", command=self.open,accelerator="Cmd+O")
		self.root.bind("<Command-o>",self.open)
		fileMenu.add_command(label="Save as...",command=self.save_as,accelerator="Cmd+Shift+S")
		self.root.bind("<Command-Shift-s>",self.save_as)
		fileMenu.add_command(label="Save...",command=self.save_as,accelerator="Cmd+S")
		self.root.bind("<Command-s>",self.save)
		fileMenu.add_command(label="Correct Spelling...",command=self.handle,accelerator="Cmd+G")
		self.root.bind("<Command-g>", self.handle)
		fileMenu.add_command(label="Main Menu",command=self.menu)

		editMenu.add_command(label="Bold",command=self.handle,accelerator="Cmd+B")
		self.root.bind("<Command-b>", self.bold)
		editMenu.add_command(label="Italic",command=self.handle,accelerator="Cmd+I")
		self.root.bind("<Command-i>", self.italic)
		editMenu.add_command(label="Underline",command=self.handle,accelerator="Cmd+U")
		self.root.bind("<Command-u>", self.underline)

		self.text = tk.Text(self.frame,borderwidth=3)
		self.text.insert("1.0",content)
		self.text.grid(row=2,column=0,sticky='NSEW')
		self.scrollbar.config(command=self.text.yview)
		self.text.config(undo=True,yscrollcommand=self.scrollbar.set)
		s = self.fontsizevar.get()
		fs = self.fontnamevar.get()
		self.text.tag_configure('format:|fontsize:'+s+"|fontname:"+fs,font=(fs,s))
		self.text.tag_add('format:|fontsize:'+s+"|fontname:"+fs,'1.0','end')

		self.text.bind('<period>',self.handle)
		self.text.bind('<Key>',self.update_title)
		self.frame.pack(fill='both',expand=True)
		self.frame.pack_propagate(0)

	def sizechange(self,*args):
		self.size(self)

	def fontchange(self,*args):
		self.font(self)

	def update_title(self,key):
		if key == 'update':
			self.root.title(self.title+" - Unsaved")
			return
		if (key.keycode not in [104,9,100,88,83,85,80,102,98]):
			i = self.text.get('1.0','end-1c')
			if i != self.corrected:
				self.root.title(self.title+" - Unsaved")

	def update_format(self,format,orig,fontsize,fontname,id=0):
		if id == 1: # For some reason this is the only way I can get the fonts to change.
			fontname = self.fontnamevar.get()
		self.text.tag_remove(orig,'sel.first','sel.last')
		tag = format+"|fontsize:"+fontsize+"|fontname:"+fontname
		self.text.tag_config(tag,font=(fontname,int(fontsize),format.replace('format:','')))
		self.text.tag_add(tag,'sel.first','sel.last')
		self.update_title(key='update')

	def bold(self,args=None):
		try:
			i = self.text.tag_names(f'{tk.SEL_LAST} - 1c')
			try:
				format = [x for x in i if 'format:' in x][0]
			except:
				format = 'format:|fontsize:'+self.fontsizevar.get()+'|fontname:'+self.fontnamevar.get()
			orig = format
			format = orig.split("|")[0]
			fontsize = orig.split("|")[1].replace("fontsize:","")
			fontname = orig.split("|")[2].replace("fontname:","")
			if 'bold' not in format:
				format = format.replace('normal ','')
				format += 'bold '
			else:
				format = format.replace('bold ','normal ')
			self.update_format(format,orig,fontsize,fontname)
		except:
			pass

	def italic(self,args=None):
		try:
			i = self.text.tag_names(f'{tk.SEL_LAST} - 1c')
			try:
				format = [x for x in i if 'format:' in x][0]
			except:
				format = 'format:|fontsize:'+self.fontsizevar.get()+'|fontname:'+self.fontnamevar.get()
			orig = format
			format = orig.split("|")[0]
			fontsize = orig.split("|")[1].replace("fontsize:","")
			fontname = orig.split("|")[2].replace("fontname:","")
			if 'italic' not in format:
				format += 'italic '
			else:
				format = format.replace('italic ','')
			self.update_format(format,orig,fontsize,fontname)
		except:
			pass

	def underline(self,args=None):
		try:
			i = self.text.tag_names(f'{tk.SEL_LAST} - 1c')
			try:
				format = [x for x in i if 'format:' in x][0]
			except:
				format = 'format:|fontsize:'+self.fontsizevar.get()+'|fontname:'+self.fontnamevar.get()
			orig = format
			format = orig.split("|")[0]
			fontsize = orig.split("|")[1].replace("fontsize:","")
			fontname = orig.split("|")[2].replace("fontname:","")
			if 'underline' not in format:
				format += 'underline '
			else:
				format = format.replace('underline ','')
			self.update_format(format,orig,fontsize,fontname)
		except:
			pass

	def size(self,*args):
		if self.fontsizevar.get() != self.fontsize:
			try:
				i = self.text.tag_names(f'{tk.SEL_LAST} - 1c')
				try:
					format = [x for x in i if 'format:' in x][0]
				except:
					format = 'format:|fontsize:'+self.fontsizevar.get()+'|fontname:'+self.fontnamevar.get()
				orig = format
				format = orig.split('|')[0]
				fontsize = self.fontsizevar.get()
				fontname = orig.split('|')[2].replace("fontname:","")
				self.update_format(format,orig,fontsize,fontname)
				self.fontsize = fontsize
			except:
				pass

	def font(self,*args):
		if (self.fontnamevar.get() != self.fontname):
			try:
				i = self.text.tag_names(f'{tk.SEL_LAST} - 1c')
				try:
					format = [x for x in i if 'format:' in x][0]
				except:
					format = 'format:|fontsize:'+self.fontsizevar.get()+'|fontname:'+self.fontnamevar.get()
				orig = format
				format = orig.split('|')[0]
				fontsize = orig.split('|')[1].replace("fontsize:","")
				fontname = ''
				self.update_format(format,orig,fontsize,font,1)
				self.fontname = fontname
			except:
				pass

	def close(self):
		if (messagebox.askquestion(title="Save", message="Save file?") != 'no'):
			self.save()
		self.menu()
		self.root.destroy()

	def menu(self):
		self.app = MainMenu(tk.Tk())

	def new(self,content='',title='New Document',filename=False,args=None):
		try:
			a = content.keycode
			content = ''
		except:
			content = content
		self.newWindow = tk.Tk()
		self.app = DocumentEditor(self.newWindow,content,title,filename)

	def open(self,args=None):
		filename = filedialog.askopenfilename()
		if filename == '':
			return None
		f = open(filename,'r')
		i = f.read()
		f.close()
		self.new(i,filename.split('.')[0].split('/')[-1:][0],filename=filename)

	def save(self,args=None):
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
