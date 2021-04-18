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
	def __init__(self, root,content='',title='New Document',filename=False,plist=None):

		self.fonts = ["Times New Roman", "Arial", "Times", "Helvetica", "Courier", "Georgia"]

		self.filename = filename
		self.plist = plist
		if plist == None and filename != False:
			self.plist = {'last_opened_filename':self.filename}
			self.save_plist()
		elif plist == None and type(filename) == 'str':
			self.plist['last_opened_filename'] = self.filename
			self.save_plist()

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
		self.italic_button = tk.Button(self.settingsFrame,text='I',command=self.italic)
		self.italic_button.grid(row=0,column=3)
		self.underline_button = tk.Button(self.settingsFrame,text='U',command=self.underline)
		self.underline_button.grid(row=0,column=4)

		self.left_button = tk.Button(self.settingsFrame,text='L',command=self.left)
		self.left_button.grid(row=1,column=0)
		self.center_button = tk.Button(self.settingsFrame,text='C',command=self.center)
		self.center_button.grid(row=1,column=1)
		self.right_button = tk.Button(self.settingsFrame,text='R',command=self.right)
		self.right_button.grid(row=1,column=2)

		self.corrected = ''

		self.line = ttk.Separator(self.frame,orient=tk.HORIZONTAL)
		self.line.grid(row=1,column=0,sticky='EW')

		fileMenu.add_command(label="New", command=self.new,accelerator="Cmd+N")
		self.root.bind("<Command-n>",self.new)
		fileMenu.add_command(label="Open", command=self.open,accelerator="Cmd+O")
		self.root.bind("<Command-o>",self.open)
		fileMenu.add_command(label="Open Last...", command=self.open_last,accelerator="Cmd+Shift+O")
		self.root.bind("<Command-Shift-O>",self.open_last)
		fileMenu.add_command(label="Save as...",command=self.save_as,accelerator="Cmd+Shift+S")
		self.root.bind("<Command-Shift-S>",self.save_as)
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
		self.root.bind("<Command-l>", self.gettext)

		self.text = tk.Text(self.frame,borderwidth=3)
		self.text.insert("1.0",content)
		self.text.grid(row=2,column=0,sticky='NSEW')
		self.scrollbar.config(command=self.text.yview)
		self.text.config(undo=True,yscrollcommand=self.scrollbar.set)
		s = self.fontsizevar.get()
		fs = self.fontnamevar.get()
		self.text.insert('1.0',' ')
		self.text.tag_configure('format:|fontsize:'+s+"|fontname:"+fs,font=(fs,s))
		self.text.tag_add('format:|fontsize:'+s+"|fontname:"+fs,'1.0','end')
		self.text.tag_add('justify:left', '1.0','end')

		self.text.bind('<period>',self.handle)
		self.text.bind('<KeyRelease>',self.update_title)
		self.text.bind('<ButtonRelease>',self.button_release)
		self.frame.pack(fill='both',expand=True)
		self.frame.pack_propagate(0)

	def save_plist(self):
		f = open('pkl.plist','wb')
		pickle.dump(self.plist,f)
		f.close()

	def sizechange(self,*args):
		self.size(self)

	def fontchange(self,*args):
		self.font(self)

	def button_release(self,event):
		if self.text.tag_ranges('sel') == ():
			self.updateFormatVars()
		elif self.text.compare("end-1c", "==", "1.0"):
			self.update_title()

	def updateFormatVars(self,event=None):
		tags = self.text.tag_names(tk.INSERT)
		for tag in tags:
			if tag != 'sel' and 'justify' not in tag:
				self.text.tag_add(tag,tk.INSERT,tk.INSERT + ' +1c')
				spl = tag.split("|")
				font = spl[2].replace('fontname:','')
				fontsize = spl[1].replace('fontsize:','')
				self.fontnamevar.set(font)
				self.fontsizevar.set(fontsize)
		pass

	def update_title(self,key):
		try:
			if key.keycode == 855638143 and self.text.compare("end-1c", "==", "1.0"):
				s = self.fontsizevar.get()
				fs = self.fontnamevar.get()
				self.text.insert('1.0',' ')
				self.text.tag_configure('format:|fontsize:'+s+"|fontname:"+fs,font=(fs,s))
				self.text.tag_add('format:|fontsize:'+s+"|fontname:"+fs,'1.0','end')
				self.text.tag_add('justify:left', '1.0','end')
				self.updateFormatVars()
			elif self.text.get('1.0') == ' ':
				self.text.delete('1.0')
				self.updateFormatVars()
			else:
				self.updateFormatVars()
			self.root.title(self.title+" - Unsaved")

		except:
			if key == 'update':
				self.root.title(self.title+" - Unsaved")
				return
			elif self.text.get('1.0','end-1c') != self.corrected:
					self.updateFormatVars()
			self.root.title(self.title+" - Unsaved")

	def left(self,args=None):
		i = self.text.tag_names(f'{tk.SEL_LAST} - 1c')
		try:
			justify = [x for x in i if "justify:" in x][0]
		except:
			justify = "justify:"
		orig = justify
		if "left" not in justify:
			self.text.tag_remove(orig,'sel.first','sel.last')
			self.text.tag_config('justify:left', justify="left")
			self.text.tag_add('justify:left', 'sel.first','sel.last')

	def right(self,args=None):
		i = self.text.tag_names(f'{tk.SEL_LAST} - 1c')
		try:
			justify = [x for x in i if "justify:" in x][0]
		except:
			justify = "justify:"
		orig = justify
		if "right" not in justify:
			self.text.tag_remove(orig,'sel.first','sel.last')
			self.text.tag_config('justify:right', justify="right")
			self.text.tag_add('justify:right', 'sel.first','sel.last')

	def center(self,args=None):
		i = self.text.tag_names(f'{tk.SEL_LAST} - 1c')
		try:
			justify = [x for x in i if "justify:" in x][0]
		except:
			justify = "justify:"
		orig = justify
		if "center" not in justify:
			self.text.tag_remove(orig,'sel.first','sel.last')
			self.text.tag_config('justify:center', justify="center")
			self.text.tag_add('justify:center', 'sel.first','sel.last')

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
		self.save_plist()
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
		self.plist['last_opened_filename'] = filename
		f = open(filename,'r')
		i = f.read()
		f.close()
		self.new(i,filename.split('.')[0].split('/')[-1:][0],filename=filename)

	def open_last(self,args=None):
		try:
			filename = self.plist['last_opened_filename']
			f = open(filename,'r')
			i = f.read()
			f.close()
			self.new(i,filename.split('.')[0].split('/')[-1:][0],filename=filename)
		except:
			self.open(self)

	def save(self,args=None):
		if self.filename == False:
			self.save_as(self)
		else:
			i = self.text.get("1.0","end-1c")
			f = open(self.filename,'w')
			f.write(i)
			f.close()
			self.plist['last_opened_filename'] = self.filename
			self.root.title(self.title)

	def save_as(self, args=None):
		i = self.text.get("1.0","end-1c")
		filename = filedialog.asksaveasfilename(initialdir = "./",title = "Select file",filetypes = (("PhonetikWrite files","*.pwf"),("all files","*.*")))
		if filename == '':
			return None
		f = open(filename,'w')
		f.write(i)
		f.close()
		self.plist['last_opened_filename'] = filename
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

	def gettext(self,*args):
		orig = deepcopy(self.text.get('1.0','end'))
		tags = [(x,self.text.tag_ranges(x)) for x in self.text.tag_names()]
		return tags

	def correct(self):
		pos = self.text.index(tk.INSERT)
		original = self.text.get("1.0","end")
		orig = deepcopy(original)
		tags = self.gettext()
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
			for tag in tags:
				if tag[0]!= 'sel':
					#tag[0] = name
					#tag[1] = tuple of indice pairs
					for i in range(0,len(tag[1])-1):
						self.text.tag_add(tag[0],tag[1][i],tag[1][i+1])
			self.text.mark_set(tk.INSERT,pos)
			self.corrected = out

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

if __name__ == '__main__':
	try:
		f = open('pkl.plist','rb')
		plist = pickle.load(f)
		f.close()
	except:
		plist = None
	gui = DocumentEditor(tk.Tk(),plist=plist)

	gui.run()
