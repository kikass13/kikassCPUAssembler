#!/usr/bin/env python3
import os
##############################################################################################

### 7 segment byte pattern for decimal numbers [0 ... 9]
### 
###     
###   dp, a, b, c, d, e, f, g
###
###            a
###        .........
###        .       .
###    f   .       .   b
###        .       .
###        ....g....
###        .       .
###        .       .
###    e   .       .   c
###        .........
###  dp.       d
###
###
segmentMatrix = {
    "a": [0,1,2,3,4,5,6,7,8],
    "b": [8,17,26,35,44],
    "c": [44, 53,62,71,80],
    "d": [72,73,74,75,76,77,78,79,80],
    "e": [72,63,54,45,36],
    "f": [36,27,18,9,0],
    "g": [36,37,38,39,40,41,42,43,44],
}

byteDigits = { 
    0: (0x7e, ["a","b","c","d","e","f"]), 
    1: (0x30, ["b","c"]), 
    2: (0x6d, ["a","b","g","e","d"]), 
    3: (0x79, ["a","b","c","d","g"]), 
    4: (0x33, ["f","g","b","c"]), 
    5: (0x5b, ["a","f","g","c","d"]), 
    6: (0x5f, ["a","c","d","e","f", "g"]), 
    7: (0x70, ["a","b","c"]), 
    8: (0x7f, ["a","b","c","d","e","f","g"]), 
    9: (0x7b, ["a","b","c","d","f","g"]), 
};



def digitToMatrix(decimal):
    ### test method for writing a number
    dotmatrix = [
        0, 0, 0, 0, 0, 0, 0, 0, 0,  ### 0  ... 8
        0, 0, 0, 0, 0, 0, 0, 0, 0,  ### 9  ... 17
        0, 0, 0, 0, 0, 0, 0, 0, 0,  ### 18 ... 26
        0, 0, 0, 0, 0, 0, 0, 0, 0,  ### 27 ... 35
        0, 0, 0, 0, 0, 0, 0, 0, 0,  ### 36 ... 44
        0, 0, 0, 0, 0, 0, 0, 0, 0,  ### 45 ... 53
        0, 0, 0, 0, 0, 0, 0, 0, 0,  ### 54 ... 62
        0, 0, 0, 0, 0, 0, 0, 0, 0,  ### 63 ... 71
        0, 0, 0, 0, 0, 0, 0, 0, 0,  ### 72 ... 80
    ]
    value, segments = byteDigits[decimal]
    for segment in segments:
        pixels = segmentMatrix[segment]
        for pixel in pixels:
            dotmatrix[pixel] = 1
    return dotmatrix

def printDigit(decimal):
    dotmatrix = digitToMatrix(decimal)
    #for i,v in enumerate(dotmatrix):
    #    if i>0 and i % 9 == 0:
    #        print("")
    #    print(v, end='')
    ### print the result
    for i,pixel in enumerate(dotmatrix):
        if i % 9 == 0:
            print("\n", end='')
        string = "." if pixel == 1 else " "
        print(string, end='')
    print("")

def getDigitFromBinary(b):
    for k,v in byteDigits.items():
        byte, segments = v
        if b == byte:
            return k


##############################################################################################

binary = []
print("Writing ones place")
for value in range(0, 256):
    hexbin, segments = byteDigits[value % 10]
    print(getDigitFromBinary(hexbin), end=", ")
    binary.append(hexbin)

### test if the segments are correct in our memory
#for byte in binary:
#    digit = getDigitFromBinary(byte)
#    printDigit(digit)

### write the rest
print("\nWriting tens place")
for value in range(0, 256):
    hexbin, segments = byteDigits[int(value / 10) % 10]
    print(getDigitFromBinary(hexbin), end=", ")
    binary.append(hexbin)

print("\nWriting hundreds place")
for value in range(0, 256):
    hexbin, segments = byteDigits[int(value / 100) % 10]
    print(getDigitFromBinary(hexbin), end=", ")
    binary.append(hexbin)

print("\nWriting sign")
for value in range(0, 256):
    negative = 0
    print(negative, end=", ")
    binary.append(negative)

print("\nWriting ones place (twos complement)")
for value in range(-128, 128):
    hexbin, segments =  byteDigits[int(abs(value) % 10)]
    print(getDigitFromBinary(hexbin), end=", ")
    binary.append(hexbin)

print("\nWriting tens place (twos complement)")
for value in range(-128, 128):
    hexbin, segments =  byteDigits[int(abs(value / 10) % 10)]
    print(getDigitFromBinary(hexbin), end=", ")
    binary.append(hexbin)

print("\nWriting hundreds place (twos complement)")
for value in range(-128, 128):
    hexbin, segments =  byteDigits[int(abs(value / 100) % 10)]
    print(getDigitFromBinary(hexbin), end=", ")
    binary.append(hexbin) 

print("\nWriting sign (twos complement)")
for value in range(-128, 128):
    negative = 1 if value < 0 else 0
    print(negative, end=", ")
    binary.append(negative)

print("\n\n")
print([hex(b) for b in binary])

path = os.path.join(os.path.dirname(__file__), "4digit_7segmentDecoder.bin")
print("Writing to .bin file to '%s' ..." % path)

byteArr = bytearray(binary)
with open(path, "wb") as f:
    f.write(byteArr)
print("Binary file written [%s bytes]" % len(byteArr))
print("\n")