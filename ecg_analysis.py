import json
import pandas as pd
import scipy as sp
import scipy.signal
import matplotlib.pyplot as plt


def read_csv(ecg_path):
    """Read in .csv file of data

    This function uses the pandas packaged to read-in a .csv file to be used
    in python. Each column is also labeled as 'time' and 'voltage'.

    :param ecg_path: string of the .csv file path to be read

    :returns: a pandas dataframe of time and voltage values and the filename
    """
    df = pd.read_csv(ecg_path, header=None)
    df.columns = ['time', 'voltage']
    return df


def duration(df):
    """Finds time duration of ECG strip

    This function subtracts the minimum time value from the maximum time
    value and returns the duration of the ECG strip.

    :param df: a dataframe of floats of ecg data

    :returns: a float of the duration of the ECG strip in seconds
    """
    max_time = max(df['time'])
    min_time = min(df['time'])
    duration = max_time - min_time
    return duration


def num_beats(df):
    """Find the number of beats in the strip

    This function uses the scipy find_peaks function to find the locations
    of the peaks in each ECG strip. The number of beats is then calculated to
    find the num_beats output.

    :param df: a dataframe of floats of ecg data

    :returns: a single integer of the number of total beats in a strip
    """
    peaks = scipy.signal.find_peaks(df['voltage'], height=0.6,
                                    distance=200)
    num_beats = len(peaks[0])
    return num_beats


def mean_hr_bpm(num_beats, duration):
    """Average heart rate calculation

    This is a simple function that converts seconds to minutes and divides
    the total number of beats found by the total minutes in the strip.

    :param num_beats: a single integer of the number of total beats in a strip
    :param duration: a single float for the time duration of the strip

    :returns: a single float of the average heart rate in the strip
    """
    minutes = duration/60
    mean_hr_bpm = num_beats/minutes
    return mean_hr_bpm


def plot_ecg(df):
    """ Creates jpg image of ecg trace

    This function uses the matplotlib package to create a plot of the ecg data
    file that is entered. The plot is then saved as 'ecg_plot.jpg' in the
    directory and cleared after saving. This allows for overwriting of the
    saved plot if the function is run multiple times.

    :param df: a dataframe of floats of ecg data

    :returns: None
    """
    plt.figure(0)
    plt.plot(df['time'], df['voltage'])
    plt.xlabel('time (s)')
    plt.ylabel('voltage (mV)')
    plt.title('ECG Data')
    plt.savefig('ecg_plot.jpg')
    plt.clf()


if __name__ == "__main__":
    df = read_csv()
    duration = duration(df)
    num_beats = num_beats(df)
    mean_hr_bpm = mean_hr_bpm(num_beats, duration)
    plot_ecg(df)
