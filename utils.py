import datetime
import gzip
import pandas
from matplotlib.dates import date2num


def open_json(filename, verbose=False):
    if filename[-3:] == '.gz':
        d = gzip.open(filename)
    else:
        d = open(filename)
    df = pandas.read_json(d)
    d.close()
    """
    I want the DataFrame's columns to be in this specific order.
    Also because otherwise I don't know which order they are and I have to use the debugger to find out
    """
    df = df[['date', 'open', 'high', 'low', 'close', 'quoteVolume', 'volume', 'weightedAverage']]
    df['date'] = pandas.to_datetime(df['date'], unit='s')
    # df.set_index('date', inplace=True)  # setting as index makes it possible to say df['2014-08-18'] which we don't really need
    df['date'] = df['date'].map(date2num)  # matplotlib likes dates in this format

    if verbose:
        print(df.head())
        print(df.memory_usage())

    return df

def between(number1, number2, n):
    boundaries = [number1, number2]
    boundaries.sort()
    return boundaries[0] <= n <= boundaries[1]
