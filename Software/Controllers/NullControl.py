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

## NullControl - Does nothing
import control as ctrl
import math

## Define TeCoLab variable class
class Controller:
	def __init__(self, T = 1):
		self.T = T # Sampling period [x200 ms]
		self.counter = 0
		self.lastControlAction = (0, 0, 0)

	# When programming a new controller, change the following method
	def controlAction(self, setPoints, temperatures):
		# Control algorithm input variables
		sp1_abs = setPoints[0]
		sp2_abs = setPoints[1]
		sp1_rel = setPoints[2]
		sp2_rel = setPoints[3]
		tem_He1 = temperatures[0]
		tem_He2 = temperatures[1]
		tem_Amb = temperatures[2]

		# Assert input variables (avoiding NaN in set points)
		if math.isnan(sp1_abs):
			sp1_abs = 0;
		if math.isnan(sp2_abs):
			sp2_abs = 0;
		if math.isnan(sp1_rel):
			sp1_rel = 0;
		if math.isnan(sp2_rel):
			sp2_rel = 0;

		# Control algorithm output variables
		H1PWM = 0
		H2PWM = 0
		CoolerPWM = 0

		# Control algorithm computation
		# No computation for this controller

		# Control algorithm return
		return H1PWM, H2PWM, CoolerPWM

	# When programming a new controller, DO NOT change the following methods
	def _control(self, setPoints, temperatures):
		self.counter += 1
		if self.counter >= 0:
			self._resetCounter()
			self.lastControlAction = self.controlAction(setPoints, temperatures)
			return self.lastControlAction, +1 # +1 represents new control action
		else:
			return self.lastControlAction, 0 # 0 represents no new control action

	def _resetCounter(self):
		self.counter = -self.T