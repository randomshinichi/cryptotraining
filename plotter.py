from time import sleep
import utils
from collections import deque
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick_ohlc, candlestick2_ohlc

pd.options.display.max_rows=1000
filename = 'data/USDT_BTC-1d.json.gz'
datareader = utils.DataReader(filename)


class Ichimoku:
    colours = {
        "tenkan_sen": "#0496ff",
        "kijun_sen": "#991515",
        "chikou_span": "#459915",
        "senkou_a": "#3F9340",
        "senkou_b": "#E54040"
    }
    def __init__(self, df):
        self.df = df
        self.i = 0
        self.tenkan_highs = deque(maxlen=9)
        self.tenkan_lows = deque(maxlen=9)

        self.kijun_highs = deque(maxlen=26)
        self.kijun_lows = deque(maxlen=26)

        self.chikou_span = deque(maxlen=26)

        self.senkou_b_highs = deque(maxlen=52)
        self.senkou_b_lows = deque(maxlen=52)

        self.df_ = self.df.copy()
        self.df_['tenkan_sen'] = pd.Series(np.nan)
        self.df_['kijun_sen'] = pd.Series(np.nan)
        self.df_['chikou_span'] = pd.Series(np.nan)
        self.df_['senkou_a'] = pd.Series(np.nan)
        self.df_['senkou_b'] = pd.Series(np.nan)


    @staticmethod
    def avg(highs, lows):
        # Returns the average only if both deques are full
        if len(highs) == highs.maxlen and len(lows) == lows.maxlen:
            return ((max(highs) + min(lows)) / 2)
        return None

    def update_df(self, i, tenkan, kijun, chikou, senkou_a, senkou_b):
        self.df_.loc[i, 'tenkan_sen'] = tenkan
        self.df_.loc[i, 'kijun_sen'] = kijun
        if i - 26 >= 0:
            self.df_.loc[i - 26, 'chikou_span'] = chikou
        self.df_.loc[i + 26, 'senkou_a'] = senkou_a
        self.df_.loc[i + 26, 'senkou_b'] = senkou_b


    def run(self):
        while self.i < len(self.df):
            self.tenkan_highs.append(self.df.iloc[self.i]['high'])
            self.tenkan_lows.append(self.df.iloc[self.i]['low'])

            self.kijun_highs.append(self.df.iloc[self.i]['high'])
            self.kijun_lows.append(self.df.iloc[self.i]['low'])
            tenkan = self.avg(self.tenkan_highs, self.tenkan_lows)
            kijun = self.avg(self.kijun_highs, self.kijun_lows)

            if tenkan and kijun:
                senkou_a = (tenkan + kijun) / 2
            else:
                senkou_a = None

            self.senkou_b_highs.append(self.df.iloc[self.i]['high'])
            self.senkou_b_lows.append(self.df.iloc[self.i]['low'])

            senkou_b = self.avg(self.senkou_b_highs, self.senkou_b_lows)

            chikou = self.df.iloc[self.i]['close']

            self.update_df(self.i, tenkan, kijun, chikou, senkou_a, senkou_b)
            self.i += 1

    def window(self, i1, i2):
        # we include 26 extra rows from the future to plot the senkou
        window = self.df_.copy()[i1:i2+26]

        # need to delete chikou_span data from the future and past 26 days
        window['chikou_span'].iloc[-52:] = np.nan

        # we have 26 extra rows from the future with data we don't want to see.
        # delete all future price data if they're not in columns senkou_a, senkou_b
        window.loc[i2:, window.columns.difference(['date', 'senkou_a', 'senkou_b'])] = np.nan
        return window

class Display:
    def __init__(self, source):
        self.left = 0
        self.right = 100
        self.source = source
        self.df = self.source.window(self.left, self.right)

        self.fig, self.ax = plt.subplots(1, 1)

    def update_window(self, i):
        self.right += i
        self.left += i

        self.df = self.source.window(self.left, self.right)

    def on_keyboard(self, event):
        if event.key == 'right':
            self.update_window(1)
        elif event.key == 'left':
            self.update_window(-1)
        elif event.key == 'alt+right':
            self.update_window(100)
        elif event.key == 'alt+left':
            self.update_window(-100)
        else:
            return

        self.plot()

    def plot(self):
        # make it very clear which figure we're modifying
        plt.figure(self.fig.number)

        # Converts raw matplotlib numbers to dates
        self.ax.clear()
        self.ax.xaxis_date()
        self.ax.grid(color='gray', linestyle='dashed', linewidth=1)
        self.ax.set_title(filename)
        plt.xlabel("Time")
        plt.ylabel("Price")
        candlestick_ohlc(self.ax, self.df.values, width=0.5, colorup='g', colordown='r')
        # Took me HOURS to figure out that I need list() otherwise ax.plot doesn't understand numpy.ndarray, and plots a vertical line
        x = list(self.df['date'].values)
        self.ax.plot(x, self.df['tenkan_sen'].values, color=self.source.colours["tenkan_sen"], linewidth=0.7)
        self.ax.plot(x, self.df['kijun_sen'].values, color=self.source.colours["kijun_sen"], linewidth=0.7)
        self.ax.plot(x, self.df['chikou_span'].values, color=self.source.colours["chikou_span"], linewidth=0.7)
        self.ax.plot(x, self.df['senkou_a'].values, color=self.source.colours["senkou_a"], linewidth=0.3)
        self.ax.plot(x, self.df['senkou_b'].values, color=self.source.colours["senkou_b"], linewidth=0.3)
        self.ax.fill_between(x, self.df['senkou_a'].values, self.df['senkou_b'].values, where=self.df['senkou_a'].values>=self.df['senkou_b'].values, facecolor=(0, 1, 0, 0.1), interpolate=True)
        self.ax.fill_between(x, self.df['senkou_a'].values, self.df['senkou_b'].values, where=self.df['senkou_a'].values<=self.df['senkou_b'].values, facecolor=(1, 0, 0, 0.1), interpolate=True)
        
        plt.legend()
        plt.gcf().canvas.mpl_connect('key_press_event', self.on_keyboard)
        plt.gcf().canvas.draw()

raw_data = datareader.copy()
ichi = Ichimoku(raw_data)
print("running Ichimoku")
ichi.run()
print("initializing display")
disp = Display(ichi)

disp.plot()
plt.show()