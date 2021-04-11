import tkinter as tk
from tkinter import filedialog

from threading import Thread

from gingerit.gingerit import GingerIt

class DocumentEditor:
	def __init__(self, root, content=''):
		self.root = root	
		self.frame = tk.Frame(self.root, height=500,width=500)
		self.frame.title = "New Document"

		self.top = tk.Frame(self.frame)
		self.bottom = tk.Frame(self.frame)
		self.top.pack(side=tk.TOP)
		self.bottom.pack(side=tk.BOTTOM,fill=tk.BOTH,expand=True)
		
		self.scrollbar = tk.Scrollbar(self.frame)
		self.scrollbar.pack(in_=self.bottom, side=tk.RIGHT, fill=tk.Y)
		
		self.menubutton = tk.Button(self.frame, text="Main Menu", command=self.menu)
		self.menubutton.pack(in_=self.top, side=tk.LEFT)
		
		self.savebutton = tk.Button(self.frame, text="Save", command=self.save)
		self.savebutton.pack(in_=self.top, side=tk.LEFT)

		self.correctbutton = tk.Button(self.frame, text="Correct", command=self.correct)
		self.correctbutton.pack(in_=self.top, side=tk.LEFT)
		
		self.text = tk.Text(self.frame, height=50, width=50)
		self.text.insert("1.0",content)
		self.text.pack(in_=self.bottom, side=tk.LEFT, fill=tk.BOTH, expand = tk.YES)	
		self.scrollbar.config(command=self.text.yview)
		self.text.config(yscrollcommand=self.scrollbar.set)
		
		self.text.bind('<period>',self.handle)
		self.frame.pack()
		self.frame.pack_propagate(0)
	
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
		print(i)
		i = i.split('.')
		i = ['.'.join(i[x:x+10]) for x in range(0, len(i), 10)]		
		for x in range(0,len(i)):
			a = i[x]
			if a.count(' ') > 9:
				a = a.split(' ')
				a = [' '.join(a[b:b+5]) for b in range(0, len(a), 5)]
				i[x] = a[0]
				i.insert(x+1,a[1])
		print(i)
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
		print(out)
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
	
	def new(self,content=''):
		self.newWindow = tk.Toplevel(self.root)
		self.app = DocumentEditor(self.newWindow,content)
		self.root.withdraw()

	def open(self):
		filename = filedialog.askopenfilename()
		if filename == '': 
			return None
		f = open(filename,'r')
		i = f.read()
		f.close()
		self.new(i)
	
	def run(self):
		self.root.mainloop()	
		
root = tk.Tk()

gui = MainMenu(root)

gui.run()
