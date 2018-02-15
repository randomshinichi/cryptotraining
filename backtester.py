#!/usr/bin/env python3
import argparse
import backtrader as bt


class IchiSignal(bt.Indicator):
    lines = (('signal'),)

    def __init__(self):
        ichi = bt.indicators.Ichimoku()
        self.lines.signal = ichi.tenkan_sen - ichi.kijun_sen


class EMASMASignal(bt.Indicator):
    lines = (('signal'),)
    params = (('p1', 9), ('p2', 26))

    def __init__(self):
        ema = bt.indicators.EMA(period=self.p.p1)
        sma = bt.indicators.SMA(period=self.p.p2)
        self.lines.signal = ema - sma


class BollingerEntrySignal(bt.Indicator):
    lines = (('signal'),)

    def __init__(self):
        bb = bt.indicators.BollingerBands()
        self.lines.signal = bb.bot - self.data


class BollingerExitSignal(bt.Indicator):
    lines = (('signal'),)

    def __init__(self):
        bb = bt.indicators.BollingerBands()
        self.lines.signal = bb.top - self.data


parser = argparse.ArgumentParser(description='A simple backtester')
parser.add_argument("data", help="the CSV for a coin pair")
parser.add_argument("--range", help="Use a ranging strategy instead of a trending", action='store_true')
args = parser.parse_args()

cerebro = bt.Cerebro()
data = bt.feeds.GenericCSVData(dataname=args.data, openinterest=-1, dtformat="%Y-%m-%dT%H:%M:%S")

cerebro.adddata(data)

if not args.range:
    # Ichimoku works great for certain pairs on the 1d that tend to trend
    cerebro.addindicator(bt.indicators.Ichimoku)
    cerebro.add_signal(bt.SIGNAL_LONG, IchiSignal)

    # EMA9 crossing SMA26 performs similarly to Ichimoku tenkou cross. Works well in trending systems
    # cerebro.add_signal(bt.SIGNAL_LONG, EMASMASignal)

elif args.range:
    # Bollinger is useful on the hourly charts but not as good as I expected.
    # It keeps me out of huge trends on the daily.
    # It's stunning on Monero, Zencash
    cerebro.addindicator(bt.indicators.BollingerBands)
    cerebro.add_signal(bt.SIGNAL_LONG, BollingerEntrySignal)
    cerebro.add_signal(bt.SIGNAL_LONGEXIT, BollingerExitSignal)


cerebro.broker.setcash(10000)
print(cerebro.broker.getvalue())
cerebro.run()
print(cerebro.broker.getvalue())
cerebro.plot()
