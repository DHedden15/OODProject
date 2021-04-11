import tkinter as tk
from tkinter import filedialog
import pickle

from multiprocessing.pool import ThreadPool

from gingerit.gingerit import GingerIt

class DocumentEditor:
	def __init__(self, root):
		self.root = root
		
		self.checked = ""

		self.scrollbar = tk.Scrollbar(root)
		self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		self.savebutton = tk.Button(root, text="Save", command=self.save)
		self.savebutton.pack()

		self.openbutton = tk.Button(root, text="Open", command=self.open)
		self.openbutton.pack()

		self.correctbutton = tk.Button(root, text="Correct", command=self.correct)
		self.correctbutton.pack()
		
		self.text = tk.Text(root, height=50, width=50)
		self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand = tk.YES)	
		self.scrollbar.config(command=self.text.yview)
		self.text.config(yscrollcommand=self.scrollbar.set)
	
		self.text.bind('<period>',self.handle)
	
	def save(self):
		i = self.text.get("1.0","end-1c")
		filename = filedialog.asksaveasfilename(initialdir = "./",title = "Select file",filetypes = (("PhonetikWrite files","*.pwf"),("all files","*.*")))
		f = open(filename,'w')
		f.write(i)
		f.close()	

	def open(self):
		filename = filedialog.askopenfilename()
		if filename == '':
			return None
		f = open(filename,'r')
		i = f.read()
		f.close()
		self.text.insert("1.0",i)

	def ginger_parse(self,parser,inp):
		return parser.parse(inp)['result']


	def correct(self):
		i = self.text.get("1.0","end-1c")
		i.replace(self.checked,'')
		i = [i[x:x+500] for x in range(0, len(i), 500)]
		out = ""
		parser = GingerIt()
		n = len(i)
		pool = ThreadPool(n)
		results = []
		for x in i:
			results.append(pool.apply_async(self.ginger_parse,args=(parser,x)))
		pool.close()
		pool.join()
		results = [r.get() for r in results]
		out = ''
		out.join(results)
		self.checked += out
		self.text.delete('1.0', tk.END)
		self.text.insert("1.0", self.checked)
	
	def handle(self,event):
		self.correct()	
		
	def run(self):
		self.root.mainloop()
	
root = tk.Tk()
root.geometry("500x500")
root.title("PhonetikWrite")

gui = DocumentEditor(root)

gui.run()
