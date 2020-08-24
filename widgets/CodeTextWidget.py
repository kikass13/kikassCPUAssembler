#!/usr/bin/env python3

import tkinter as tk

class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2,y,anchor="nw", text=linenum)
            i = self.textwidget.index("%s+1line" % i)


class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, *args):
        # let the actual widget perform the requested action
        cmd = (self._orig,) + args
        result = self.tk.call(cmd)

        # generate an event if something was added or deleted,
        # or the cursor position changed
        if (args[0] in ("insert", "replace", "delete") or 
            args[0:3] == ("mark", "set", "insert") or
            args[0:2] == ("xview", "moveto") or
            args[0:2] == ("xview", "scroll") or
            args[0:2] == ("yview", "moveto") or
            args[0:2] == ("yview", "scroll")
        ):
            self.event_generate("<<Change>>", when="tail")

        # return what the actual widget returned
        return result        


class CodeTextWidget(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        width = kwargs.get("width", 30)
        height = kwargs.get("height", 20)
        self.text = CustomText(self, width=width, height=height)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.hsb = tk.Scrollbar(self, orient="horizontal", command=self.text.xview)

        self.text.configure(yscrollcommand=self.vsb.set)
        self.text.configure(xscrollcommand=self.hsb.set)
        self.linenumbers = TextLineNumbers(self, width=30)
        self.linenumbers.attach(self.text)

        self.linenumbers.pack(side="left", fill="y")
        self.vsb.pack(side="right", fill="y")
        self.hsb.pack(side="bottom", fill="x")
        self.text.pack(side="left", fill="both", expand=True)

        ### overwrite paste and copy events because these raise exceptions with
        ### empty selected ctrl+c or non selected text ctrl+v
        self.text.bind("<<Paste>>", self.paste)
        self.text.bind("<<Copy>>", self.copy)
        ### also initialize our clipboard with something so that its not empty
        self.clipboard_append("")

        ### chaneg events for line scrollbar
        self.text.bind("<<Change>>", self._on_change)
        self.text.bind("<Configure>", self._on_change)
        self.text.bind("<<Change>>", self._on_change)

    def _on_change(self, event):
        self.linenumbers.redraw()

    def copy(self, event):
        ### reinitialize our clipboard with somethign non zero
        self.clipboard_clear()
        self.clipboard_append("")
        ### check what is selected to perform the copy
        if self.text.tag_ranges("sel"):
            code = self.text.get("sel.first", "sel.last")
            self.clipboard_append(code)
        return "break"

    def paste(self, event):
        pasteText = self.clipboard_get()
        if pasteText and self.text.tag_ranges("sel"):
            code = self.text.delete("sel.first", "sel.last")
        self.text.insert(tk.INSERT, pasteText)
        return "break"

def testCallback(event):
    print("Something happened:\n%s" % event)

if __name__ == "__main__":
    root = tk.Tk()

    code = CodeTextWidget(root)
    code.text.bind("<KeyRelease>", testCallback)

    code.text.tag_configure("bigfont", font=("Helvetica", "24", "bold"))

    code.text.insert("end", "one\ntwo\nthree\n")
    code.text.insert("end", "four\n",("bigfont"))
    code.text.insert("end", "five\n")

    code.pack(side="top", fill="both", expand=True)
    root.mainloop()