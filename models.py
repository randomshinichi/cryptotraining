from datamanager import DataManager
from indicators import Ichimoku, RSI, StochasticRSI


class Timeframe:
    """Holds actual price data and manages the indicators on that data"""

    def __init__(self, pair, timeframe):
        self.dm = DataManager()
        self.data = self.dm.open(pair, timeframe)
        self.rsi = None
        self.stochrsi = None
        self.ichimoku = None

    def run_indicators(self, rsi, stochrsi, ichimoku):
        """
        Just because you created the Timeframe, doesn't mean
        you should run all the indicatros straight away!
        On the other hand, accumulating lots of Coins hanging around,
        waiting for you to run run_indicators() on them eats up too much RAM.
        """
        if rsi:
            self.rsi = RSI(self.data)
            self.rsi.process()
        if stochrsi:
            self.stochrsi = StochasticRSI(self.data)
            self.stochrsi.process()
        if ichimoku:
            self.ichimoku = Ichimoku(self.data)
            self.ichimoku.process()


class Coin:
    """
    Actual entry search tactics defined here.
    Can compare across Timeframes.
    """

    def __init__(self, pair):
        self.pair = pair
        self.dm = DataManager()
        self.tf = {
            "1h": Timeframe(self.pair, "1h"),
            "2h": Timeframe(self.pair, "2h"),
            "4h": Timeframe(self.pair, "4h"),
            "1d": Timeframe(self.pair, "1d")
        }

    def debug(self):
        self.tf["1h"].run_indicators(rsi=True, stochrsi=True)

    def run_indicators(self, rsi=False, stochrsi=False, ichimoku=False):
        for timeframe in self.tf:
            self.tf[timeframe].run_indicators(rsi, stochrsi, ichimoku)

    def rsi_increasing_multiple_timeframes(self):
        timeframes = [self.tf["1h"].rsi.is_increasing(), self.tf["2h"].rsi.is_increasing(), self.tf[
            "4h"].rsi.is_increasing(), self.tf["1d"].rsi.is_increasing()]
        return all(timeframes[:3]), timeframes

    def rsi_is_oversold(self):
        return self.tf["1d"].rsi.is_oversold(period=1)

    def stochrsi_is_oversold(self):
        return self.tf["1d"].stochrsi.is_oversold()
