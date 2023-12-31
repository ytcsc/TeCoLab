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

import importlib
from Modules.tecolab_experiment import Experiment
from Modules.tecolab_communication_protocol import searchTeCoLabPort, readTemperatures, writePWMs
from Modules.tecolab_command_line_arguments import getParameters
from Modules.tecolab_messages import TecolabMessages

## Get parameters
args = getParameters()
expFilePath = 'Experiments/' + args.ExperimentFileName + '.csv'
controlFilePath = 'Controllers.' + args.ControllerModuleName
controlModule = importlib.import_module(controlFilePath)

## Search for a TeCoLab device
tecolab = searchTeCoLabPort()
if tecolab == False:
	print(TecolabMessages.Message1.value)
	exit()

## Load the selected experiment
print(TecolabMessages.Message2.value + args.ExperimentFileName)
experiment = Experiment(experiment_path = expFilePath, experiment_period = args.period)
print(TecolabMessages.Message3.value)
print(experiment.table)

## Load the selected controller
if (args.period < 1):
	args.period = 1
controller = controlModule.Controller()
controller.control_setup()

while(experiment.is_running == True):
	if (experiment.iterationControl() == True):
		# Reads temperatures
		experiment.setTemperatures(readTemperatures(tecolab))

		# Get control action
		experiment.setControlAction(controller._control_compute(experiment.getSetPoints(), experiment.getTemperatures()))

		# Adds experiment disturbances
		experiment.applyDisturbances()

		# Applies to the board
		writePWMs(tecolab, experiment.getDisturbedControlAction())

		# Logs the information
		experiment.log()

writePWMs(tecolab, (0, 0, 0)) # Turn the board off after the experiment