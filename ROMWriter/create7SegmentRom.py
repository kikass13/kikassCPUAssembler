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
    "dp":[81]
}

N = None
byteDigits = { 
    0: [N, "a","b","c","d","e","f",N],  ### DP,a,b,c,d,e,f,g
    1: [N, N, "b","c", N, N, N, N],     ### where DP is highest bit, and g is lowest
    2: [N, "a","b", N, "d", "e", N, "g"], 
    3: [N, "a","b","c","d", N, N, "g"], 
    4: [N, "b","c", N, N, "f","g"], 
    5: [N, "a", N, "c", "d", N, "f","g"], 
    6: [N, "a", N, "c","d","e","f","g"], 
    7: [N, "a","b","c", N, N, N, N], 
    8: [N, "a","b","c","d","e","f","g"], 
    9: [N, "a","b","c","d", N, "f","g"], 
}

def digitToByte(digit):
    lines = byteDigits[digit]
    byte = 0
    for l in lines:
        bit = 1 if l else 0
        byte = (byte << 1) + bit
    #print(">>> %s" % format(byte, '#010b'))
    return byte



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
        0,                          ### 81 = DecimalPoint
    ]
    value, segments = byteDigits[decimal]
    for segment in segments:
        if segment:
            pixels = segmentMatrix[segment]
            for pixel in pixels:
                dotmatrix[pixel] = 1
    return dotmatrix

def printDigit(decimal):
    dotmatrix = digitToMatrix(decimal)
    for i,pixel in enumerate(dotmatrix):
        if i % 9 == 0:
            print("\n", end='')
        string = "." if pixel == 1 else " "
        print(string, end='')
    print("")


##############################################################################################

binary = []
print("Writing ones place")
for value in range(0, 256):
    digit = value % 10
    binVal = digitToByte(digit)
    print(digit, end=", ")
    binary.append(binVal)

### test if the segments are correct in our memory
#for byte in binary:
#    digit = getDigitFromBinary(byte)
#    printDigit(digit)

### write the rest
print("\nWriting tens place")
for value in range(0, 256):
    digit = int(value / 10) % 10
    binVal = digitToByte(digit)
    print(digit, end=", ")
    binary.append(binVal)

print("\nWriting hundreds place")
for value in range(0, 256):
    digit = int(value / 100) % 10
    binVal = digitToByte(digit)
    print(digit, end=", ")
    binary.append(binVal)

print("\nWriting sign")
for value in range(0, 256):
    negative = 0
    print(negative, end=", ")
    binary.append(negative)

print(len(binary))

print("\nWriting ones place (twos complement)")
for value in range(-128, 128):
    digit = int(abs(value) % 10)
    binVal = digitToByte(digit)
    print(digit, end=", ")
    binary.append(binVal)

print("\nWriting tens place (twos complement)")
for value in range(-128, 128):
    digit = int(abs(value / 10) % 10)
    binVal = digitToByte(digit)
    print(digit, end=", ")
    binary.append(binVal)

print("\nWriting hundreds place (twos complement)")
for value in range(-128, 128):
    digit = int(abs(value / 100) % 10)
    binVal = digitToByte(digit)
    print(digit, end=", ")
    binary.append(binVal)

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


### this should be the binary value for the digits 
### when 
### << DP,a,b,c,d,e,f,g >> is used
### where DP is highest bit, and g is lowest
###
### 0: 0x7e
### 1: 0x30
### 2: 0x6d
### 3: 0x79
### 4: 0x33
### 5: 0x5b
### 6: 0x5f
### 7: 0x70 
### 8: 0x7f
### 9: 0x7b
