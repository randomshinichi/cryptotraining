import datetime
import gzip
import pandas
from matplotlib.dates import date2num


class DataReader:
    def __init__(self, filename, verbose=False):
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
        self.df = df[['date', 'open', 'high', 'low', 'close', 'quoteVolume', 'volume', 'weightedAverage']]
        self.df['date'] = pandas.to_datetime(self.df['date'], unit='s')
        # self.df.set_index('date', inplace=True)  # setting as index makes it possible to say df['2014-08-18'] which we don't really need
        self.df['date'] = self.df['date'].map(date2num)  # matplotlib likes dates in this format

        if verbose:
            print(self.df.head())
            print(self.df.memory_usage())

    def copy(self, i1=None, i2=None):
        return self.df.copy().iloc[i1:i2]


def between(number1, number2, n):
    boundaries = [number1, number2]
    boundaries.sort()
    return boundaries[0] <= n <= boundaries[1]
