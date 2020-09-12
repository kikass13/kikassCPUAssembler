#!/usr/bin/env python3

import os
import yaml

import tkinter as tk
from tkinter.font import Font
import tkinter.filedialog

from widgets.CodeTextWidget import CodeTextWidget
from assembler.AssemblerChecker import AssemblerChecker

######################################################################################################################

FONT_DEFAULT = None
FONT_LABEL = None
TABULATOR_INDENT_COUNT = 2



exportTypes = {
    0: ".bin",
    1: ".ascii",
    #2: ".elf",
    #3: ".hex",
}

class AssemblerGui(object):
    def __init__(self):
        ### create necessary utilities
        self.checker = AssemblerChecker()
        ### create the main window
        self.root = tk.Tk()
        self.root.title("My CPU Assembler")
        ### create stuff
        self.createViews()
        ### pack stuff
        self.drawViews()
    
    def createViews(self):
        ### creates special fonts for stuff
        FONT_DEFAULT = Font(family="Consolas", size=12)
        FONT_LABEL = Font(family="Consolas", size=12, weight="bold", underline=1)
        FONT_ADDRESS = Font(family="Consolas", size=12, slant="italic", underline=1)

        ### add code widget
        self.code = CodeTextWidget(self.root, width=50, height=30)
        self.code.text.configure(wrap="none")
        self.code.text.configure(font=FONT_DEFAULT)
        ### add on keypress event
        self.code.text.bind('<KeyRelease>', self.onCodeChanged)
        ### change tabulator key 
        self.code.text.bind("<Tab>", self.onTabPressed)
        self.code.text.bind("<Shift-KeyPress-Tab>", self.onShiftTabPressed)

        ### custom tags for colored text and stuff
        self.code.text.tag_configure("default", font=FONT_DEFAULT)
        self.code.text.tag_configure("label", font=FONT_LABEL, foreground="orange")
        self.code.text.tag_configure("address", font=FONT_ADDRESS, background="lightblue")
        self.code.text.tag_configure("symbol", font=FONT_DEFAULT, foreground="gray")
        self.code.text.tag_configure("comment", font=FONT_DEFAULT, foreground="green")

        ### add default code and add some special color things
        self.code.text.insert("1.0", "#0x0000\n", "address") 
        self.code.text.insert("2.0", "main:\n", "label") 
        ### focus
        self.code.text.focus_set()

        ### side panel
        self.sidepanel = tk.Frame(self.root)
        ### buttons
        self.buttonCpuInfo = tk.Button(self.sidepanel, text="CPU Info", width=15, height=5, command=self.onCpuInfoClicked)
        self.buttonLoad = tk.Button(self.sidepanel , text="Load", width=15, height=2, command=self.onLoadClicked)
        self.buttonSave = tk.Button(self.sidepanel , text="Save", width=15, height=2, command=self.onSaveClicked)
        self.buttonCheck = tk.Button(self.sidepanel , text="Check", width=15, height=5, command=self.onCheckClicked)
        self.buttonExport = tk.Button(self.sidepanel , text="Export", width=15, height=5, command=self.onExportClicked)

        ### create a variable to store options for the radiobuttons
        self.exportMode = tk.IntVar()
        self.exportMode.set(0)
        self.radiobuttons = []
        for v, t in exportTypes.items():
            rb = tk.Radiobutton(self.sidepanel, text=t, variable=self.exportMode, value=v, anchor="w")
            self.radiobuttons.append(rb) 

    def drawViews(self):
        tk.Frame(height=4, bd=4, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)
        self.code.pack(fill="both", expand=True, side=tk.LEFT)

        self.sidepanel.pack(fill="both", expand=True, side=tk.RIGHT)
        self.buttonCpuInfo.pack(padx=5, pady=5)
        tk.Frame(self.sidepanel, height=4, bd=4, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)
        self.buttonLoad.pack(padx=5, pady=5)
        self.buttonSave.pack(padx=5, pady=5)
        tk.Frame(self.sidepanel, height=4, bd=4, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)
        self.buttonCheck.pack(padx=5, pady=5)
        tk.Frame(self.sidepanel, height=4, bd=4, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)
        self.buttonExport.pack(padx=5, pady=5)
        for radioBtn in self.radiobuttons:
            radioBtn.pack(padx=5, pady=5)
        tk.Frame(self.sidepanel, height=4, bd=4, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)

    def run(self):
        self.root.mainloop()

    def onCpuInfoClicked(self):
        ### load instruction set info
        currentDir = os.path.dirname(__file__)
        filename = "instruction_set.yml"
        path = os.path.join(currentDir, filename)
        d = None
        with open(path, 'r') as stream:
            try:
                d = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                raise e
        if not d:
            return

        ### read data and interprete table entries
        instructions = d["instructions"]
        headers = list(instructions[0].keys()) ### grab first element and get our headers
        contents = [headers]
        rows = len(instructions)
        columns = len(headers)
        for i in instructions:
            l = []
            for k in headers:
                l.append(i[k])
            contents.append(l)

        showRows = 10 ### only so much rows will be shown before scrolling is necessary

        ### open popup window
        win = tk.Toplevel()
        win.wm_title("CPU Info")
        rowCount = 0
        ### contents
        ### see 
        ### https://stackoverflow.com/questions/43731784/tkinter-canvas-scrollbar-with-grid
        ### ...
        frame_main = tk.Frame(win)
        frame_main.grid(sticky='news')

        label1 = tk.Label(frame_main, text="Instruction Set")
        label1.grid(row=0, column=0, pady=(5, 0), sticky='nw')
        #label2 = tk.Label(frame_main, text="Label 2", fg="blue")
        #label2.grid(row=1, column=0, pady=(5, 0), sticky='nw')
        #label3 = tk.Label(frame_main, text="Label 3", fg="red")
        #label3.grid(row=3, column=0, pady=5, sticky='nw')

        # Create a frame for the canvas with non-zero row&column weights
        frame_canvas = tk.Frame(frame_main)
        frame_canvas.grid(row=2, column=0, pady=(5, 0), sticky='nw')
        frame_canvas.grid_rowconfigure(0, weight=1)
        frame_canvas.grid_columnconfigure(0, weight=1)
        # Set grid_propagate to False to allow 5-by-5 buttons resizing later
        frame_canvas.grid_propagate(False)

        # Add a canvas in that frame
        canvas = tk.Canvas(frame_canvas)
        canvas.grid(row=0, column=0, sticky="news")

        # Link a scrollbar to the canvas
        vsb = tk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        canvas.configure(yscrollcommand=vsb.set)

        # Create a frame to contain the buttons
        frame_buttons = tk.Frame(canvas, bg="blue")
        canvas.create_window((0, 0), window=frame_buttons, anchor='nw')

        # Add buttons to the frame
        contentEntries = [[tk.Entry() for j in range(columns)] for i in range(rows)]
        for i in range(0, rows):
            for j in range(0, columns):
                string = contents[i][j]
                if(i == 0): ### header line
                    contentEntries[i][j] = tk.Entry(frame_buttons, width=len(string)*3, fg='blue', font=('Arial',10,"bold")) 
                else:
                     contentEntries[i][j] = tk.Entry(frame_buttons, fg='black', font=('Arial',8)) 
                contentEntries[i][j].grid(row=i, column=j, sticky='news')
                contentEntries[i][j].insert(tk.END, string)
                contentEntries[i][j].configure(state='readonly')
        # Update buttons frames idle tasks to let tkinter calculate buttons sizes
        frame_buttons.update_idletasks()

        # Resize the canvas frame to show exactly n-by-n buttons and the scrollbar
        show_columns_width = sum([contentEntries[0][j].winfo_width() for j in range(columns)])
        show_columns_height = sum([contentEntries[i][0].winfo_height() for i in range(showRows)])
        frame_canvas.config(width=show_columns_width + vsb.winfo_width(),
                            height=show_columns_height)

        # Set the canvas scrolling region
        canvas.config(scrollregion=canvas.bbox("all"))
        ### other stuff
        b = tk.Button(frame_main, text="Close", bd=6, command=win.destroy)
        b.grid(row=10, column=0, sticky="we")


    def onLoadClicked(self):
        path = tkinter.filedialog.askopenfilename(initialdir="\%userprofile\%", filetypes =(("Assembler File", "*.asm"),("All Files","*.*")), title = "Choose a file.")
        if path:
            with open(path, 'r') as f:
                self.code.text.delete(1.0, tk.END)
                self.code.text.insert(1.0, f.read())
                self.refreshCode()
    def onSaveClicked(self):
        path = tkinter.filedialog.asksaveasfilename(defaultextension=".asm")
        if path:
            code = self.code.text.get(1.0, tk.END)
            with open(path, 'w') as f:
                f.write(code)
    def onCheckClicked(self):
        fullText = self.code.text.get("1.0", tk.END)
        success, errors, pseudocode = self.checker.checkCode(fullText)
        print(success)
        print(errors)
        print("================")
        print(pseudocode)
        ### do stuff with the errors and shit ...

    def onExportClicked(self):
        code = self.code.text.get("1.0", tk.END)
        success, errors, binary, lastWrittenByte = self.checker.assemble(code)
        print("Assembly Result:")
        print("  Success: %s" % success)
        print("  Errors: %s" % errors)
        print("  ROM: %s" % binary[:lastWrittenByte])

        exportMode = self.exportMode.get()
        extension = ""

        extension = exportTypes[exportMode]
        path = tkinter.filedialog.asksaveasfilename(defaultextension=extension)
        if path:
            if exportMode == 0:
                # Create bytearray from list of integers.
                byteArr = bytearray(binary)
                with open(path, "wb") as f:
                    f.write(byteArr)
                print("Binary file written [%s bytes]" % len(byteArr))
            elif exportMode == 1:
                ### ascii format export
                with open(path, 'w') as f:
                    for i, byte in enumerate(binary):
                        if i > 0 and i % 10 == 0:
                            f.write("\n")
                        f.write('%.2X ' % byte)
                print("Ascii file written [%s bytes]" % len(binary))
            #elif exportMode == 2:
            #    print("Export mode %s not supported" % exportMode)
            #else:
            #    print("Export mode %s not supported" % exportMode)

            


    def onTabPressed(self, event):
        self.code.text.insert(tk.INSERT, " " * TABULATOR_INDENT_COUNT)
        return 'break'
    def onShiftTabPressed(self, event):
        index = self.getCurrentIndex()
        deletedLine = self.deleteLine(index)
        spaces = self.getLineIndents(deletedLine)
        if spaces >= 2:
            deletedLine = deletedLine[2:]
        else:
            deletedLine = deletedLine.lstrip(" ")
        self.code.text.insert(index, deletedLine)
        #currentIndex = self.getCurrentIndex()
        #currentLine, currentChar = self.getIndexCoordinates(currentIndex)
        #targetCharIndex = int(currentChar) - TABULATOR_INDENT_COUNT
        #targetCharIndex = 0 if targetCharIndex < 0 else targetCharIndex
        #self.code.text.delete( "%s.%s" % (currentLine, targetCharIndex), tk.INSERT) ### indieces have to be reverted when deleting ... example (6.0, 6.2) -.-
        return 'break'

    ### iterate through teh code and yield each and every line one after another
    def codeLineIterator(self):
        lastLine = int(self.code.text.index("end").split(".")[0])
        for lineIndex in range(0, lastLine+1):
            ### defien inieces
            startIndex = "%s.0" % lineIndex
            endIndex = "%s.end" % lineIndex
            #### grab current
            line = self.code.text.get(startIndex, endIndex)
            yield startIndex, endIndex, line

    def refreshCode(self):
        ### go through all lines of our text widget and re-process each and every line
        ### so that things get marked and colored properly again
        for startIndex, endIndex, line in self.codeLineIterator():
            ### re-process line
            self.processLine(line, startIndex, endIndex)

    def onCodeChanged(self, args):
        #print(args)
        ## allow cahracters and some specific control keys to start the parsign of teh line (to color text and stuff)
        if args.keysym == "BackSpace" or args.keysym == "Delete" or args.keysym == "Return" or args.keysym == "Tab" or args.keysym == "Control_L" or args.char and args.char.isprintable():
            #print("onCodeChanged()")
            #print("compare", self.text.get(1.0, tk.END))
            ### go through current line and check for labels to change their color
            lineStartIndex, lineEndIndex = self.getCurrentLineIndieces()
            line = self.getLineTextBetween(lineStartIndex, lineEndIndex)
            lineType, lineKey = self.processLine(line, lineStartIndex, lineEndIndex)
            ### remember indent when going to next line
            if(args.keysym == "Return"):
                currentLine, currentChar = self.getIndexCoordinates(lineStartIndex)
                lastLine = self.getPreviousLineText()
                lastSpaces = self.getLineIndents(lastLine)
                self.code.text.insert(lineStartIndex, " " * lastSpaces)

    def processLine(self, line, lineStartIndex, lineEndIndex):
        lineType, lineKey = self.checker.checkLine(line)
        if lineType == AssemblerChecker.LINETYPE.LABEL:
            self.markLabelText(lineKey, lineStartIndex, lineEndIndex)
        elif lineType == AssemblerChecker.LINETYPE.ADDRESS:
            self.markAddressText(lineKey, lineStartIndex, lineEndIndex)
        elif lineType == AssemblerChecker.LINETYPE.SYMBOLDEF:
            self.markSymbolDefinitionText(lineKey, lineStartIndex, lineEndIndex)
        elif lineType == AssemblerChecker.LINETYPE.COMMENT:
            self.markCommentText(lineKey, lineStartIndex, lineEndIndex)
        ### check others ...
        else:
            self.unmarkText(line, lineStartIndex, lineEndIndex)
        return lineType, lineKey

    def markLabelText(self, name, indexStart, indexEnd):
        ### mark text given by indieces as label
        self.code.text.tag_add("label", indexStart, indexEnd)

    def markAddressText(self, name, indexStart, indexEnd):
        ### mark text given by indieces as label
        currentLine, currentChar = self.getIndexCoordinates(indexStart)
        lastLine, lastChar = self.getIndexCoordinates(indexEnd)
        pre1 = indexStart
        self.code.text.tag_add("address", indexStart, "%s.0" % str(int(currentLine)+1))
    def markSymbolDefinitionText(self, name, indexStart, indexEnd):
        self.code.text.tag_add("symbol", indexStart, indexEnd)
    def markCommentText(self, name, indexStart, indexEnd):
         self.code.text.tag_add("comment", indexStart, indexEnd)
    def unmarkText(self, text, indexStart, indexEnd):
        currentLine, currentChar = indexStart.split(".")
        #lastLine, lastChar = indexEnd.split(".")
        ### remove all tags and marks and return the text to normal
        for tag in self.code.text.tag_names():
            #self.code.text.tag_remove(tag, indexStart, indexEnd)
            self.code.text.tag_remove(tag, indexStart, "%s.0" % str(int(currentLine)+1))
    

    def getPreviousLineIndieces(self):
        start, end = self.getCurrentLineIndieces()
        return self.jumpIndex(start, -1, 0)

    def getCurrentLineIndieces(self):
        lineStartIndex = self.code.text.index("insert linestart")
        lineEndIndex = self.code.text.index("insert lineend")
        return lineStartIndex, lineEndIndex

    def getCurrentIndex(self):
        return self.code.text.index("insert")
    def getIndexCoordinates(self, index):
        return index.split(".") # currentLine, currentChar

    def getPreviousLineText(self):
        currentLine, currentChar = self.getIndexCoordinates(self.getCurrentIndex())
        prev = self.getPreviousLineIndieces()
        return self.getFullLineText(prev)
    def getCurrentLineText(self):
        start, end = self.getCurrentLineIndieces()
        return self.getLineTextBetween(start,end)
    def getFullLineText(self, index):
        line, char = self.getIndexCoordinates(index)
        return self.code.text.get("%s.0" % line, "%s.end" % line)
    def getLineTextBetween(self, start, end):
        return self.code.text.get(start, end)

    def getLineIndents(self, line):
        return len(line) - len(line.lstrip(" "))

    def jumpIndex(self, index, jumpy, jumpx):
        line, char = self.getIndexCoordinates(index)
        return "%s.%s" % ( int(line) + jumpy, int(char)+jumpx)

    def deleteCurrentLine(self):
        index = self.getCurrentIndex()
        deletedText = self.deleteLine(index)
        return deletedText
    def deleteLine(self, index):
        line, char = self.getIndexCoordinates(index)
        deletedText = self.getFullLineText(index)
        self.code.text.delete("%s.0" % line, "%s.end" % line)
        return deletedText

######################################################################################################################

def main():
    a = AssemblerGui()
    a.run()

if __name__ == "__main__":
    main()