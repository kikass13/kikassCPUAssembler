#!/usr/bin/env python3

import tkinter as tk
from tkinter.font import Font

from widgets.CodeTextWidget import CodeTextWidget
from assembler.AssemblerChecker import AssemblerChecker

######################################################################################################################

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
        self.code.text.tag_configure("label", font=FONT_LABEL, foreground="green")
        self.code.text.tag_configure("address", font=FONT_ADDRESS, background="lightblue")
        self.code.text.tag_configure("symbol", font=FONT_ADDRESS, foreground="gray")

        ### add default code and add some special color things
        self.code.text.insert("1.0", "#0x0000\n", "address") 
        self.code.text.insert("2.0", "main:\n", "label") 
        ### focus
        self.code.text.focus_set()

        ### buttons
        self.buttonCpuInfo = tk.Button(self.root, text="CPU Info", width=15, height=5, command=self.onCpuInfoClicked)
        self.buttonLoad = tk.Button(self.root, text="Load", width=15, height=2, command=self.onLoadClicked)
        self.buttonSave = tk.Button(self.root, text="Save", width=15, height=2, command=self.onSaveClicked)
        self.buttonCheck = tk.Button(self.root, text="Check", width=15, height=5, command=self.onCheckClicked)
        self.buttonExport = tk.Button(self.root, text="Export", width=15, height=5, command=self.onExportClicked)

        ### create a variable to store options for the radiobuttons
        self.exportMode = tk.IntVar()
        self.exportMode.set(1)
        self.radiobutton_1 = tk.Radiobutton(self.root, text=".elf", variable=self.exportMode, value=1, anchor="w")
        self.radiobutton_2 = tk.Radiobutton(self.root, text=".hex", variable=self.exportMode, value=2, anchor="w")

    def drawViews(self):

        tk.Frame(height=4, bd=4, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)
        self.code.pack(side="left", fill="both", expand=True)

        self.buttonCpuInfo.pack(padx=5, pady=5)
        tk.Frame(height=4, bd=4, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)
        self.buttonLoad.pack(padx=5, pady=5)
        self.buttonSave.pack(padx=5, pady=5)
        tk.Frame(height=4, bd=4, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)
        self.buttonCheck.pack(padx=5, pady=5)
        tk.Frame(height=4, bd=4, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)
        self.buttonExport.pack(padx=5, pady=5)
        self.radiobutton_1.pack(padx=5, pady=5)
        self.radiobutton_2.pack(padx=5, pady=5)
        tk.Frame(height=4, bd=4, relief=tk.SUNKEN).pack(fill=tk.X, anchor="s", padx=5, pady=5)

    def run(self):
        self.root.mainloop()

    def onCpuInfoClicked(self):
        pass
    def onLoadClicked(self):
        pass
    def onSaveClicked(self):
        pass
    def onCheckClicked(self):
        fullText = self.code.text.get("1.0", tk.END)
        success, results = self.checker.checkLines(fullText)
        ### do stuff with the errors and shit ...
    def onExportClicked(self):
        pass

    def onTabPressed(self, event):
        self.code.text.insert(tk.INSERT, " " * TABULATOR_INDENT_COUNT)
        return 'break'
    def onShiftTabPressed(self, event):
        index = self.getCurrentIndex()
        deletedLine = self.deleteLine(index)
        print(deletedLine)
        spaces = self.getLineIndents(deletedLine)
        print(spaces)
        if spaces >= 2:
            deletedLine = deletedLine[2:]
        else:
            deletedLine = deletedLine.lstrip(" ")
        print(deletedLine)
        self.code.text.insert(index, deletedLine)
        #currentIndex = self.getCurrentIndex()
        #currentLine, currentChar = self.getIndexCoordinates(currentIndex)
        #targetCharIndex = int(currentChar) - TABULATOR_INDENT_COUNT
        #targetCharIndex = 0 if targetCharIndex < 0 else targetCharIndex
        #self.code.text.delete( "%s.%s" % (currentLine, targetCharIndex), tk.INSERT) ### indieces have to be reverted when deleting ... example (6.0, 6.2) -.-
        return 'break'

    def onCodeChanged(self, args):
        #print(args)
        ## allow cahracters and some specific control keys to start the parsign of teh line (to color text and stuff)
        if args.keysym == "BackSpace" or args.keysym == "Delete" or args.keysym == "Return" or args.keysym == "Tab" or args.keysym == "Control_L" or args.char and args.char.isprintable():
            #print("onCodeChanged()")
            #print("compare", self.text.get(1.0, tk.END))
            ### go through current line and check for labels to change their color
            lineStartIndex, lineEndIndex = self.getCurrentLineIndieces()
            line = self.getLineTextBetween(lineStartIndex, lineEndIndex)
            lineType, lineKey = self.checker.checkLine(line)
            if lineType == AssemblerChecker.LINETYPE.LABEL:
                self.markLabelText(lineKey, lineStartIndex, lineEndIndex)
            elif lineType == AssemblerChecker.LINETYPE.ADDRESS:
                self.markAddressText(lineKey, lineStartIndex, lineEndIndex)
            elif lineType == AssemblerChecker.LINETYPE.SYMBOLDEF:
                self.markSymbolDefinitionText(lineKey, lineStartIndex, lineEndIndex)
            ### check others ...
            ###
            ### normal text
            else:
                self.unmarkText(line, lineStartIndex, lineEndIndex)

            ### remember indent when going to next line
            if(args.keysym == "Return"):
                currentLine, currentChar = self.getIndexCoordinates(lineStartIndex)
                lastLine = self.getPreviousLineText()
                lastSpaces = self.getLineIndents(lastLine)
                self.code.text.insert(lineStartIndex, " " * lastSpaces)

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
        ### mark text given by indieces as label
        self.code.text.tag_add("symbol", indexStart, indexEnd)

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