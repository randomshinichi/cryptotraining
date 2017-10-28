from collections import deque
import pandas as pd
import numpy as np


class RSI:
    """
    TODO:
    lows_decreasing_steadily()
    Figures out whether the lows in the RSI have been decreasing steadily. Period is configurable.
    I don't actually need this function. Because I'm only going to buy when RSI is oversold, i.e. <30.
    And if it's oversold, the lows have already been decreasing steadily.
    """

    def __init__(self, df, length=14):
        """
        df = Pandas Dataframe
        pair = Coin's name. Useful when something goes wrong in here,
        and you need to know which coin it is.
        """
        self.df = df.reset_index()
        self.n = {
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
            "basevolume": "basevolume"
        }
        self.length = length
        self.candles = deque(maxlen=self.length)
        self.gains = deque(maxlen=self.length)
        self.losses = deque(maxlen=self.length)
        self.gain_avg_prev = 0
        self.losses_avg_prev = 0
        self.df['rsi'] = pd.Series(np.nan)

        self.process()

    def process(self):
        def rsi(gain_avg, losses_avg):
            # Sometimes you get dirty data, especially at the beginning of a coin's life
            try:
                rs = gain_avg / losses_avg
            except ZeroDivisionError:
                rs = 0

            rsi = 100 - (100 / (1 + rs))
            return rsi

        for i, row in self.df[1:].iterrows():
            gain = 0
            loss = 0

            try:
                change = row['close'] - self.df.loc[i - 1, 'close']
            except TypeError as e:
                # print("NaNs in price data")
                change = np.nan

            if change > 0:
                gain = change
            elif change < 0:
                loss = abs(change)

            self.gains.append(gain)
            self.losses.append(loss)

            # if i < 14, keep iterating until the deques are full
            if i < self.length:
                continue

            if i == self.length:
                gain_avg = sum(self.gains) / len(self.gains)
                losses_avg = sum(self.losses) / len(self.losses)

            elif i > self.length:
                gain_avg = (13 * self.gain_avg_prev + self.gains[-1]) / self.length
                losses_avg = (13 * self.losses_avg_prev + self.losses[-1]) / self.length

            self.gain_avg_prev = gain_avg
            self.losses_avg_prev = losses_avg

            self.df.loc[i, 'rsi'] = rsi(gain_avg, losses_avg)

    def is_oversold(self, period=1):
        """
        Returns whether the RSI has been <30 for the past (period) candles.
        Because if it only returns whether the current candle's RSI is oversold,
        that doesn't tell us much by itself.
        """
        window = self.df[-period:]
        res = []  # [True, False, False, True, True]... to be ANDed later
        for i, row in window.iterrows():
            res.append(row['rsi'] <= 30)

        return all(res)

    def is_increasing(self, period=21):
        """
        for 1d timeframe, a good period over which this calculation
        should be run is 21 days.
        """

        # .loc[] does not work with negative indices.
        # So if we want the last 10 datapoints and the df is 1000 long,
        # we need to go .loc[990:, 'rsi']
        period_from_last = len(self.df) - period
        window = self.df.loc[period_from_last:, 'rsi']

        # split the lookup window into 2
        window_1 = window[:round(len(window)/2)]
        window_2 = window[round(len(window)/2):]

        # if the 1st window's avg is lower than the 2nd window's, Then
        # the RSI must have been rising, right/
        return window_1.mean() <= window_2.mean()

class Ichimoku:
    colours={
        "tenkan_sen": "#0496ff",
        "kijun_sen": "#991515",
        "chikou_span": "#459915",
        "senkou_a": "#3F9340",
        "senkou_b": "#E54040"
    }
    def __init__(self, df):
        """
        df = Pandas Dataframe
        pair = Coin's name. Useful when something goes wrong in here,
        and you need to know which coin it is.
        """
        # if df has an index, we don't want it.
        # Because loc is the best way to select individual elements in the 2D
        # array, since iloc won't let you select the column.
        self.df=df.reset_index()

        self.n={
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
            "basevolume": "basevolume"
        }
        self.tenkan_highs=deque(maxlen=9)
        self.tenkan_lows=deque(maxlen=9)

        self.kijun_highs=deque(maxlen=26)
        self.kijun_lows=deque(maxlen=26)

        self.chikou_span=deque(maxlen=26)

        self.senkou_b_highs=deque(maxlen=52)
        self.senkou_b_lows=deque(maxlen=52)

        self.df['tenkan_sen']=pd.Series(np.nan)
        self.df['kijun_sen']=pd.Series(np.nan)
        self.df['chikou_span']=pd.Series(np.nan)
        self.df['senkou_a']=pd.Series(np.nan)
        self.df['senkou_b']=pd.Series(np.nan)

        self.process()

    def update_df(self, i, tenkan, kijun, chikou, senkou_a, senkou_b):
        if i - 26 >= 0:
            self.df.loc[i - 26, 'chikou_span']=chikou

        self.df.loc[i, ['tenkan_sen', 'kijun_sen']]=(tenkan, kijun)
        self.df.loc[i + 26, ['senkou_a', 'senkou_b']]=(senkou_a, senkou_b)

    def process(self):
        def avg(highs, lows):
            # Returns the average only if both deques are full
            if len(highs) == highs.maxlen and len(lows) == lows.maxlen:
                return ((max(highs) + min(lows)) / 2)
            return None
        for i, row in self.df.iterrows():
            hi=self.df.loc[i, self.n["high"]]
            lo=self.df.loc[i, self.n["low"]]

            self.tenkan_highs.append(hi)
            self.tenkan_lows.append(lo)

            self.kijun_highs.append(hi)
            self.kijun_lows.append(lo)
            tenkan=avg(self.tenkan_highs, self.tenkan_lows)
            kijun=avg(self.kijun_highs, self.kijun_lows)

            if tenkan and kijun:
                senkou_a=(tenkan + kijun) / 2
            else:
                senkou_a=None

            self.senkou_b_highs.append(hi)
            self.senkou_b_lows.append(lo)

            senkou_b=avg(self.senkou_b_highs, self.senkou_b_lows)

            chikou=self.df.loc[i, self.n["close"]]

            self.update_df(i, tenkan, kijun, chikou, senkou_a, senkou_b)

    def is_all_clear(self):
        """
        Checks if there is nothing above chikou_span.
        Then checks if tenkan > kijun > senkou a > senkou b
        For more fine-grained recommendations, might need Tristate class with notes.
        """
        def last(line):
            last_i=self.df[line].last_valid_index()
            last_value=self.df.loc[last_i, line]
            return last_i, last_value

        last_i_chikou, chikou_span=last('chikou_span')
        chikou_all_clear=(chikou_span > self.df.loc[last_i_chikou, 'tenkan_sen']) and \
            (chikou_span > self.df.loc[last_i_chikou, 'kijun_sen']) and \
            (chikou_span > self.df.loc[last_i_chikou, 'senkou_a']) and \
            (chikou_span > self.df.loc[last_i_chikou, 'senkou_b'])

        last_i, tenkan_sen=last('tenkan_sen')
        now_all_clear=(tenkan_sen >= self.df.loc[last_i, 'kijun_sen']) and \
            (tenkan_sen > self.df.loc[last_i, 'senkou_a']) and \
            (tenkan_sen > self.df.loc[last_i, 'senkou_b'])
        return chikou_all_clear and now_all_clear
