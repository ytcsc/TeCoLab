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

from Modules.Utils.continuous_time_LTI import Controller
import control

class Controller(Controller):
	def __init__(self):
		super().__init__()

	def set_PID(self, Kp: float, Ki: float, Kd: float, p: float = 100, **kwargs):
		if (Kp == 0):
			numerator = [0]
			denominator = [1]
		elif (Ki == 0) and (Kd == 0): # P
			numerator = [Kp]
			denominator = [1]
		elif (Ki == 0) and (Kd != 0): # PD
			numerator = [Kp*(1+Kd*p), p]
			denominator = [1, p]
		elif (Ki != 0) and (Kd == 0): # PI
			numerator = [Kp, Kp*Ki]
			denominator = [1, 0]
		elif (Ki != 0) and (Kd != 0): # PID
			numerator = [Kp*(1+Kd*p), Kp*(p+Ki), Kp*Ki*p]
			denominator = [1, p, 0]
		system = control.TransferFunction(numerator, denominator, 0)
		index = self.set_LTI(system, **kwargs)
		return index