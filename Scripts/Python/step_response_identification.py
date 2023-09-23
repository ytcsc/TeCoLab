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

def calculate_parameters(dataframe: pd.DataFrame) -> Tuple[float, float, float, float, float]:
    """
    Calculate system parameters and extract relevant data.

    Args:
        dataframe (pd.DataFrame): The input data as a pandas DataFrame.

    Returns:
        Tuple[float, float, float, float, pd.DataFrame]: A tuple containing system parameters
        (K, L, TAU, P, offset)
    """

    offset = dataframe['H1_TEMP'].values[0]
    dataframe.loc[:,'H1_TEMP'] = dataframe['H1_TEMP'] - offset
    window = int(dataframe.index.max() / 10)
    rolling_mean = dataframe.rolling(window).mean()
    max_value = rolling_mean.max()[0]

    P = dataframe.loc[dataframe['H1_ADD_NOISE'] > 0]['H1_ADD_NOISE'].values[0]
    K = dataframe.loc[dataframe['H1_TEMP'] > max_value * 0.99]['H1_TEMP'].mean() / P
    L = dataframe.loc[dataframe['H1_TEMP'] > 0.0].index.values[0]
    TAU = dataframe.loc[dataframe['H1_TEMP'] > (0.632 * max_value)].index.values[0]

    return K, L, TAU, P, offset

def simulate_and_plot(dataframe: pd.DataFrame, H: control.TransferFunction, K: float, L: float, TAU: float, P: float, offset: float):
    """
    Simulate the system and plot the results.

    Args:
        dataframe (pd.DataFrame): The DataFrame containing the data.
        H (control.TransferFunction): The system transfer function.
        K (float): The system gain.
        L (float): The system time delay.
        TAU (float): The system time constant.
        P (float): The system additive noise magnitude.
        offset (float, optional): The vertical offset to apply to the y-values.
    """

    sampling_interval = dataframe.index[1] - dataframe.index[0]

    t = np.arange(0, dataframe.index.max(), sampling_interval)
    (y, t) = step(H, T=t)
    y = y + offset

    plt.figure(figsize=(10, 6))
    plt.plot(dataframe['H1_TEMP'], label='System', linewidth=3)
    plt.plot(t, y, label='Simulated system')
    plt.xlabel("Time [s]")
    plt.ylabel("Temperature [ºC]")
    expression = f'$G(s) = \\frac{{{K*P}e^{{-{L}s}}}}{{{TAU}s + 1}}$'
    plt.title(expression)
    plt.grid(color='b', linestyle='-', linewidth=0.1)
    legend_text = f'$K = {K}$\n$L = {L}$\n$\\tau = {TAU}$\n$P = {P}$'
    plt.text(0.75, 0.2, legend_text, bbox=dict(facecolor='white', alpha=0.7), transform=plt.gca().transAxes)

    plt.legend()
    plt.show()

def main() -> None:

    path = easygui.fileopenbox()
    dataframe = load_data(path)

    K, L, TAU, P, offset = calculate_parameters(dataframe.copy())
    n_pade = 10
    (num_pade, den_pade) = control.pade(L, n_pade)
    H_pade = control.tf(num_pade, den_pade)

    num = [K * P]
    den = [TAU, 1]
    H_without_delay = control.tf(num, den)

    H_with_delay = control.series(H_pade, H_without_delay)

    simulate_and_plot(dataframe, H_with_delay, K, L, TAU, P, offset)

if __name__ == "__main__":
    main()