'''
Copyright 2024 Leonardo Cabral

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

import argparse

## Other messages
VERSION = 'TeCoLab version: alpha'
EXPFILEHELP = 'experiment file name in Experiments folder without extension'
CONTMODULEHELP = 'controller module name in Controllers folder without extension'
VERSIONHELP = 'shows TeCoLab version'
PERIODHELP = 'chooses TeCoLab sampling period (default 200)'

def getParameters():
	parser = argparse.ArgumentParser()
	parser.add_argument('ExperimentFileName', help = EXPFILEHELP)
	parser.add_argument('ControllerModuleName', help = CONTMODULEHELP)
	parser.add_argument('-v', help = VERSIONHELP, action = 'store_true')
	parser.add_argument('-t', '--period', type = int, default = 200, help = PERIODHELP)
	
	if parser.parse_args().v:
		print(VERSION)

	return parser.parse_args()