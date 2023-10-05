import pandas as pd
import numpy as np
from typing import Tuple
import control
from control.matlab import step
import matplotlib.pyplot as plt
import easygui

def check_data(dataframe):
    """
    Check if the DataFrame represents a step response.

    Args:
        dataframe (pd.DataFrame): The DataFrame to check.

    """

    assert 'H1_ADD_NOISE' in dataframe.columns, "Invalid experiment CSV file"

    dataframe_test = dataframe.copy()
    dataframe_test.drop_duplicates(subset='H1_ADD_NOISE', keep='first', inplace=True)
    nonzero_points = dataframe_test[dataframe_test['H1_ADD_NOISE'] != 0]
    assert len(nonzero_points) == 1, "The experiment is not a step response"


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load data from a CSV file.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: The loaded data as a pandas DataFrame.
    """
    dataframe = pd.read_csv(file_path)
    check_data(dataframe)
    dataframe.set_index('TIME', inplace=True)
    starting_time = dataframe.loc[dataframe['H1_ADD_NOISE'] > 0.0].index.values[0]
    dataframe = dataframe.loc[starting_time:]
    dataframe.index = (dataframe.index - starting_time) / 1000
    return dataframe

def identification(dataframe: pd.DataFrame) -> Tuple[float, float, float, float, float]:
    """
    Calculate system parameters and extract relevant data.

    Args:
        dataframe (pd.DataFrame): The input data as a pandas DataFrame.

    Returns:
        Tuple[float, float, float, float, pd.DataFrame]: A tuple containing system parameters
        (static_gain, time_delay, time_constant, step_power, initial_temperature)
    """

    initial_temperature = dataframe['H1_TEMP'].values[0]
    dataframe.loc[:,'H1_TEMP'] = dataframe['H1_TEMP'] - initial_temperature
    window = int(dataframe.index.max() / 10)
    moving_average = dataframe.rolling(window).mean()
    max_value = moving_average.max()[0]

    step_power = dataframe.loc[dataframe['H1_ADD_NOISE'] > 0]['H1_ADD_NOISE'].values[0]
    static_gain = round((max_value / step_power), 4)
    time_delay = dataframe.loc[dataframe['H1_TEMP'] > 0.0].index.values[0]
    time_constant = dataframe.loc[dataframe['H1_TEMP'] > (0.632 * max_value)].index.values[0] - time_delay

    return static_gain, time_delay, time_constant, step_power, initial_temperature

def simulate_and_plot(
        dataframe: pd.DataFrame,
        transfer_function: control.TransferFunction,
        static_gain: float,
        time_delay: float,
        time_constant: float,
        step_power: float,
        initial_temperature: float
 ):
    """
    Simulate the system and plot the results.

    Args:
        dataframe (pd.DataFrame): The DataFrame containing the data.
        transfer_function (control.TransferFunction): The system transfer function.
        static_gain (float): The system gain.
        time_delay (float): The system time delay.
        time_constant (float): The system time constant.
        step_power (float): The system additive noise magnitude.
        initial_temperature (float, optional): The vertical offset to apply to the y-values.
    """

    sampling_interval = dataframe.index[1] - dataframe.index[0]

    t = np.arange(0, dataframe.index.max(), sampling_interval)
    (y, t) = step(transfer_function, T=t)
    y = y + initial_temperature

    plt.figure(figsize=(10, 6))
    plt.plot(dataframe['H1_TEMP'], label='Experiment data', linewidth=3)
    plt.plot(t, y, label='Identified system')
    plt.xlabel("Time [s]")
    plt.ylabel("Temperature [ºC]")
    expression = f'$G(s) = \\frac{{{static_gain}e^{{-{time_delay}s}}}}{{{time_constant}s + 1}}$'
    plt.title(expression)
    plt.grid(color='b', linestyle='-', linewidth=0.1)
    legend_text = f'$K = {static_gain}$\n$L = {time_delay}$\n$\\tau = {time_constant}$\n$P = {step_power}$'
    plt.text(0.75, 0.2, legend_text, bbox=dict(facecolor='white', alpha=0.7), transform=plt.gca().transAxes)

    plt.legend()
    plt.show()

def main() -> None:

    path = easygui.fileopenbox()
    dataframe = load_data(path)

    static_gain, time_delay, time_constant, step_power, initial_temperature = identification(dataframe.copy())
    n_pade = 10
    (num_pade, den_pade) = control.pade(time_delay, n_pade)
    transfer_function_pade = control.tf(num_pade, den_pade)

    num = [static_gain * step_power]
    den = [time_constant, 1]
    transfer_function = control.tf(num, den)

    transfer_function_with_delay = control.series(transfer_function_pade, transfer_function)

    simulate_and_plot(
        dataframe,
        transfer_function_with_delay,
        static_gain,
        time_delay,
        time_constant,
        step_power,
        initial_temperature
    )

if __name__ == "__main__":
    main()