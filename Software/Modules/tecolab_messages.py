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

from enum import Enum

class TecolabMessages(Enum):
    ErrorMessage1 = 'ERROR: Experiment table has duplicate values in time column.'
    ErrorMessage2 = 'ERROR: Experiment table has time intervals smaller than the specified period.'
    ErrorMessage3 = 'ERROR: Experiment table has negative values of time.'
    ErrorMessage4 = 'ERROR: Experiment table has absolute values of setpoint 1 exceeding 100°C.'
    ErrorMessage5 = 'ERROR: Experiment table has absolute values of setpoint 2 exceeding 100°C.'
    ErrorMessage6 = 'ERROR: Experiment table has nonpositive values of rate saturation for heater 1.'
    ErrorMessage7 = 'ERROR: Experiment table has nonpositive values of rate saturation for heater 2.'
    ErrorMessage8 = 'ERROR: Experiment table has nonpositive values of rate saturation for fan.'

    WarningMessage1 = 'WARNING: Experiment table has negative values of relative setpoint 1.'
    WarningMessage2 = 'WARNING: Experiment table has negative values of relative setpoint 2.'

    Message1 = 'No TeCoLab device found. Terminating program.'
    Message2 = 'Loading experiment: '
    Message3 = 'Experiment table:'
    Message4 = 'Identifying serial devices connected:'
    Message5 = 'No serial devices connected. Terminating program.'
    Message6 = 'Searching for TeCoLab device:'
    Message7 = 'Testing port: '
    Message8 = 'TeCoLab device found at port: '