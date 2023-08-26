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
    ComputedPWMH1 = 'H1_C_PWM'
    ComputedPWMH2 = 'H2_C_PWM'
    ComputedPWMFan = 'F_C_PWM'
    DisturbedPWMH1 = 'H1_D_PWM'
    DisturbedPWMH2 = 'H2_D_PWM'
    DisturbedPWMFan = 'F_D_PWM'
    NewControlAction = 'CTRL_ACTION'
