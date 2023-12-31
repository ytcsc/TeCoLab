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

from Modules.Utils.periodic_controller import Controller
import control

class Controller(Controller):
	def __init__(self):
		super().__init__()
		self.discrete_time_LTI_list = list()
		self._last_state = list()
		self._last_index = -1;

	def set_LTI(self, system):
		if control.isdtime(system) == False:
			print('ERROR at discrete_time_LTI module, set_LTI method: system argument must be a discrete-time LTI system.')
			exit()
		system = control.ss(system)
		self._last_index = self._last_index + 1
		self.discrete_time_LTI_list.append(system)
		self._last_state.append(0)
		return self._last_index

	def get_LTI(self, index: int):
		if (index < 0):
			print('ERROR at discrete_time_LTI module, get_LTI method: index argument must be a nonnegative number.')
			exit()
		if (index > self._last_index):
			return None
		else:
			return self.discrete_time_LTI_list[index]

	def LTI_compute(self, index: int, u: float):
		if (index < 0):
			print('ERROR at discrete_time_LTI module, LTI_compute method: index argument must be a nonnegative number.')
			exit()
		if (index > self._last_index):
			print('ERROR at discrete_time_LTI module, LTI_compute method: index argument out of bounds.')
			exit()
		(_, output, X) = control.forced_response(self.discrete_time_LTI_list[index], T = [0, 1], U = [u, u], X0 = self._last_state[index], return_x = True)
		self._last_state[index] = [ls[1] for ls in X]
		return output[0]