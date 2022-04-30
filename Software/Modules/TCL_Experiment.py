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
import datetime

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
		#self.final_index = self.expTable["time [ms]"].size
		self.final_time = self.expTable["time [ms]"].max()

		self.initial_time = self._millis()
		self.current_time = self._millis()
		self.ellapsed_time = self._millis()
		self.last_iteration_time = 0
		self.period = 100 # [ms]
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
				"Time [ms]": self.ellapsed_time,
				"TempH1 [°C]": [self.temperatures[0]],
				"TempH2 [°C]": [self.temperatures[1]],
				"TempAm [°C]": [self.temperatures[2]],
				"sp1_abs [°C]": self.currentRow["sp1_abs [°C]"],
				"sp2_abs [°C]": self.currentRow["sp2_abs [°C]"],
				"sp1_rel [°C]": self.currentRow["sp1_rel [°C]"],
				"sp2_rel [°C]": self.currentRow["sp2_rel [°C]"],
				"h1_mul_noise": self.currentRow["h1_mul_noise"],
				"h2_mul_noise": self.currentRow["h2_mul_noise"],
				"fan_mul_noise": self.currentRow["fan_mul_noise"],
				"h1_add_noise": self.currentRow["h1_add_noise"],
				"h2_add_noise": self.currentRow["h2_add_noise"],
				"fan_add_noise": self.currentRow["fan_add_noise"],
				"h1_neg_sat": self.currentRow["h1_neg_sat"],
				"h2_neg_sat": self.currentRow["h2_neg_sat"],
				"fan_neg_sat": self.currentRow["fan_neg_sat"],
				"h1_pos_sat": self.currentRow["h1_pos_sat"],
				"h2_pos_sat": self.currentRow["h2_pos_sat"],
				"fan_pos_sat": self.currentRow["fan_pos_sat"],
				"ComputedPWMH1": [self.controlAction[0][0]],
				"ComputedPWMH2": [self.controlAction[0][1]],
				"ComputedPWMFan": [self.controlAction[0][2]],
				"NewControlAction": [self.controlAction[1]],
				"DisturbedPWMH1": [self.disturbedControlAction[0][0]],
				"DisturbedPWMH2": [self.disturbedControlAction[0][1]],
				"DisturbedPWMFan": [self.disturbedControlAction[0][2]],
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
		return cr["sp1_abs [°C]"], cr["sp2_abs [°C]"], cr["sp1_rel [°C]"], cr["sp2_rel [°C]"]

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

		H1PWM = np.clip(H1PWM*self.currentRow["h1_mul_noise"] + self.currentRow["h1_add_noise"], self.currentRow["h1_neg_sat"], self.currentRow["h1_pos_sat"])
		H2PWM = np.clip(H2PWM*self.currentRow["h2_mul_noise"] + self.currentRow["h2_add_noise"], self.currentRow["h2_neg_sat"], self.currentRow["h2_pos_sat"])
		CoPWM = np.clip(CoPWM*self.currentRow["fan_mul_noise"] + self.currentRow["fan_add_noise"], self.currentRow["fan_neg_sat"], self.currentRow["fan_pos_sat"])

		self.disturbedControlAction = ((H1PWM, H2PWM, CoPWM), self.controlAction[1])

	def getDisturbedControlAction(self):
		return self.disturbedControlAction[0]

	def _clearLog(self):
		del self.logDB
		self._createLogDatabase(createFilename = False)

	def _getCurrentRow(self):
		self.currentRow = self.expTable[self.expTable["time [ms]"] <= self.ellapsed_time].iloc[-1]
		self._assertCurrentRow()

	def _assertCurrentRow(self):
		if np.isnan(self.currentRow["h1_mul_noise"]):
			self.currentRow["h1_mul_noise"] = 1
		if np.isnan(self.currentRow["h2_mul_noise"]):
			self.currentRow["h2_mul_noise"] = 1
		if np.isnan(self.currentRow["fan_mul_noise"]):
			self.currentRow["fan_mul_noise"] = 1
		if np.isnan(self.currentRow["h1_add_noise"]):
			self.currentRow["h1_add_noise"] = 0
		if np.isnan(self.currentRow["h2_add_noise"]):
			self.currentRow["h2_add_noise"] = 0
		if np.isnan(self.currentRow["fan_add_noise"]):
			self.currentRow["fan_add_noise"] = 1
		if np.isnan(self.currentRow["h1_neg_sat"]):
			self.currentRow["h1_neg_sat"] = 0
		if np.isnan(self.currentRow["h2_neg_sat"]):
			self.currentRow["h2_neg_sat"] = 0
		if np.isnan(self.currentRow["fan_neg_sat"]):
			self.currentRow["fan_neg_sat"] = 0
		if np.isnan(self.currentRow["h1_pos_sat"]):
			self.currentRow["h1_pos_sat"] = 100
		if np.isnan(self.currentRow["h2_pos_sat"]):
			self.currentRow["h2_pos_sat"] = 100
		if np.isnan(self.currentRow["fan_pos_sat"]):
			self.currentRow["fan_pos_sat"] = 100

	def _millis(self):
		return round(time.time()*1000)

	def _createLogDatabase(self, createFilename = True):
		self.logDB = pd.DataFrame(columns = ['Time [ms]', 'TempH1 [°C]', 'TempH2 [°C]', 'TempAm [°C]', 'sp1_abs [°C]', 'sp2_abs [°C]', 'sp1_rel [°C]', 'sp2_rel [°C]', 'h1_mul_noise', 'h2_mul_noise', 'fan_mul_noise', 'h1_add_noise', 'h2_add_noise', 'fan_add_noise', 'h1_neg_sat', 'h2_neg_sat', 'fan_neg_sat', 'h1_pos_sat', 'h2_pos_sat', 'fan_pos_sat', 'ComputedPWMH1', 'ComputedPWMH2', 'ComputedPWMFan', 'NewControlAction', 'DisturbedPWMH1', 'DisturbedPWMH2', 'DisturbedPWMFan'])
		if createFilename == True:
			self.log_filename = "Logs/" + datetime.datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p") + ".csv"

	def _assertExperimentTable(self):
		# Tests if time values are unique.
		if (self.expTable["time [ms]"].count() != self.expTable["time [ms]"].nunique()):
			print(ERROR_T1)
			exit()
		# Tests if delta t exceeds 100 ms for every sample.
		if (self.expTable["time [ms]"].diff().min() < 100):
			print(ERROR_T2)
			exit()
		# Tests if there are negative values of t.
		if (self.expTable["time [ms]"].min() < 0):
			print(ERROR_T3)
			exit()
		# Tests if there are absolute setpoint 1 that exceeds 100°C.
		if (self.expTable["sp1_abs [°C]"].max() > 100):
			print(ERROR_SP1)
			exit()
		# Tests if there are absolute setpoint 2 that exceeds 100°C.
		if (self.expTable["sp2_abs [°C]"].max() > 100):
			print(ERROR_SP2)
			exit()
		# Tests if there are negative values of relative setpoint 1.
		if (self.expTable["sp1_rel [°C]"].min() < 0):
			print(WARNING_SP1)
		# Tests if there are negative values of relative setpoint 2.
		if (self.expTable["sp2_rel [°C]"].min() < 0):
			print(WARNING_SP2)