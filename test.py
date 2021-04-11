import tkinter as tk 
from tkinter import filedialog
import pickle

from gingerit.gingerit import GingerIt

class DocumentEditor:
	def __init__(self, master):
		self.master = master
		
		self.text = tk.Text(root, height=5, width=50)
		self.text.pack()

		self.savebutton = tk.Button(root, text="Save", command=self.save)
		self.savebutton.pack()

		self.openbutton = tk.Button(root, text="Open", command=self.open)
		self.openbutton.pack()

		self.correctbutton = tk.Button(root, text="Correct", command=self.correct)
		self.correctbutton.pack()

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

	def correct(self):
		i = self.text.get("1.0","end-1c")
		parser = GingerIt()
		result = parser.parse(i)['result']
		self.text.delete('1.0', tk.END)
		self.text.insert("1.0",result)
				
root = tk.Tk()
root.geometry("500x500")
root.title("PhonetikWrite")

gui = DocumentEditor(root)

tk.mainloop()
