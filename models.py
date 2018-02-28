from datamanager import Data
from talib import EMA, RSI, STOCHRSI

dm = Data()


class Coin:
    """
    Actual entry search tactics defined here.
    Can compare across Timeframes.
    """

    def __init__(self, pair, exchange):
        self.pair = pair
        self.exchange = exchange
        self.tf = {
            "1h": dm.open(self.pair, "1h", exchange),
            "2h": dm.open(self.pair, "2h", exchange),
            "4h": dm.open(self.pair, "4h", exchange),
            "1d": dm.open(self.pair, "1d", exchange)
        }

    def __str__(self):
        return self.pair

    def __repr__(self):
        return self.pair

    def ema_bullish_cross(self, timeframe="1d", fast_period=9, slow_period=26):
        ema_fast = EMA(self.tf[timeframe].close.as_matrix(), fast_period)
        ema_slow = EMA(self.tf[timeframe].close.as_matrix(), slow_period)

        # If EMA9 > EMA26, find out when the bullish cross happened
        if ema_fast[-1] > ema_slow[-1]:
            idx = 1
            while ema_fast[-idx] > ema_slow[-idx]:
                idx += 1

            return ema_fast[-1] > ema_slow[-1], idx
        else:
            return False, 0

    def rsi_increasing_all_timeframes(self, period=20):
        def is_increasing(series):
            midpoint = int(len(series) / 2)
            return series[:midpoint].mean() < series[midpoint:].mean()

        results = []
        for i in list(self.tf.keys()):
            rsi_timeframe = RSI(self.tf[i].close.as_matrix())[-period:]
            results.append(is_increasing(rsi_timeframe))

        return all(results)

    def stochrsi_oversold_all_timeframes(self):
        """
        TA-LIB STOCHRSI doesn't give the same results as Tradingview.
        """
        results = []
        for i in list(self.tf.keys()):
            k, d = STOCHRSI(self.tf[i].close.as_matrix(), timeperiod=14, fastk_period=3, fastd_period=3)
            results.append(d[-1] < 20)
        return all(results)
