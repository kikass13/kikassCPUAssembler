#!/usr/bin/env python3

from enum import Enum

######################################################################################################################


BINARY_ROM_MAX_SIZE = 0xFFFF
DEFAULT_ROM = lambda: [0] * BINARY_ROM_MAX_SIZE

class AssemblerChecker(object):
    class LINETYPE(Enum):
        UNKNOWN = 0                 ### 
        CODE = 1                    ### abcdefghi
        LABEL = 2                   ### main:
        ADDRESS = 3                 ### #0x0F0A
        SYMBOLDEF = 4               ### $SYMBOL_NAME = 1

        CONSTSTATIC = 6             ### .0x10       
        COMMENT = 10                ### // some comment

    checkDict = {
        LINETYPE.CODE:              lambda self, l: self.isCode(l),
        LINETYPE.LABEL:             lambda self, l: self.isLabel(l),
        LINETYPE.ADDRESS:           lambda self, l: self.isFixedAddress(l),
        LINETYPE.SYMBOLDEF:         lambda self, l: self.isSymbolDefinition(l),
        LINETYPE.CONSTSTATIC:       lambda self, l: self.isConstStatic(l),
        LINETYPE.COMMENT:           lambda self, l: self.isComment(l),
    }
    assemblyDict = {
        LINETYPE.CODE:              lambda self, **kwargs: self.assembleCode(**kwargs),
        LINETYPE.LABEL:             lambda self, **kwargs: self.assembleLabel(**kwargs),
        LINETYPE.ADDRESS:           lambda self, **kwargs: self.assembleFixedAddress(**kwargs),
        LINETYPE.CONSTSTATIC:       lambda self, **kwargs: self.assembleConstStatic(**kwargs),
        LINETYPE.COMMENT:           lambda self, **kwargs: self.assembleComment(**kwargs),
    }

    cmdDict = {
        "lda":     {
                    "Id": "3", 
                    "Opcode": "0x0C", 
                    "Args": "1",
                    "Parameters": "<const int>",
                    "Description": "",
                    "Tasks": "",
                },
        "jmp":     {
                    "Id": "200", 
                    "Opcode": "0xF0", 
                    "Args": "1",
                    "Parameters": "<address>",
                    "Description": "Jump to <address>",
                    "Tasks": "PC = <address>",
                },
    }

    def __init__(self):
        pass

    def assemble(self, text):
        success = True
        errors = []
        binary = DEFAULT_ROM()

        ### first repeat the check
        codeOk, results, pseudocode = self.checkCode(text)
        errors.extend(results)
        ### then use the coe to assemble stuff
        binaryIndex = 0
        if codeOk:
            ### use pseudocode to interprete and convert to binary
            binary, binaryIndex, labelDict = self.assembleLines(pseudocode, binary=binary, binaryIndex=binaryIndex)
        return success and codeOk, errors, binary, binaryIndex

    def assembleLines(self, pseudocode, binary=DEFAULT_ROM(), binaryIndex=0, labels={}, lineNumber=0, lineType=None, key=None, line=None):
        labelDict = {}
        for lineNumber, lineType, key, line in pseudocode:
            binary, binaryIndex, labelDict = self.assembleLine(binary=binary, binaryIndex=binaryIndex, labels=labels, lineNumber=lineNumber, lineType=lineType, key=key, line=line)
        return binary, binaryIndex, labelDict
    
    def assembleLine(self, binary=DEFAULT_ROM(), binaryIndex=0, labels={}, lineNumber=0, lineType=None, key=None, line=None):
        func = self.assemblyDict.get(lineType)
        if func:
            binary, binaryIndex, labels = func(self, binary=binary, binaryIndex=binaryIndex, labels=labels, lineNumber=lineNumber, lineType=lineType, key=key, line=line)
        return binary, binaryIndex, labels

    def checkCode(self, text):
        success = True
        errors = []
        pseudocode = []
        ### prepare
        lines = text.split("\n")

        symbols = {}
        ### resolve symbols in code if necessary
        #########################################################################################
        symbolReplacesLines = []
        for i, line in enumerate(lines):
            symbolKey = self.isSymbolDefinition(line)
            if symbolKey: 
                ### we have the desire to resolve all symbols before we return our pseudocode
                ### so we have to keep track of them
                symbols.update(symbolKey)
            ### by finding ${REF}
            left = line.find("${")
            right = line.find("}")
            newLine = line
            possibleSymbolRef = newLine[left+2:right].strip()
            if left != -1 and possibleSymbolRef:
                ### and replacing it with whatever symbol we have
                possibleSymbolVal = symbols.get(possibleSymbolRef, None)
                if possibleSymbolVal:
                    newLine = "%s%s%s" % (newLine[:left], possibleSymbolVal ,newLine[right+1:])
                else:
                    success = False
                    errors.append((i, AssemblerChecker.LINETYPE.SYMBOLDEF, possibleSymbolRef, line))
            symbolReplacesLines.append(newLine)
        #########################################################################################
        if success:
            ### check each line and fill errors and generate simplified code
            for i, line in enumerate(symbolReplacesLines):
                ### skip empty lines
                if line.strip():
                    lType, lKey = self.checkLine(line)
                    if lType == AssemblerChecker.LINETYPE.UNKNOWN or lKey == None:
                        errors.append((i+1, lType, lKey, line))
                    else:
                        ### assemble lines to see if it's actually working code
                        try:
                            binary, binaryIndex, labels = self.assembleLine(lineNumber=i+1, lineType=lType, key=lKey, line=line)
                        except Exception as e:
                            pass
                            errors.append((i+1, lType, lKey, line))
                        else:
                            ### append to our pseudo code
                            pseudocode.append((i+1, lType, lKey, line))
        ### return
        success = len(errors) == 0
        return success, errors, pseudocode

    def checkLine(self, line):
        strippedLine = line.strip()
        if strippedLine:
            ### all kinds of checks on that line
            for lType, func in self.checkDict.items():
                lKey = func(self, strippedLine)
                if not lKey == None :
                    return lType, lKey
            ### return default if nothing fits
        return AssemblerChecker.LINETYPE.UNKNOWN, None

####################################################################################################

    def assembleCode(self, binary=None, binaryIndex=None, labels=None, lineNumber=None, lineType=None, key=None, line=None):
        ### key = {cmd: LDA, args:[7]}
        cmd = key.get("cmd", None)
        op = key.get("op", None)
        args = key.get("args", None)

        if cmd and op:
            opHex = int(op, 16)
            binary[binaryIndex] = opHex
            binaryIndex += 1
        if args:
            for arg in args:
                try:
                    ### check if arg is a label
                    if arg in labels:
                        ### binaryindex of the label is used as arg
                        value = labels[arg]
                    ### process arg as some value
                    elif "0x" in arg:
                        ### convert value hex string (see if its valid)
                        value = int(arg, 16)
                    else:
                        ### convert value int
                        value = int(arg)
                except Exception as e:
                    raise e
                binary[binaryIndex] = value
                binaryIndex += 1
        return binary, binaryIndex, labels

    def assembleLabel(self, binary=None, binaryIndex=None, labels=None, lineNumber=None, lineType=None, key=None, line=None):
        labels[key] = binaryIndex
        return binary, binaryIndex, labels
    def assembleFixedAddress(self, binary=None, binaryIndex=None, labels=None, lineNumber=None, lineType=None, key=None, line=None):
        ### key = new binaryIndex
        ### + we have to extend our memory if that index is in the future
        newBinaryIndex = key
        indexDiff = newBinaryIndex - len(binary)
        if indexDiff > 0:
            ### extend memory
            binary.extend([0 for elem in range(indexDiff)])
        return binary, newBinaryIndex, labels
    def assembleConstStatic(self, binary=None, binaryIndex=None, labels=None, lineNumber=None, lineType=None, key=None, line=None):
        ### key = const value to write to memory
        binary[binaryIndex] = key
        binaryIndex+=1
        return binary, binaryIndex, labels
    def assembleComment(self, binary=None, binaryIndex=None, labels=None, lineNumber=None, lineType=None, key=None, line=None):
        return binary, binaryIndex, labels

####################################################################################################

    def isCode(self, line):
        code = None
        ### check if current line is a label for code
        stuff = line.split(" ")
        cmd = stuff[0].lower()
        args = stuff[1:]
        d = self.cmdDict.get(cmd, None)
        if d:
            code = {"cmd": cmd, "op": d["Opcode"], "args": args}
        return code

    def isLabel(self, line):
        label = None
        ### check if current line is a label (last symbol is a colon ':')
        if(len(line) >= 2 and line[-1] == ":"):
            label = line[:-1]
        return label

    def isFixedAddress(self, line):
        address = None
        ### check if current line is a fixed rom address (leading with '#')
        ### valid input would be #0xAA or #0x0 or #0xF9F9AF
        if(len(line) >= 4 and line[0:3] == "#0x"):
            try:
                ### convert address hex string (see if its valid)
                addressInt = int(line[1:], 16)
                address = addressInt
            except Exception as e:
                pass
        return address

    def isSymbolDefinition(self, line):
        symbol = None
        ### check if current line is a label (last symbol is a colon ':')
        if(len(line) >= 4 and line[0] == "$"):
            string = line[1:]
            parts = string.split("=")
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                symbol = {key : value}
        return symbol

    def isConstStatic(self, line):
        const = None
        if(len(line) >= 2 and line[0] == "."):
            try:
                if "0x" in line:
                    ### convert value hex string (see if its valid)
                    constInt = int(line[1:], 16)
                else:
                    ### convert value int
                    constInt = int(line[1:])
                const = constInt
            except Exception as e:
                pass
        return const

    def isComment(self, line):
        comment = None
        ### check if current line is a fixed rom address (leading with '#')
        ### valid input would be #0xAA or #0x0 or #0xF9F9AF
        if(len(line) >= 2 and line[0:2] == "//"):
            comment = line[2:]
        return comment



######################################################################################################################


def testCheckLine(checker, code):
    codeLines = code.split("\n")
    print("\n======================================")
    for line in codeLines:
        lineType, lineKey = checker.checkLine(line)
        if lineType == AssemblerChecker.LINETYPE.LABEL:
            print("'%s' >>> LABEL FOUND >>> %s[%s]" % (line, lineType, lineKey))
        elif lineType == AssemblerChecker.LINETYPE.ADDRESS:
            print("'%s' >>> ADDRESS FOUND >>> %s[%s]" % (line, lineType, lineKey))
        elif lineType == AssemblerChecker.LINETYPE.SYMBOLDEF:
            print("'%s' >>> SYMBOLDEF FOUND >>> %s[%s]" % (line, lineType, lineKey))
        elif lineType == AssemblerChecker.LINETYPE.CONSTSTATIC:
            print("'%s' >>> CONSTSTATIC FOUND >>> %s[%s]" % (line, lineType, lineKey))
        elif lineType == AssemblerChecker.LINETYPE.COMMENT:
            print("'%s' >>> COMMENT FOUND >>> %s[%s]" % (line, lineType, lineKey))
        elif lineType == AssemblerChecker.LINETYPE.CODE:
            print("'%s' >>> CODE FOUND >>> %s[%s]" % (line, lineType, lineKey))
        else:
            print("'%s' >>> UNKNOWN TEXT >>> %s[%s]" % (line, lineType, lineKey))
    print("======================================\n")

def main():
    checker = AssemblerChecker()
    code = "$ABC = 7\n #0x0000 \n .255 \n #0x0004 \n .0xAA \n #0x0002 \n .0xA0 \n .0xA1 \n #0x000F \n main: \n // I AM SOME COMMENT \n LDA ${ABC} \n  LDA 3 \n jmp main"
    ### test1
    testCheckLine(checker, code)
    ### test2
    success, errors, binary, lastWrittenByte= checker.assemble(code)
    print("Assembly Result:")
    print("  Success: %s" % success)
    print("  Errors: %s" % errors)
    print("  ROM: %s" % binary[:lastWrittenByte])
    
    

if __name__ == "__main__":
    main()
