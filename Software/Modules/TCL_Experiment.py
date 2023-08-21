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

import pandas as pd
import numpy as np
import pathlib
import time
from datetime import datetime
from Modules.enums import CSVColumns

## Error messages
ERROR_T1 = "Error: Experiment table has duplicate values in time column."
ERROR_T2 = "Error: Experiment table has time intervals smaller than 100 ms."
ERROR_T3 = "Error: Experiment table has negative values of time."

ERROR_SP1 = "Error: Experiment table has absolute values of setpoint 1 exceeding 100°C."
ERROR_SP2 = "Error: Experiment table has absolute values of setpoint 2 exceeding 100°C."
WARNING_SP1 = "Warning: Experiment table has negative values of relative setpoint 1."
WARNING_SP2 = "Warning: Experiment table has negative values of relative setpoint 2."

class Experiment:
	def __init__(self, expPath):
		self.expTable = pd.read_csv(expPath)
		self.currentRow = 0
		#self.current_index = 0
		#self.final_index = self.expTable[CSVColumns.Time.value].size
		self.final_time = self.expTable[CSVColumns.Time.value].max()

		self.initial_time = self._millis()
		self.current_time = self._millis()
		self.ellapsed_time = self._millis()
		self.last_iteration_time = 0
		self.period = 200 # [ms]
		self.run_flag = True

		self.temperatures = 0
		self.controlAction = 0
		self.disturbedControlAction = 0

		self.last_log_time = 0
		self.log_filename = 0

		self._assertExperimentTable()
		self._createLogDatabase()

	def log(self):
		tempDB = pd.DataFrame(
			{
				CSVColumns.Time.value: self.ellapsed_time,
				CSVColumns.TemperatureH1.value: [self.temperatures[0]],
				CSVColumns.TemperatureH2.value: [self.temperatures[1]],
				CSVColumns.TemperatureAMB.value: [self.temperatures[2]],
				CSVColumns.SetPoint1Absolute.value: self.currentRow[CSVColumns.SetPoint1Absolute.value],
				CSVColumns.SetPoint2Absolute.value: self.currentRow[CSVColumns.SetPoint2Absolute.value],
				CSVColumns.SetPoint1Relative.value: self.currentRow[CSVColumns.SetPoint1Relative.value],
				CSVColumns.SetPoint1Relative.value: self.currentRow[CSVColumns.SetPoint1Relative.value],
				CSVColumns.MultiplicativeNoiseH1.value: self.currentRow[CSVColumns.MultiplicativeNoiseH1.value],
				CSVColumns.MultiplicativeNoiseH2.value: self.currentRow[CSVColumns.MultiplicativeNoiseH2.value],
				CSVColumns.MultiplicativeNoiseFan.value: self.currentRow[CSVColumns.MultiplicativeNoiseFan.value],
				CSVColumns.AdditiveNoiseH1.value: self.currentRow[CSVColumns.AdditiveNoiseH1.value],
				CSVColumns.AdditiveNoiseH2.value: self.currentRow[CSVColumns.AdditiveNoiseH2.value],
				CSVColumns.AdditiveNoiseFan.value: self.currentRow[CSVColumns.AdditiveNoiseFan.value],
				CSVColumns.NegativeSaturationH1.value: self.currentRow[CSVColumns.NegativeSaturationH1.value],
				CSVColumns.NegativeSaturationH2.value: self.currentRow[CSVColumns.NegativeSaturationH2.value],
				CSVColumns.NegativeSaturationFan.value: self.currentRow[CSVColumns.NegativeSaturationFan.value],
				CSVColumns.PositiveSaturationH1.value: self.currentRow[CSVColumns.PositiveSaturationH1.value],
				CSVColumns.PositiveSaturationH2.value: self.currentRow[CSVColumns.PositiveSaturationH2.value],
				CSVColumns.PositiveSaturationFan.value: self.currentRow[CSVColumns.PositiveSaturationFan.value],
				CSVColumns.ComputedPWMH1.value: [self.controlAction[0][0]],
				CSVColumns.ComputedPWMH2.value: [self.controlAction[0][1]],
				CSVColumns.ComputedPWMFan.value: [self.controlAction[0][2]],
				CSVColumns.NewControlAction.value: [self.controlAction[1]],
				CSVColumns.DisturbedPWMH1.value: [self.disturbedControlAction[0][0]],
				CSVColumns.DisturbedPWMH2.value: [self.disturbedControlAction[0][1]],
				CSVColumns.DisturbedPWMFan.value: [self.disturbedControlAction[0][2]],
			}
		)
		self.logDB = pd.concat([self.logDB, tempDB])

		if self.ellapsed_time - self.last_log_time >= 5000:
			self.last_log_time = self.ellapsed_time
			path = pathlib.Path(self.log_filename)
			if path.is_file():
				self.logDB.to_csv(self.log_filename, mode = 'a', index = False, header = False)
			else:
				self.logDB.to_csv(self.log_filename, index = False, header = True)
			self._clearLog()

	def iterationControl(self):
		self.ellapsedTime()
		if self.ellapsed_time - self.last_iteration_time >= self.period:
			self.last_iteration_time = self.ellapsed_time
			self._getCurrentRow()
			return True
		else:
			return False

	def setInitialTime(self):
		self.initial_time = self._millis()

	def terminateExecution(self):
		self.run_flag = False

	def ellapsedTime(self):
		self.current_time = self._millis()
		self.ellapsed_time = self.current_time - self.initial_time
		if self.ellapsed_time > self.final_time:
			self.terminateExecution()

	def getSetPoints(self):
		cr = self.currentRow
		return cr[CSVColumns.SetPoint1Absolute.value], cr[CSVColumns.SetPoint2Absolute.value], cr[CSVColumns.SetPoint1Relative.value], cr[CSVColumns.SetPoint1Relative.value]

	def setTemperatures(self, temp):
		self.temperatures = temp

	def getTemperatures(self):
		return self.temperatures

	def applyDisturbances(self):
		H1PWM = self.controlAction[0][0]
		H2PWM = self.controlAction[0][1]
		CoPWM = self.controlAction[0][2]
		if np.isnan(H1PWM):
			H1PWM = 0
		if np.isnan(H2PWM):
			H2PWM = 0
		if np.isnan(CoPWM):
			CoPWM = 0

		H1PWM = np.clip(H1PWM*self.currentRow[CSVColumns.MultiplicativeNoiseH1.value] + self.currentRow[CSVColumns.AdditiveNoiseH1.value], self.currentRow[CSVColumns.NegativeSaturationH1.value], self.currentRow[CSVColumns.PositiveSaturationH1.value])
		H2PWM = np.clip(H2PWM*self.currentRow[CSVColumns.MultiplicativeNoiseH2.value] + self.currentRow[CSVColumns.AdditiveNoiseH2.value], self.currentRow[CSVColumns.NegativeSaturationH2.value], self.currentRow[CSVColumns.PositiveSaturationH2.value])
		CoPWM = np.clip(CoPWM*self.currentRow[CSVColumns.MultiplicativeNoiseFan.value] + self.currentRow[CSVColumns.AdditiveNoiseFan.value], self.currentRow[CSVColumns.NegativeSaturationFan.value], self.currentRow[CSVColumns.PositiveSaturationFan.value])

		self.disturbedControlAction = ((H1PWM, H2PWM, CoPWM), self.controlAction[1])

	def getDisturbedControlAction(self):
		return self.disturbedControlAction[0]

	def _clearLog(self):
		del self.logDB
		self._createLogDatabase(createFilename = False)

	def _getCurrentRow(self):
		self.currentRow = self.expTable[self.expTable[CSVColumns.Time.value] <= self.ellapsed_time].iloc[-1]
		self._assertCurrentRow()

	def _assertCurrentRow(self):

		if np.isnan(self.currentRow[CSVColumns.MultiplicativeNoiseH1.value]):
			self.currentRow[CSVColumns.MultiplicativeNoiseH1.value] = 1
		if np.isnan(self.currentRow[CSVColumns.MultiplicativeNoiseH2.value]):
			self.currentRow[CSVColumns.MultiplicativeNoiseH2.value] = 1
		if np.isnan(self.currentRow[CSVColumns.MultiplicativeNoiseFan.value]):
			self.currentRow[CSVColumns.MultiplicativeNoiseFan.value] = 1
		if np.isnan(self.currentRow[CSVColumns.AdditiveNoiseH1.value]):
			self.currentRow[CSVColumns.AdditiveNoiseH1.value] = 0
		if np.isnan(self.currentRow[CSVColumns.AdditiveNoiseH2.value]):
			self.currentRow[CSVColumns.AdditiveNoiseH2.value] = 0
		if np.isnan(self.currentRow[CSVColumns.AdditiveNoiseFan.value]):
			self.currentRow[CSVColumns.AdditiveNoiseFan.value] = 1
		if np.isnan(self.currentRow[CSVColumns.NegativeSaturationH1.value]):
			self.currentRow[CSVColumns.NegativeSaturationH1.value] = 0
		if np.isnan(self.currentRow[CSVColumns.NegativeSaturationH2.value]):
			self.currentRow[CSVColumns.NegativeSaturationH2.value] = 0
		if np.isnan(self.currentRow[CSVColumns.NegativeSaturationFan.value]):
			self.currentRow[CSVColumns.NegativeSaturationFan.value] = 0
		if np.isnan(self.currentRow[CSVColumns.PositiveSaturationH1.value]):
			self.currentRow[CSVColumns.PositiveSaturationH1.value] = 100
		if np.isnan(self.currentRow[CSVColumns.PositiveSaturationH2.value]):
			self.currentRow[CSVColumns.PositiveSaturationH2.value] = 100
		if np.isnan(self.currentRow[CSVColumns.PositiveSaturationFan.value]):
			self.currentRow[CSVColumns.PositiveSaturationFan.value] = 100

	def _millis(self):
		return round(time.time()*1000)

	def _createLogDatabase(self, createFilename = True):
		columns_list = [column.value for column in CSVColumns]
		self.logDB = pd.DataFrame(columns = columns_list)
		if createFilename == True:
			date_format = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
			self.log_filename = f'Logs/{date_format}.csv'

	def _assertExperimentTable(self):
		# Tests if time values are unique.
		if (self.expTable[CSVColumns.Time.value].count() != self.expTable[CSVColumns.Time.value].nunique()):
			print(ERROR_T1)
			exit()
		# Tests if delta t exceeds 100 ms for every sample.
		if (self.expTable[CSVColumns.Time.value].diff().min() < 100):
			print(ERROR_T2)
			exit()
		# Tests if there are negative values of t.
		if (self.expTable[CSVColumns.Time.value].min() < 0):
			print(ERROR_T3)
			exit()
		# Tests if there are absolute setpoint 1 that exceeds 100°C.
		if (self.expTable[CSVColumns.SetPoint1Absolute.value].max() > 100):
			print(ERROR_SP1)
			exit()
		# Tests if there are absolute setpoint 2 that exceeds 100°C.
		if (self.expTable[CSVColumns.SetPoint2Absolute.value].max() > 100):
			print(ERROR_SP2)
			exit()
		# Tests if there are negative values of relative setpoint 1.
		if (self.expTable[CSVColumns.SetPoint1Relative.value].min() < 0):
			print(WARNING_SP1)
		# Tests if there are negative values of relative setpoint 2.
		if (self.expTable[CSVColumns.SetPoint1Relative.value].min() < 0):
			print(WARNING_SP2)