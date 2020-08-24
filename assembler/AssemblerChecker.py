#!/usr/bin/env python3

from enum import Enum

######################################################################################################################

class AssemblerChecker(object):
    class LINETYPE(Enum):
        UNKNOWN = 0                 ### 
        CODE = 1                    ### abcdefghi
        LABEL = 2                   ### main:
        ADDRESS = 3                 ### #0x0F0A
        SYMBOLDEF = 4               ### $SYMBOL_NAME = 1
        #SYMBOLREF = 5              ### ${SYMBOL_NAME}
        COMMENT = 10                ### // some comment

    checkDict = {
        LINETYPE.LABEL:             lambda self, l: self.isLabel(l),
        LINETYPE.ADDRESS:           lambda self, l: self.isFixedAddress(l),
        LINETYPE.SYMBOLDEF:         lambda self, l: self.isSymbolDefinition(l),
        LINETYPE.COMMENT:           lambda self, l: self.isComment(l),
    }

    def __init__(self):
        pass

    def checkLines(self, text):
        success = True
        results = None
        ### prepare
        lines = text.split("\n")

        ### check each line
        print(lines)
        ### build up results

        ### return
        return success, results

    def checkLine(self, line):
        ### all kinds of checks on that line
        for ltype, func in self.checkDict.items():
            lKey = func(self, line)
            if lKey:
                return ltype, lKey
        ### return default if nothing fits
        return AssemblerChecker.LINETYPE.UNKNOWN, None


    def isLabel(self, line):
        label = None
        strippedLine = line.strip()
        ### check if current line is a label (last symbol is a colon ':')
        if(len(strippedLine) >= 2 and strippedLine[-1] == ":"):
            label = strippedLine[:-1]
        return label

    def isFixedAddress(self, line):
        address = None
        strippedLine = line.strip()
        ### check if current line is a fixed rom address (leading with '#')
        ### valid input would be #0xAA or #0x0 or #0xF9F9AF
        if(len(strippedLine) >= 4 and strippedLine[0:3] == "#0x"):
            try:
                ### convert address hex string (see if its valid)
                addressInt = int(strippedLine[1:], 16)
                address = strippedLine
            except Exception as e:
                pass
        return address

    def isSymbolDefinition(self, line):
        symbol = None
        strippedLine = line.strip()
        ### check if current line is a label (last symbol is a colon ':')
        if(len(strippedLine) >= 4 and strippedLine[0] == "$"):
            string = strippedLine[1:]
            parts = string.split("=")
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                symbol = {key : value}
        return symbol

    def isComment(self, line):
        comment = None
        strippedLine = line.strip()
        ### check if current line is a fixed rom address (leading with '#')
        ### valid input would be #0xAA or #0x0 or #0xF9F9AF
        if(len(strippedLine) >= 2 and strippedLine[0:2] == "//"):
            comment = line
        return comment

######################################################################################################################

def main():
    checker = AssemblerChecker()
    codeLines = ["$ABC = 7", "#0xF00A", "main: ", "// I AM SOME COMMENT", "LDA 7"]
    for line in codeLines:
        lineType, lineKey = checker.checkLine(line)
        if lineType == AssemblerChecker.LINETYPE.LABEL:
            print("'%s' >>> LABEL FOUND >>> %s[%s]" % (line, lineType, lineKey))
        elif lineType == AssemblerChecker.LINETYPE.ADDRESS:
            print("'%s' >>> ADDRESS FOUND >>> %s[%s]" % (line, lineType, lineKey))
        elif lineType == AssemblerChecker.LINETYPE.SYMBOLDEF:
            print("'%s' >>> SYMBOLDEF FOUND >>> %s[%s]" % (line, lineType, lineKey))
        elif lineType == AssemblerChecker.LINETYPE.COMMENT:
            print("'%s' >>> COMMENT FOUND >>> %s[%s]" % (line, lineType, lineKey))
        else:
            print("'%s' >>> NORMAL TEXT >>> %s[%s]" % (line, lineType, lineKey))

if __name__ == "__main__":
    main()
