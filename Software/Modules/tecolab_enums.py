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

class CSVColumns(Enum):
    Time = 'TIME'
    TemperatureH1 = 'H1_TEMP'
    TemperatureH2 = 'H2_TEMP'
    TemperatureAMB = 'AMB_TEMP'
    SetPoint1Absolute = 'SP1_ABS'
    SetPoint2Absolute = 'SP2_ABS'
    SetPoint1Relative = 'SP1_REL'
    SetPoint2Relative = 'SP2_REL'
    MultiplicativeNoiseH1 = 'H1_MUL_NOISE'
    MultiplicativeNoiseH2 = 'H2_MUL_NOISE'
    MultiplicativeNoiseFan = 'F_MUL_NOISE'
    AdditiveNoiseH1 = 'H1_ADD_NOISE'
    AdditiveNoiseH2 = 'H2_ADD_NOISE'
    AdditiveNoiseFan = 'F_ADD_NOISE'
    NegativeSaturationH1 = 'H1_NEG_SAT'
    NegativeSaturationH2 = 'H2_NEG_SAT'
    NegativeSaturationFan = 'F_NEG_SAT'
    PositiveSaturationH1 = 'H1_POS_SAT'
    PositiveSaturationH2 = 'H2_POS_SAT'
    PositiveSaturationFan = 'F_POS_SAT'
    RateSaturationH1 = 'H1_RATE_SAT'
    RateSaturationH2 = 'H2_RATE_SAT'
    RateSaturationFan = 'F_RATE_SAT'
    ComputedPWMH1 = 'H1_C_PWM'
    ComputedPWMH2 = 'H2_C_PWM'
    ComputedPWMFan = 'F_C_PWM'
    DisturbedPWMH1 = 'H1_D_PWM'
    DisturbedPWMH2 = 'H2_D_PWM'
    DisturbedPWMFan = 'F_D_PWM'
    NewControlAction = 'CTRL_ACTION'
    ControlActionComputationTime = 'CTRL_TIME'