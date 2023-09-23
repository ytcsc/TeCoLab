import pandas as pd
import numpy as np
from typing import Tuple
import control
from control.matlab import step
import matplotlib.pyplot as plt
import easygui

def check_data(df):
    """
    Check if the DataFrame represents a step response.

    Args:
        df (pd.DataFrame): The DataFrame to check.

    """

    assert 'H1_ADD_NOISE' in df.columns, "Invalid experiment CSV file"

    df_test = df.copy()
    df_test.drop_duplicates(subset='H1_ADD_NOISE', keep='first', inplace=True)
    nonzero_points = df_test[df_test['H1_ADD_NOISE'] != 0]
    assert len(nonzero_points) == 1, "The experiment is not a step response"


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load data from a CSV file.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: The loaded data as a pandas DataFrame.
    """
    df = pd.read_csv(file_path)
    check_data(df)
    df.set_index('TIME', inplace=True)
    starting_time = df.loc[df['H1_ADD_NOISE'] > 0.0].index.values[0]
    df = df.loc[starting_time:]
    df.index = (df.index - starting_time) / 1000
    return df

def calculate_parameters(df: pd.DataFrame) -> Tuple[float, float, float, float, pd.DataFrame]:
    """
    Calculate system parameters and extract relevant data.

    Args:
        df (pd.DataFrame): The input data as a pandas DataFrame.

    Returns:
        Tuple[float, float, float, float, pd.DataFrame]: A tuple containing system parameters
        (K, L, TAU, P, offset) and the modified DataFrame.
    """
    K = 0.0
    L = 0.0
    TAU = 0.0
    P = 0.0
    offset = 0.0

    offset = df['H1_TEMP'].values[0]
    df.loc[:,'H1_TEMP'] = df['H1_TEMP'] - offset
    window = int(df.index.max() / 10)
    rolling_mean = df.rolling(window).mean()
    max_value = rolling_mean.max()[0]

    P = df.loc[df['H1_ADD_NOISE'] > 0]['H1_ADD_NOISE'].values[0]
    K = df.loc[df['H1_TEMP'] > max_value * 0.99]['H1_TEMP'].mean() / P
    L = df.loc[df['H1_TEMP'] > 0.0].index.values[0]
    TAU = df.loc[df['H1_TEMP'] > (0.632 * max_value)].index.values[0]

    return K, L, TAU, P, offset

def simulate_and_plot(df: pd.DataFrame, H: control.TransferFunction, K: float, L: float, TAU: float, P: float, offset: float) -> None:
    """
    Simulate the system and plot the results.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        H (control.TransferFunction): The system transfer function.
        K (float): The system gain.
        L (float): The system time delay.
        TAU (float): The system time constant.
        P (float): The system additive noise magnitude.
        offset (float, optional): The vertical offset to apply to the y-values.
    """

    sampling_interval = df.index[1] - df.index[0]

    t = np.arange(0, df.index.max(), sampling_interval)
    (y, t) = step(H, T=t)
    y = y + offset

    plt.figure(figsize=(10, 6))
    expression = f'$G(s) = \\frac{{{K*P}e^{{-{L}s}}}}{{{TAU}s + 1}}$'
    plt.plot(df['H1_TEMP'], label='System', linewidth=3)
    plt.plot(t, y, label='Simulated system')
    plt.xlabel("Time [s]")
    plt.ylabel("Temperature [ºC]")
    plt.title(expression)
    plt.grid(color='b', linestyle='-', linewidth=0.1)
    legend_text = f'$K = {K}$\n$L = {L}$\n$\\tau = {TAU}$\n$P = {P}$'
    plt.text(0.75, 0.2, legend_text, bbox=dict(facecolor='white', alpha=0.7), transform=plt.gca().transAxes)

    plt.legend()
    plt.show()

def main() -> None:

    path = easygui.fileopenbox()
    df = load_data(path)

    K, L, TAU, P, offset = calculate_parameters(df.copy())
    n_pade = 10
    (num_pade, den_pade) = control.pade(L, n_pade)
    H_pade = control.tf(num_pade, den_pade)

    num = [K * P]
    den = [TAU, 1]
    H_without_delay = control.tf(num, den)

    H_with_delay = control.series(H_pade, H_without_delay)

    simulate_and_plot(df, H_with_delay, K, L, TAU, P, offset)

if __name__ == "__main__":
    main()