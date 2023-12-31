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

from Modules.Utils.discrete_time_LTI import Controller
import control

class Controller(Controller):
	def __init__(self):
		super().__init__()
		self.discretization_period = 0.2
		self.continuous_time_LTI_list = list()

	def set_discretization_period(self, period: float):
		if (period <= 0):
			print('ERROR at continuous_time_LTI module, set_discretization_period method: period argument must be a strictly positive number.')
			exit()
		self.discretization_period = period

	def set_LTI(self, system, **kwargs):
		if control.isctime(system) == False:
			print('ERROR at continuous_time_LTI module, set_LTI method: system argument must be a continuous-time LTI system.')
			exit()
		method = kwargs.get('method', 'zoh')
		alpha = kwargs.get('alpha', None)
		prewarp_frequency = kwargs.get('prewarp_frequency', None)
		self.continuous_time_LTI_list.append(system)
		print('CT system = ', system)
		system = control.sample_system(system, self.discretization_period, method = method, alpha = alpha, prewarp_frequency = prewarp_frequency)
		print('DT system = ', system)
		self.discrete_time_LTI_list.append(system)
		self._last_state.append(0)
		self._last_index = self._last_index + 1
		return self._last_index

	def get_LTI(self, index):
		if (index < 0):
			print('ERROR at discrete_time_LTI module, get_LTI method: index argument must be a nonnegative number.')
			exit()
		if (index > self._last_index):
			return None
		else:
			return self.continuous_time_LTI_list[index], self.discrete_time_LTI_list[index]