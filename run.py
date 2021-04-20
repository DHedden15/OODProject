import tkinter
import tkinter as tk
from tkinter import filedialog, font, LEFT, TOP, X, SUNKEN, W, BOTTOM, colorchooser
from tkinter.font import Font
from tkinter import ttk
import time
from threading import *
import pkg_resources
import pickle
from jellyfish import *
from textblob import Word
import enchant
from numpy import exp
import numpy as np
import pkg_resources
import re
from copy import deepcopy
from wordfreq import word_frequency
import math
import tkinter.messagebox as messagebox


class DocumentEditor:
    def __init__(self, root, content='', title='New Document', filename=False, plist=None, data=None):

        self.fonts = ["Times New Roman", "Arial", "Times", "Helvetica", "Courier", "Georgia"]
        self.items = []

        self.filename = filename
        self.plist = plist
        if plist == None and filename != False:
            self.plist = {'last_opened_filename': self.filename}
            self.save_plist()
        elif plist == None and type(filename) == 'str':
            self.plist['last_opened_filename'] = self.filename
            self.save_plist()

        self.root = root
        self.title = title
        self.root.title(self.title)
        self.frame = tk.Frame(self.root, height=500, width=500)
        self.items.append(self.frame)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.frame.grid_propagate(False)

        self.fontname = 'Times New Roman'
        self.fontsize = 20

        self.frame.grid_rowconfigure(0, weight=0)
        self.frame.grid_rowconfigure(1, weight=0)
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        self.scrollbar = tk.Scrollbar(self.frame)
        self.scrollbar.grid(row=2, column=1, sticky='NSEW')
        self.items.append(self.scrollbar)

        menubar = tk.Menu(self.frame)
        self.root.config(menu=menubar)

        fileMenu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=fileMenu)

        editMenu = tk.Menu(menubar)
        menubar.add_cascade(label="Edit", menu=editMenu)

        # **** Toolbar **** #
        self.toolbar = tk.Frame(self.root)# that terkwaz now in a function
        self.items.append(self.toolbar)

        #boldImg = tkinter.PhotoImage(file='./resources/bold.png')
        #boldImgResize = boldImg.subsample(27, 27) image=boldImgResize bg='black'
        self.boldBtn = tk.Button(self.toolbar, text='Bold', command=self.bold)
        self.boldBtn.pack(side=LEFT, padx=2, pady=2)
        self.items.append(self.boldBtn)

        self.italicBtn = tk.Button(self.toolbar, text="Italic", command=self.italic)
        self.italicBtn.pack(side=LEFT, padx=2, pady=2)
        self.items.append(self.italicBtn)

        self.underlineBtn = tk.Button(self.toolbar, text="Underline", command=self.underline)
        self.underlineBtn.pack(side=LEFT, padx=2, pady=2)
        self.items.append(self.underlineBtn)

        self.strikeBtn = tk.Button(self.toolbar, text="Strike")
        self.strikeBtn.pack(side=LEFT, padx=2, pady=2)
        self.items.append(self.strikeBtn)

        self.textColorBtn = tk.Button(self.toolbar, text="Text Color", ) #command=textColor
        self.textColorBtn.pack(side=LEFT, padx=2, pady=2)
        self.items.append(self.textColorBtn)

        self.undoBtn = tk.Button(self.toolbar, text="Undo", ) #command=edit_undo
        self.undoBtn.pack(side=LEFT, padx=2, pady=2)
        self.items.append(self.undoBtn)

        self.redoBtn = tk.Button(self.toolbar, text="Redo", ) #command=edit_redo
        self.redoBtn.pack(side=LEFT, padx=2, pady=2)
        self.items.append(self.redoBtn)

        # **** Status Bar **** #
        self.status = tk.Label(self.root, text="TBD", bd=1, relief=SUNKEN, anchor=W)
        self.status.pack(side=BOTTOM, fill=X)
        self.items.append(self.status)

        self.toolbar.pack(side=TOP, fill=X)

        self.settingsFrame = tk.Frame(self.frame)
        self.items.append(self.settingsFrame)
        self.settingsFrame.grid(row=0, column=0, sticky='E')
        self.fontnamevar = tk.StringVar(self.frame)
        self.fontnamevar.set(self.fontname)
        self.fontnamevar.trace('w', self.fontchange)
        self.fontMenu = tk.OptionMenu(self.settingsFrame, self.fontnamevar, *self.fonts)
        self.fontMenu.grid(row=0, column=0)
        self.items.append(self.fontMenu)

        sizes = range(1, 101)
        self.fontsizevar = tk.StringVar(self.frame)
        self.fontsizevar.set(self.fontsize)
        self.sizeMenu = ttk.Combobox(self.settingsFrame, textvariable=self.fontsizevar)
        self.items.append(self.sizeMenu)
        self.sizeMenu['values'] = [str(x) for x in range(1, 101)]
        self.sizeMenu.current(self.fontsize - 1)
        self.fontsizevar.trace('w', self.sizechange)
        self.sizeMenu.grid(row=0, column=1)

        self.left_button = tk.Button(self.settingsFrame, text='L', command=self.left)
        self.items.append(self.left_button)
        self.left_button.grid(row=1, column=0)
        self.center_button = tk.Button(self.settingsFrame, text='C', command=self.center)
        self.center_button.grid(row=1, column=1)
        self.items.append(self.center_button)
        self.right_button = tk.Button(self.settingsFrame, text='R', command=self.right)
        self.right_button.grid(row=1, column=2)
        self.items.append(self.right_button)

        self.corrected = ''

        self.line = ttk.Separator(self.frame, orient=tk.HORIZONTAL)
        self.line.grid(row=1, column=0, sticky='EW')

        fileMenu.add_command(label="New", command=self.new, accelerator="Cmd+N")
        self.root.bind("<Command-n>", self.new)
        fileMenu.add_command(label="Open", command=self.open, accelerator="Cmd+O")
        self.root.bind("<Command-o>", self.open)
        fileMenu.add_command(label="Open Last...", command=self.open_last, accelerator="Cmd+Shift+O")
        self.root.bind("<Command-Shift-O>", self.open_last)
        fileMenu.add_command(label="Save as...", command=self.save_as, accelerator="Cmd+Shift+S")
        self.root.bind("<Command-Shift-S>", self.save_as)
        fileMenu.add_command(label="Save...", command=self.save_as, accelerator="Cmd+S")
        self.root.bind("<Command-s>", self.save)
        fileMenu.add_command(label="Correct Spelling...", command=self.handle, accelerator="Cmd+G")
        self.root.bind("<Command-g>", self.handle)
        fileMenu.add_command(label="Main Menu", command=self.menu)

        editMenu.add_command(label="Bold", command=self.handle, accelerator="Cmd+B")
        self.root.bind("<Command-b>", self.bold)
        editMenu.add_command(label="Italic", command=self.handle, accelerator="Cmd+I")
        self.root.bind("<Command-i>", self.italic)
        editMenu.add_command(label="Underline", command=self.handle, accelerator="Cmd+U")
        self.root.bind("<Command-u>", self.underline)
        editMenu.add_command(label="Turquoise...", command=self.turquoise, accelerator="Cmd+T")
        self.root.bind("<Command-u>", self.turquoise)

        self.text = tk.Text(self.frame, borderwidth=3)
        self.items.append(self.text)
        self.text.insert("1.0", content)
        self.text.grid(row=2, column=0, sticky='NSEW')
        self.scrollbar.config(command=self.text.yview)
        self.text.config(undo=True, yscrollcommand=self.scrollbar.set)
        s = self.fontsizevar.get()
        fs = self.fontnamevar.get()
        if data == None:
            self.text.insert('1.0', ' ')
            self.text.tag_configure('format:|fontsize:' + s + "|fontname:" + fs, font=(fs, s))
            self.text.tag_add('format:|fontsize:' + s + "|fontname:" + fs, '1.0', 'end')
            self.text.tag_add('justify:left', '1.0', 'end')
        else:
            self.text.insert('1.0', content)
            for tag in data.keys():
                if tag != 'text' and tag != 'sel' and 'justify' not in tag:
                    for i in range(0, len(data[tag]) - 1):
                        style = tag.split("|")
                        format = style[0].replace("format:", '')
                        fontsize = style[1].replace("fontsize:", '')
                        fontname = style[2].replace("fontname:", '')
                        self.text.tag_config(tag, font=(fontname, int(fontsize), format))
                        self.text.tag_add(tag, data[tag][i], data[tag][i + 1])
                if 'justify' in tag:
                    for i in range(0, len(data[tag]) - 1):
                        justify = tag.replace("justify:", '')
                        self.text.tag_config(tag, justify=justify)
                        self.text.tag_add(tag, data[tag][i], data[tag][i + 1])

        self.text.bind('<period>', self.handle)
        self.text.bind('<KeyRelease>', self.update_title)
        self.text.bind('<ButtonRelease>', self.button_release)
        self.frame.pack(fill='both', expand=True)
        self.frame.pack_propagate(0)

    def turquoise(self, *args):
        for item in self.items:
            item.configure(background='medium turquoise')

    def save_plist(self):
        f = open('./resources/pkl.plist', 'wb')
        pickle.dump(self.plist, f)
        f.close()

    def sizechange(self, *args):
        self.size(self)

    def fontchange(self, *args):
        self.font(self)

    def button_release(self, event):
        if self.text.tag_ranges('sel') == ():
            self.updateFormatVars()
        elif self.text.compare("end-1c", "==", "1.0"):
            self.update_title()

    def updateFormatVars(self, event=None):
        tags = self.text.tag_names(tk.INSERT)
        for tag in tags:
            if tag != 'sel' and 'justify' not in tag:
                self.text.tag_add(tag, tk.INSERT, tk.INSERT + ' +1c')
                spl = tag.split("|")
                font = spl[2].replace('fontname:', '')
                fontsize = spl[1].replace('fontsize:', '')
                self.fontnamevar.set(font)
                self.fontsizevar.set(fontsize)
        pass

    def update_title(self, key):
        try:
            if key.keycode == 855638143 and self.text.compare("end-1c", "==", "1.0"):
                s = self.fontsizevar.get()
                fs = self.fontnamevar.get()
                self.text.insert('1.0', ' ')
                self.text.tag_configure('format:|fontsize:' + s + "|fontname:" + fs, font=(fs, s))
                self.text.tag_add('format:|fontsize:' + s + "|fontname:" + fs, '1.0', 'end')
                self.text.tag_add('justify:left', '1.0', 'end')
                self.updateFormatVars()
            elif self.text.get('1.0') == ' ':
                self.text.delete('1.0')
                self.updateFormatVars()
            else:
                self.updateFormatVars()
            self.root.title(self.title + " - Unsaved")

        except:
            if key == 'update':
                self.root.title(self.title + " - Unsaved")
                return
            elif self.text.get('1.0', 'end-1c') != self.corrected:
                self.updateFormatVars()
            self.root.title(self.title + " - Unsaved")

    def left(self, args=None):
        i = self.text.tag_names(f'{tk.SEL_LAST} - 1c')
        try:
            justify = [x for x in i if "justify:" in x][0]
        except:
            justify = "justify:"
        orig = justify
        if "left" not in justify:
            self.text.tag_remove(orig, 'sel.first', 'sel.last')
            self.text.tag_config('justify:left', justify="left")
            self.text.tag_add('justify:left', 'sel.first', 'sel.last')

    def right(self, args=None):
        i = self.text.tag_names(f'{tk.SEL_LAST} - 1c')
        try:
            justify = [x for x in i if "justify:" in x][0]
        except:
            justify = "justify:"
        orig = justify
        if "right" not in justify:
            self.text.tag_remove(orig, 'sel.first', 'sel.last')
            self.text.tag_config('justify:right', justify="right")
            self.text.tag_add('justify:right', 'sel.first', 'sel.last')

    def center(self, args=None):
        i = self.text.tag_names(f'{tk.SEL_LAST} - 1c')
        try:
            justify = [x for x in i if "justify:" in x][0]
        except:
            justify = "justify:"
        orig = justify
        if "center" not in justify:
            self.text.tag_remove(orig, 'sel.first', 'sel.last')
            self.text.tag_config('justify:center', justify="center")
            self.text.tag_add('justify:center', 'sel.first', 'sel.last')

    def update_format(self, format, orig, fontsize, fontname, id=0):
        if id == 1:  # For some reason this is the only way I can get the fonts to change.
            fontname = self.fontnamevar.get()
        self.text.tag_remove(orig, 'sel.first', 'sel.last')
        tag = format + "|fontsize:" + fontsize + "|fontname:" + fontname
        self.text.tag_config(tag, font=(fontname, int(fontsize), format.replace('format:', '')))
        self.text.tag_add(tag, 'sel.first', 'sel.last')
        self.update_title(key='update')

    def bold(self, args=None):
        try:
            i = self.text.tag_names(f'{tk.SEL_LAST} - 1c')
            try:
                format = [x for x in i if 'format:' in x][0]
            except:
                format = 'format:|fontsize:' + self.fontsizevar.get() + '|fontname:' + self.fontnamevar.get()
            orig = format
            format = orig.split("|")[0]
            fontsize = orig.split("|")[1].replace("fontsize:", "")
            fontname = orig.split("|")[2].replace("fontname:", "")
            if 'bold' not in format:
                format = format.replace('normal ', '')
                format += 'bold '
            else:
                format = format.replace('bold ', 'normal ')
            self.update_format(format, orig, fontsize, fontname)
        except:
            pass

    def italic(self, args=None):
        try:
            i = self.text.tag_names(f'{tk.SEL_LAST} - 1c')
            try:
                format = [x for x in i if 'format:' in x][0]
            except:
                format = 'format:|fontsize:' + self.fontsizevar.get() + '|fontname:' + self.fontnamevar.get()
            orig = format
            format = orig.split("|")[0]
            fontsize = orig.split("|")[1].replace("fontsize:", "")
            fontname = orig.split("|")[2].replace("fontname:", "")
            if 'italic' not in format:
                format += 'italic '
            else:
                format = format.replace('italic ', '')
            self.update_format(format, orig, fontsize, fontname)
        except:
            pass

    def underline(self, args=None):
        try:
            i = self.text.tag_names(f'{tk.SEL_LAST} - 1c')
            try:
                format = [x for x in i if 'format:' in x][0]
            except:
                format = 'format:|fontsize:' + self.fontsizevar.get() + '|fontname:' + self.fontnamevar.get()
            orig = format
            format = orig.split("|")[0]
            fontsize = orig.split("|")[1].replace("fontsize:", "")
            fontname = orig.split("|")[2].replace("fontname:", "")
            if 'underline' not in format:
                format += 'underline '
            else:
                format = format.replace('underline ', '')
            self.update_format(format, orig, fontsize, fontname)
        except:
            pass

    def textColor(self, *args):
        my_color = colorchooser.askcolor()
        color_font = font.Font(self.text, self.frame.cget("color"))
        self.frame.tag_configure("color", font=color_font, foreground=my_color)
        current_tags = self.frame.tag_names("sel.first")
        if "color" in current_tags:
            self.frame.tag_remove("color", "sel.first")
        else:
            self.frame.tag_add("color", "sel.first")

    def size(self, *args):
        if self.fontsizevar.get() != self.fontsize:
            try:
                i = self.text.tag_names(f'{tk.SEL_LAST} - 1c')
                try:
                    format = [x for x in i if 'format:' in x][0]
                except:
                    format = 'format:|fontsize:' + self.fontsizevar.get() + '|fontname:' + self.fontnamevar.get()
                orig = format
                format = orig.split('|')[0]
                fontsize = self.fontsizevar.get()
                fontname = orig.split('|')[2].replace("fontname:", "")
                self.update_format(format, orig, fontsize, fontname)
                self.fontsize = fontsize
            except:
                pass

    def font(self, *args):
        if (self.fontnamevar.get() != self.fontname):
            try:
                i = self.text.tag_names(f'{tk.SEL_LAST} - 1c')
                try:
                    format = [x for x in i if 'format:' in x][0]
                except:
                    format = 'format:|fontsize:' + self.fontsizevar.get() + '|fontname:' + self.fontnamevar.get()
                orig = format
                format = orig.split('|')[0]
                fontsize = orig.split('|')[1].replace("fontsize:", "")
                fontname = ''
                self.update_format(format, orig, fontsize, font, 1)
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

    def new(self, content='', title='New Document', filename=False, args=None, data=None):
        try:
            a = content.keycode
            content = ''
        except:
            content = content
        self.newWindow = tk.Tk()
        self.app = DocumentEditor(self.newWindow, content, title, filename, data=data)

    def open(self, args=None):
        filename = filedialog.askopenfilename(filetypes=[("PhonetikWrite files", "*.pwf")])
        if filename == '':
            return None
        self.plist['last_opened_filename'] = filename
        try:
            f = open(filename, 'rb')
            data = pickle.load(f)
            f.close()
            i = data['text']
            self.new(i, filename.split('.')[0].split('/')[-1:][0], filename=filename, data=data)
        except:
            messagebox.showerror("File Opening Error", "The selected file has been corrupted.", icon='error')

    def open_last(self, args=None):
        try:
            filename = self.plist['last_opened_filename']
            f = open(filename, 'rb')
            data = pickle.load(f)
            f.close()
            i = data['text']
            self.new(i, filename.split('.')[0].split('/')[-1:][0], filename=filename, data=data)
        except:
            self.open(self)

    def save(self, args=None):
        if self.filename == False:
            self.save_as(self)
        else:
            i = self.text.get("1.0", "end-1c")
            i = ''.join([x for x in i])
            tags = [tag for tag in self.gettext()]
            data = {}
            for tag in tags:
                name = tag[0]
                indices_tcl = tag[1]
                indices_str = []
                for index in indices_tcl:
                    indices_str.append(str(index))
                data[name] = indices_str
            data['text'] = i
            f = open(self.filename, 'wb')
            pickle.dump(data, f)
            f.close()
            self.plist['last_opened_filename'] = self.filename
            self.root.title(self.title)

    def save_as(self, args=None):
        i = self.text.get("1.0", "end-1c")
        i = ''.join([x for x in i])
        tags = [tag for tag in self.gettext()]
        data = {}
        for tag in tags:
            name = tag[0]
            indices_tcl = tag[1]
            indices_str = []
            for index in indices_tcl:
                indices_str.append(str(index))
            data[name] = indices_str
        filename = filedialog.asksaveasfilename(initialdir="./", title="Select file",
                                                filetypes=[("PhonetikWrite files", "*.pwf")])
        if filename == '':
            return None
        data['text'] = i
        f = open(filename, 'wb')
        pickle.dump(data, f)
        f.close()
        self.plist['last_opened_filename'] = filename
        self.filename = filename
        self.title = self.filename.split('.')[0].split('/')[-1:][0]
        self.root.title(self.title)

    def parse_chunk(self, i, returns, j, mutex):
        # Chunk is array of 100 word strings.
        chunk = i[j]
        mutex.acquire()
        e = enchant.Dict('en')
        mutex.release()
        out = []
        for i in range(0, len(chunk)):
            if chunk[i] != '':
                a = Algo(chunk[i], e, mutex)
                out.append(a.out)
        returns[j] = out

    def handle(self, event=None):
        current = self.text.index(tk.CURRENT)
        self.correct()

    def whitespace(self, inp):
        whitespace = []
        for word in inp:
            try:
                punct = '[^a-zA-Z\s]'
                search = re.search('(' + punct + '*\s+' + punct + '*|' + punct + '+)', word)
                index = search.start()
                spaces = word[index:search.end()]
                whitespace.append([index, spaces])
            except:
                whitespace.append([False, False])
        return whitespace

    def gettext(self, *args):
        orig = deepcopy(self.text.get('1.0', 'end'))
        tags = [(x, self.text.tag_ranges(x)) for x in self.text.tag_names()]
        return tags

    def correct(self):
        pos = self.text.index(tk.INSERT)
        original = self.text.get("1.0", "end")
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
            for j in range(0, len(i)):
                t = Thread(target=self.parse_chunk, args=(i, returns, j, mutex))
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
            for i in range(0, len(words)):
                # or if first word
                isFirst = True if i == 0 or '.' in caps[i - 1] else False
                if isFirst:
                    w = words[i][0].upper() + words[i][1:]
                    if whitespace[i][0] != False:
                        if whitespace[i][0] != 0:
                            w += whitespace[i][1]
                        else:
                            w = whitespace[i][1] + w
                    out += w + " "
                elif caps[i].lower() != caps[i]:
                    out += caps[i] + " "
                else:
                    w = words[i]
                    if whitespace[i][0] != False:
                        if whitespace[i][0] != 0:
                            if whitespace[i][0] != 0:
                                w += whitespace[i][1]
                            else:
                                w = w[1:] + whitespace[i][1]
                        else:
                            w = whitespace[i][1] + w
                    out += w + " "
            out = out.rstrip()
            self.text.delete('1.0', tk.END)
            self.text.insert("1.0", out)
            for tag in tags:
                if tag[0] != 'sel':
                    # tag[0] = name
                    # tag[1] = tuple of indice pairs
                    for i in range(0, len(tag[1]) - 1):
                        self.text.tag_add(tag[0], tag[1][i], tag[1][i + 1])
            diff = len(out) - len(orig)
            self.text.mark_set(tk.INSERT + str(diff) + 'c', pos)
            self.corrected = out

    def run(self):
        self.root.mainloop()


class Algo:
    def __init__(self, inp, e, mutex):
        ##pdb.set_trace()
        self.inp = inp
        self.out = self.inp
        ####### IMPORTANT
        mutex.acquire()
        correct = e.check(self.inp)
        mutex.release()
        if not correct:
            self.correct_word(e, mutex)

    def correct_word(self, e, mutex):
        mutex.acquire()
        self.candidates = e.suggest(self.inp)
        mutex.release()
        self.options = []
        for option in self.candidates:
            comparison = soundex(option) == soundex(self.inp)
            comparison = comparison and not bool([x for x in [' ', '-'] if x in option])
            if comparison and option[0].islower():
                self.options = self.options + [option]

        init = False
        distances = None
        for option in self.options:
            count = self.options.count(option)
            done = option in distances[:, 0] if init == True else False
            if count >= 1 and not done:
                dist = -1 * levenshtein_distance(self.inp, option)
                dist = dist + jaro_distance(self.inp, option)
                dist = dist * self.options.count(option)
                pair = np.array([[option, dist]])
                if init == False:
                    distances = pair
                    init = True
                else:
                    distances = np.concatenate((distances, pair))
        if init == True:
            distances[:, 1] = self.softmax(distances[:, 1])
            self.out = distances[np.argmax(distances, axis=0)[1]][0]
        else:
            self.out = self.inp

    def softmax(self, arr):
        arr = exp(arr.astype(float))
        arr = arr / arr.sum()
        return arr


if __name__ == '__main__':
    try:
        f = open('./resources/pkl.plist', 'rb')
        plist = pickle.load(f)
        f.close()
    except:
        plist = None
    root = tk.Tk()
    img = tk.Image('photo', file='./resources/logo.png')
    root.tk.call('wm', 'iconphoto', root._w, img)
    gui = DocumentEditor(root, plist=plist)
    # gui.call('wm','iconphoto', root._w, img)
    gui.run()
