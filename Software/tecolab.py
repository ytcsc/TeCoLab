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

from Modules.TCL_Experiment import *
from Modules.TCL_CommunicationProtocol import *
from Controllers.NullControl import *

## Parameters (to do: remove the need of this part)
expPath = "Experiments/basic.csv"

## Search for a TeCoLab device
tecolab = searchTeCoLabPort()
if tecolab == False:
	print("No TeCoLab device found. Terminating program.")
	exit()

## Load the selected experiment
print("Loading experiment.")
exp = Experiment(expPath)
print(exp.expTable)

## Load the selected controller
cont = Controller(T = 2)

## Execute experiment
exp.setInitialTime()

while(exp.run_flag == True):
	if (exp.iterationControl() == True):
		# Reads temperatures
		exp.setTemperatures(readTemperatures(tecolab))

		# Get control action
		exp.controlAction = cont._control(exp.getSetPoints(), exp.getTemperatures())

		# Adds experiment disturbances
		exp.applyDisturbances()

		# Applies to the board
		writePWMs(tecolab, exp.getDisturbedControlAction())

		# Logs the information
		exp.log()

		