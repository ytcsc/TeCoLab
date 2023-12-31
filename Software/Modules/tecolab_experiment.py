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

import pathlib
import time
import pandas as pd
import numpy as np
from datetime import datetime
from Modules.tecolab_enums import CSVColumns
from Modules.tecolab_messages import TecolabMessages

class Experiment:
	def __init__(self, experiment_path: str, experiment_period: int = 200):
		self.table = pd.read_csv(experiment_path)
		self.table_current_row = 0

		self.time_initial = self._millis()
		self.time_final = self.table[CSVColumns.Time.value].max()
		self.time_current = self.time_initial
		self.time_ellapsed = 0
		self.time_last_iteration = 0
		self.time_last_log = 0
		self.time_control_action_computation = 0

		self.period = experiment_period # [ms]
		self.is_running = True
		self.log_data_frame = pd.DataFrame(columns = [column.value for column in CSVColumns])
		self.log_filename = f'Logs/{datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")}.csv'

		self.temperatures = (0, 0, 0)
		self.control_action_computed = (0, 0, 0)
		self.control_action_disturbed = (0, 0, 0)
		self.control_action_signal = 0

		self._assertExperimentTable()

	def log(self):
		new_row = pd.DataFrame(
			{
				CSVColumns.Time.value: self.time_ellapsed,
				CSVColumns.TemperatureH1.value: [self.temperatures[0]],
				CSVColumns.TemperatureH2.value: [self.temperatures[1]],
				CSVColumns.TemperatureAMB.value: [self.temperatures[2]],
				CSVColumns.SetPoint1Absolute.value: self.table_current_row[CSVColumns.SetPoint1Absolute.value],
				CSVColumns.SetPoint2Absolute.value: self.table_current_row[CSVColumns.SetPoint2Absolute.value],
				CSVColumns.SetPoint1Relative.value: self.table_current_row[CSVColumns.SetPoint1Relative.value],
				CSVColumns.SetPoint1Relative.value: self.table_current_row[CSVColumns.SetPoint1Relative.value],
				CSVColumns.MultiplicativeNoiseH1.value: self.table_current_row[CSVColumns.MultiplicativeNoiseH1.value],
				CSVColumns.MultiplicativeNoiseH2.value: self.table_current_row[CSVColumns.MultiplicativeNoiseH2.value],
				CSVColumns.MultiplicativeNoiseFan.value: self.table_current_row[CSVColumns.MultiplicativeNoiseFan.value],
				CSVColumns.AdditiveNoiseH1.value: self.table_current_row[CSVColumns.AdditiveNoiseH1.value],
				CSVColumns.AdditiveNoiseH2.value: self.table_current_row[CSVColumns.AdditiveNoiseH2.value],
				CSVColumns.AdditiveNoiseFan.value: self.table_current_row[CSVColumns.AdditiveNoiseFan.value],
				CSVColumns.NegativeSaturationH1.value: self.table_current_row[CSVColumns.NegativeSaturationH1.value],
				CSVColumns.NegativeSaturationH2.value: self.table_current_row[CSVColumns.NegativeSaturationH2.value],
				CSVColumns.NegativeSaturationFan.value: self.table_current_row[CSVColumns.NegativeSaturationFan.value],
				CSVColumns.PositiveSaturationH1.value: self.table_current_row[CSVColumns.PositiveSaturationH1.value],
				CSVColumns.PositiveSaturationH2.value: self.table_current_row[CSVColumns.PositiveSaturationH2.value],
				CSVColumns.PositiveSaturationFan.value: self.table_current_row[CSVColumns.PositiveSaturationFan.value],
				CSVColumns.RateSaturationH1.value: self.table_current_row[CSVColumns.RateSaturationH1.value],
				CSVColumns.RateSaturationH2.value: self.table_current_row[CSVColumns.RateSaturationH2.value],
				CSVColumns.RateSaturationFan.value: self.table_current_row[CSVColumns.RateSaturationFan.value],
				CSVColumns.ComputedPWMH1.value: [self.control_action_computed[0]],
				CSVColumns.ComputedPWMH2.value: [self.control_action_computed[1]],
				CSVColumns.ComputedPWMFan.value: [self.control_action_computed[2]],
				CSVColumns.DisturbedPWMH1.value: [self.control_action_disturbed[0]],
				CSVColumns.DisturbedPWMH2.value: [self.control_action_disturbed[1]],
				CSVColumns.DisturbedPWMFan.value: [self.control_action_disturbed[2]],
				CSVColumns.NewControlAction.value: [self.control_action_signal],
				CSVColumns.ControlActionComputationTime.value: [self.time_control_action_computation],
			}
		)
		self.log_data_frame = pd.concat([self.log_data_frame, new_row])
		if self.time_ellapsed - self.time_last_log >= 5000:
			self.time_last_log = self.time_ellapsed
			path = pathlib.Path(self.log_filename)
			if path.is_file():
				self.log_data_frame.to_csv(self.log_filename, mode = 'a', index = False, header = False)
			else:
				self.log_data_frame.to_csv(self.log_filename, index = False, header = True)
			self.log_data_frame = self.log_data_frame[0:0]

	def iterationControl(self):
		self.time_current = self._millis()
		self.time_ellapsed = self.time_current - self.time_initial
		if self.time_ellapsed >= self.time_final:
			self.is_running = False
			return False
		if self.time_ellapsed - self.time_last_iteration >= self.period:
			self.time_last_iteration = self.time_ellapsed
			self._getCurrentRow()
			return True
		else:
			return False

	def getSetPoints(self):
		return self.table_current_row[CSVColumns.SetPoint1Absolute.value], self.table_current_row[CSVColumns.SetPoint2Absolute.value], self.table_current_row[CSVColumns.SetPoint1Relative.value], self.table_current_row[CSVColumns.SetPoint2Relative.value]

	def setTemperatures(self, temp):
		self.temperatures = temp

	def getTemperatures(self):
		return self.temperatures

	def setControlAction(self, control_action):
		H1PWM = control_action[0][0]
		H2PWM = control_action[0][1]
		CoPWM = control_action[0][2]
		if isinstance(H1PWM, (int, float)) == False:
			H1PWM = self.control_action_computed[0]
		if isinstance(H2PWM, (int, float)) == False:
			H2PWM = self.control_action_computed[1]
		if isinstance(CoPWM, (int, float)) == False:
			CoPWM = self.control_action_computed[2]
		self.control_action_computed = (H1PWM, H2PWM, CoPWM)
		self.control_action_signal = control_action[1]
		self.time_control_action_computation = control_action[2]

	def applyDisturbances(self):
		H1PWM = self.control_action_computed[0]
		H2PWM = self.control_action_computed[1]
		CoPWM = self.control_action_computed[2]
		
		H1PWM = H1PWM*self.table_current_row[CSVColumns.MultiplicativeNoiseH1.value]
		H1PWM = H1PWM + self.table_current_row[CSVColumns.AdditiveNoiseH1.value]
		H1PWM = np.clip(H1PWM, self.control_action_disturbed[0]-self.table_current_row[CSVColumns.RateSaturationH1.value]*self.period/1000, self.control_action_disturbed[0]+self.table_current_row[CSVColumns.RateSaturationH1.value]*self.period/1000)
		H1PWM = np.clip(H1PWM, self.table_current_row[CSVColumns.NegativeSaturationH1.value], self.table_current_row[CSVColumns.PositiveSaturationH1.value])

		H2PWM = H2PWM*self.table_current_row[CSVColumns.MultiplicativeNoiseH2.value]
		H2PWM = H2PWM + self.table_current_row[CSVColumns.AdditiveNoiseH2.value]
		H2PWM = np.clip(H2PWM, self.control_action_disturbed[1]-self.table_current_row[CSVColumns.RateSaturationH2.value]*self.period/1000, self.control_action_disturbed[1]+self.table_current_row[CSVColumns.RateSaturationH2.value]*self.period/1000)
		H2PWM = np.clip(H2PWM, self.table_current_row[CSVColumns.NegativeSaturationH2.value], self.table_current_row[CSVColumns.PositiveSaturationH2.value])

		CoPWM = CoPWM*self.table_current_row[CSVColumns.MultiplicativeNoiseFan.value]
		CoPWM = CoPWM + self.table_current_row[CSVColumns.AdditiveNoiseFan.value]
		CoPWM = np.clip(CoPWM, self.control_action_disturbed[2]-self.table_current_row[CSVColumns.RateSaturationFan.value]*self.period/1000, self.control_action_disturbed[2]+self.table_current_row[CSVColumns.RateSaturationFan.value]*self.period/1000)
		CoPWM = np.clip(CoPWM, self.table_current_row[CSVColumns.NegativeSaturationFan.value], self.table_current_row[CSVColumns.PositiveSaturationFan.value])

		self.control_action_disturbed = (H1PWM, H2PWM, CoPWM)

	def getDisturbedControlAction(self):
		return self.control_action_disturbed

	def _getCurrentRow(self):
		self.table_current_row = self.table[self.table[CSVColumns.Time.value] <= self.time_ellapsed].iloc[-1]
		if np.isnan(self.table_current_row[CSVColumns.MultiplicativeNoiseH1.value]):
			self.table_current_row[CSVColumns.MultiplicativeNoiseH1.value] = 1
		if np.isnan(self.table_current_row[CSVColumns.MultiplicativeNoiseH2.value]):
			self.table_current_row[CSVColumns.MultiplicativeNoiseH2.value] = 1
		if np.isnan(self.table_current_row[CSVColumns.MultiplicativeNoiseFan.value]):
			self.table_current_row[CSVColumns.MultiplicativeNoiseFan.value] = 1
		if np.isnan(self.table_current_row[CSVColumns.AdditiveNoiseH1.value]):
			self.table_current_row[CSVColumns.AdditiveNoiseH1.value] = 0
		if np.isnan(self.table_current_row[CSVColumns.AdditiveNoiseH2.value]):
			self.table_current_row[CSVColumns.AdditiveNoiseH2.value] = 0
		if np.isnan(self.table_current_row[CSVColumns.AdditiveNoiseFan.value]):
			self.table_current_row[CSVColumns.AdditiveNoiseFan.value] = 0
		if np.isnan(self.table_current_row[CSVColumns.NegativeSaturationH1.value]):
			self.table_current_row[CSVColumns.NegativeSaturationH1.value] = 0
		if np.isnan(self.table_current_row[CSVColumns.NegativeSaturationH2.value]):
			self.table_current_row[CSVColumns.NegativeSaturationH2.value] = 0
		if np.isnan(self.table_current_row[CSVColumns.NegativeSaturationFan.value]):
			self.table_current_row[CSVColumns.NegativeSaturationFan.value] = 0
		if np.isnan(self.table_current_row[CSVColumns.PositiveSaturationH1.value]):
			self.table_current_row[CSVColumns.PositiveSaturationH1.value] = 100
		if np.isnan(self.table_current_row[CSVColumns.PositiveSaturationH2.value]):
			self.table_current_row[CSVColumns.PositiveSaturationH2.value] = 100
		if np.isnan(self.table_current_row[CSVColumns.PositiveSaturationFan.value]):
			self.table_current_row[CSVColumns.PositiveSaturationFan.value] = 100
		if np.isnan(self.table_current_row[CSVColumns.RateSaturationH1.value]):
			self.table_current_row[CSVColumns.RateSaturationH1.value] = 1000
		if np.isnan(self.table_current_row[CSVColumns.RateSaturationH2.value]):
			self.table_current_row[CSVColumns.RateSaturationH2.value] = 1000
		if np.isnan(self.table_current_row[CSVColumns.RateSaturationFan.value]):
			self.table_current_row[CSVColumns.RateSaturationFan.value] = 1000

	def _millis(self):
		return round(time.time()*1000)

	def _assertExperimentTable(self):
		# Tests if time values are unique.
		if (self.table[CSVColumns.Time.value].count() != self.table[CSVColumns.Time.value].nunique()):
			print(TecolabMessages.ErrorMessage1)
			exit()
		# Tests if delta t in the experiment is less than the period.
		if (self.table[CSVColumns.Time.value].diff().min() < self.period):
			print(TecolabMessages.ErrorMessage2)
			exit()
		# Tests if there are negative values of t.
		if (self.table[CSVColumns.Time.value].min() < 0):
			print(TecolabMessages.ErrorMessage3)
			exit()
		# Tests if there are absolute setpoint 1 that exceeds 100°C.
		if (self.table[CSVColumns.SetPoint1Absolute.value].max() > 100):
			print(TecolabMessages.ErrorMessage4)
			exit()
		# Tests if there are absolute setpoint 2 that exceeds 100°C.
		if (self.table[CSVColumns.SetPoint2Absolute.value].max() > 100):
			print(TecolabMessages.ErrorMessage5)
			exit()
		# Tests if there are negative values of relative setpoint 1.
		if (self.table[CSVColumns.SetPoint1Relative.value].min() < 0):
			print(TecolabMessages.WarningMessage1)
		# Tests if there are negative values of relative setpoint 2.
		if (self.table[CSVColumns.SetPoint1Relative.value].min() < 0):
			print(TecolabMessages.WarningMessage2)
		if (self.table[CSVColumns.RateSaturationH1.value].min() < 0):
			print(TecolabMessages.ErrorMessage6)
			exit()
		if (self.table[CSVColumns.RateSaturationH2.value].min() < 0):
			print(TecolabMessages.ErrorMessage7)
			exit()
		if (self.table[CSVColumns.RateSaturationFan.value].min() < 0):
			print(TecolabMessages.ErrorMessage8)
			exit()