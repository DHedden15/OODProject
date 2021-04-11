import tkinter as tk
from tkinter import filedialog, font
from tkinter.font import Font
from tkinter import ttk
import time
from threading import Thread

from gingerit.gingerit import GingerIt

class DocumentEditor:
	def __init__(self, root, content=''):
		self.root = root	
		self.frame = tk.Frame(self.root, height=500,width=500)
		self.frame.grid_propagate(False)

		self.font = Font(family='Times New Roman',size=12)

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

		sizes = range(0,100)
		self.fontsize = tk.IntVar(self.frame)
		self.fontsize.set(12)
		self.fontsize.trace('w', self.sizechange)
		self.sizeMenu = tk.OptionMenu(self.settingsFrame,self.fontsize,*sizes)
		self.sizeMenu.grid(row=0,column=1)
				

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

	def parse(self,inp,returns,thread_n):
		parser = GingerIt()	
		returns[thread_n] = parser.parse(inp)['result']

	def correct(self):
		i = self.text.get("1.0","end-1c")
		
		i = [x + '.' for x in i.split('.') if x != '']	
		
		returns = {}

		threads = []
		
		for j in range(0,len(i)):
			threads.append(Thread(target=self.parse,args=(i[j],returns,j)))
	
		for thread in threads:
			thread.start()

		for thread in threads:
			thread.join()		
		
		out = ''
		for i in range(0,len(i)):
			out += returns[i]
		out = out[:-1]
		self.text.delete('1.0', tk.END)
		self.text.insert("1.0", out)
	
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
		
root = tk.Tk()

gui = MainMenu(root)

gui.run()
