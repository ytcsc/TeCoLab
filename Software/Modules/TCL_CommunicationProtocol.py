'''
Copyright 2022 Leonardo Cabral

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import serial
import serial.tools.list_ports
import time
import numpy as np
import struct

def searchTeCoLabPort():
	## Check connected serial ports
	ports = serial.tools.list_ports.comports()
	if ports:
		print("Identifying serial devices connected:")
		for port, desc, hwid in sorted(ports):
		   	print("{}: {} [{}]".format(port, desc, hwid))
	else:
		print("No serial devices connected. Terminating program.")
		return False
	## Search for TeCoLab device
	print("Searching for TeCoLab device:")
	for port, desc, hwid in sorted(ports):
		ser = serial.Serial(port, 115200, timeout = 0.10)
		time.sleep(4)
		print("Testing port: {}".format(ser.name))
		ser.write(b"AA")
		ans = ser.read(2)
		if ans == b"AA":
			print("TeCoLab device found at port: {}".format(ser.name))
			return ser
		else:
			ser.close()
	return False

def computeCheckSum(data):
	checksum = 0
	for ch in data:
		checksum += ch
	checksum = checksum & 0xFF
	return checksum

def readTemperatures(tecolab):
	serialMessage = b"R" + struct.pack('>B', 0x00) + struct.pack('>B', 0x06)
	serialMessage = serialMessage + struct.pack('>B', computeCheckSum(serialMessage))
	tecolab.write(serialMessage)

	tempMessage = tecolab.read(8)
	error = tempMessage[0]
	TAmsignal = 1 - 2*(tempMessage[2] >> 7)
	TemperatureAm = TAmsignal * (((tempMessage[2] & 0x7F)*(2**8) + tempMessage[1]) / 100)
	TH1signal = 1 - 2*(tempMessage[4] >> 7)
	TemperatureH1 = TH1signal * (((tempMessage[4] & 0x7F)*(2**8) + tempMessage[3]) / 100)
	TH2signal = 1 - 2*(tempMessage[6] >> 7)
	TemperatureH2 = TH2signal * (((tempMessage[6] & 0x7F)*(2**8) + tempMessage[5]) / 100)
	ChSum = tempMessage[7]

	return TemperatureH1, TemperatureH2, TemperatureAm

def writePWMs(tecolab, controlAction):
	H1 = int(round(np.clip(controlAction[0]*255/100, 0, 255)))
	H2 = int(round(np.clip(controlAction[1]*255/100, 0, 255)))
	Co = int(round(np.clip(controlAction[2]*255/100, 0, 255)))
	serialMessage = b"W" + struct.pack('>B', 0x06) + struct.pack('>B', 0x03) + struct.pack('>B', H1) + struct.pack('>B', H2) + struct.pack('>B', Co)
	serialMessage = serialMessage + struct.pack('>B', computeCheckSum(serialMessage))
	tecolab.write(serialMessage)
	return tecolab.read(2)