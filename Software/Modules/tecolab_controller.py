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

import time

class Controller:
	def __init__(self):
		self.setpoint_abs_1 = 0
		self.setpoint_abs_2 = 0
		self.setpoint_rel_1 = 0
		self.setpoint_rel_2 = 0
		self.temperature_heater_1 = 0
		self.temperature_heater_2 = 0
		self.temperature_ambient = 0
		self.actuator_heater_1 = 0
		self.actuator_heater_2 = 0
		self.actuator_fan = 0

	def control_setup(self):
		pass

	def control_action(self):
		pass

	def control_signal(self):
		return True

	def _control_compute(self, setPoints, temperatures):
		self.setpoint_abs_1 = setPoints[0]
		self.setpoint_abs_2 = setPoints[1]
		self.setpoint_rel_1 = setPoints[2]
		self.setpoint_rel_2 = setPoints[3]
		self.temperature_heater_1 = temperatures[0]
		self.temperature_heater_2 = temperatures[1]
		self.temperature_ambient = temperatures[2]
		self.actuator_heater_1 = []
		self.actuator_heater_2 = []
		self.actuator_fan = []
		control_signal = 0
		t_1 = round(time.time()*1000)
		if (self.control_signal() == True):
			control_signal = 1
			self.control_action()
		t_2 = round(time.time()*1000)
		return (self.actuator_heater_1, self.actuator_heater_2, self.actuator_fan), control_signal, (t_2 - t_1)