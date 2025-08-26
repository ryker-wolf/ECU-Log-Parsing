import tkinter as tk
from tkinter import filedialog
import time
import os
import zlib
import struct
root = tk.Tk()
root.withdraw()
os.system("")

from enum import IntEnum

class Enum15(IntEnum): # any of the const values that are unnamed I was simply too lazy to find, it was tedious
    const_0 = 0
    const_1 = 1
    const_2 = 2
    const_3 = 3
    const_4 = 4
    const_5 = 5
    const_6 = 10
    const_7 = 14
    const_8 = 15
    const_9 = 20
    const_10 = 21
    const_11 = 30
    const_12 = 31
    const_13 = 32
    const_14 = 33
    const_15 = 40
    const_16 = 47
    const_17 = 50
    const_18 = 51
    const_19 = 54
    const_20 = 55
    const_21 = 56
    const_22 = 57
    const_23 = 58
    const_24 = 59
    const_25 = 60
    const_26 = 61
    const_27 = 62
    const_28 = 64
    kiloPerSecond = 70
    gramPerSecond = 71
    poundPerHour = 72
    poundPerMinute = 73
    poundPerSecond = 74
    kilogramPerHour = 75
    kiloPerMinute = 76
    const_36 = 80
    const_37 = 81
    const_38 = 82
    const_39 = 85
    const_40 = 86
    const_41 = 87
    pascal = 90
    const_43 = 91
    const_44 = 92
    inhg = 97
    psi = 98
    bar = 99
    const_48 = 100
    pascalPS = 105
    const_50 = 106
    psiPS = 107
    barps = 108
    meterPerSecond = 110
    kilometerPerHour = 113
    milePerHour = 114
    const_56 = 115
    const_57 = 120
    const_58 = 127
    const_59 = 125
    const_60 = 126
    const_61 = 130
    const_62 = 131
    const_63 = 133
    const_64 = 134
    const_65 = 135
    const_66 = 136
    cubicMMPerSecond = 140
    literPerHour = 141
    const_69 = 142
    cubicMMPerSecond2 = 143
    literPerSecond = 144
    cubicCMPS = 145
    const_73 = 150
    number = 155
    percent = 156
    ppm = 157
    radian = 160
    degreeAngle = 161
    const_79 = 170
    const_80 = 180
    const_81 = 182
    meter = 190
    const_83 = 191
    const_84 = 192
    const_85 = 194
    inch = 199
    foot = 200
    mile = 202
    nauticalMile = 203
    const_90 = 210
    kilogram = 220
    gram = 223
    milligram = 224
    micropound = 230
    weightUnknown = 237
    lambda_val = 238
    lambdaPhi = 239
    afrMethanol = 231
    const_99 = 232
    afrDiesel = 233
    afrGasoline = 234
    const_102 = 235
    const_103 = 236
    kelvin = 240
    celcius = 241
    fahrenheit = 242
    timeSecond = 248
    timeMinute = 249
    timeHour = 250
    timeDay = 251
    timeFortnight = 252
    timeMillisecond = 254
    timeMicrosecond = 255

class HPLLoader:
    def __init__(self, logPath):
        self.logPath = logPath
        self.log = open(self.logPath, 'rb')
        self.data = None
        self.dataPosition = 0
    
    def hexStr(self, data):
        hexBytes = " ".join(f"0x{b:02X}" for b in data) # idfk what im doing
        return hexBytes

    def ensureHPTunersFormat(self):
        fileCode = self.log.read(3).hex()
        return fileCode == str("HPT").encode("utf-8").hex() # make sure its a HPT formatted file

    def ensureType(self):
        if not self.ensureHPTunersFormat():
            return False
        logCode = self.log.read(2).hex()
        self.log.read(1)
        return logCode == "2060" # this makes sure its a log file

    def readInt32(self):
        firstByte = self.log.read(1)[0]
        result = (self.log.read(1)[0] << 8) | firstByte
        return result

    def skip(self, amt):
        self.log.read(amt) # lol
    
    def rebuildAES(self):
        AESKey = self.log.read(16)
        print(f"AES key: {self.hexStr(AESKey)}") # you can use the AES key to decrypt the information related to the vehicle, I found no use in it :) (things like the VIN)

    def readData(self, amt):
        temp = []
        for b in range(0, amt):
            temp.append(self.data[self.dataPosition])
            self.dataPosition = self.dataPosition + 1
        return temp

    def readDataSingle(self):
        return self.readData(1)[0] # i got tired of typing brackets

    def readDataInt32(self):
        firstByte = self.readDataSingle()
        result = (self.readDataSingle() << 8) | firstByte
        self.readData(2) # add some padding?
        return result

    def read7BitEncodedInt(self):
        num = 0
        num2 = 0
        while num2 != 35:
            b = self.readDataSingle()
            num |= (b & 127) << num2
            num2 += 7
            if (b & 128) == 0:
                return num
        raise ValueError("Format_Bad7BitInt32") # 1:1 from dnspy

    def readString(self):
        strLength = self.read7BitEncodedInt()
        if strLength:
            strBytes = self.readData(strLength)
            strr = bytes(strBytes).decode('utf-8')
            return strr

    def readDouble(self):
        buffer = self.readData(8)
        num = (buffer[0] | (buffer[1] << 8) | (buffer[2] << 16) | 
            (buffer[3] << 24))
        num2 = (buffer[4] | (buffer[5] << 8) | (buffer[6] << 16) | 
                (buffer[7] << 24))
        num3 = (num2 << 32) | num
        return struct.unpack('d', num3.to_bytes(8, 'little'))[0]

    def readInt64(self):
        buffer = self.readData(8)
        num = (buffer[0] | (buffer[1] << 8) | (buffer[2] << 16) | 
               (buffer[3] << 24))
        num2 = (buffer[4] | (buffer[5] << 8) | (buffer[6] << 16) | 
                (buffer[7] << 24))
        return (num2 << 32) | num

    def setData(self, dataLength):
        self.data = zlib.decompress(self.log.read(dataLength), wbits=-zlib.MAX_WBITS) # the data is compressed, must decompress it to read
        self.dataPosition = 0

    def rebuildReader(self):
        print("Parsing HPL file...")
        out = open("hpl_output.txt", "w")

        logSize = self.readInt32()
        self.log.read(logSize)
        channelCount = int(self.log.read(1).hex(), 16)
        self.skip(1)

        out.write(f"Log size: {logSize}\nChannel count: {channelCount}\n")
        for ch in range(0, channelCount):
            dataLength = self.readInt32()
            self.skip(2) # more buffer, this may become used if the file gets big enough?
            self.setData(dataLength)
            channelId = self.readDataInt32()
            self.readString()
            dataType = self.readData(1)[0]
            eDataType = Enum15(dataType)
            interval = self.readDataInt32()
            dataCount = self.readDataInt32()

            out.write(f"channelId: {channelId}\ndataType: {dataType} | {hex(dataType)} | {eDataType.name}\ninterval: {interval}\ncount: {dataCount}\n")
            for x in range(0, dataCount):
                if eDataType:
                    dateTime = self.readInt64()
                    val = self.readDouble()
                    end = ", "
                    if x == dataCount - 1:
                        end = ""
                    out.write(f"{val}{end}") # NOTE: no conversions have been done. You can do the conversions based off the Enum15 type
                else: # things like "On/Off"
                    dateTime = self.readInt64()
                    strr = self.readString()
                    end = ", "
                    if x == dataCount - 1:
                        end = ""
                    out.write(f"{strr}{end}")
            out.write("\n")
        out.close()
        print("Done!")


logFile = filedialog.askopenfilename(
    title="Open HPL file",
    filetypes=[("All files", "*.hpl")]
)

if logFile:
    loader = HPLLoader(logFile)
    if loader.ensureType():
        loader.rebuildAES()
        loader.rebuildReader()
