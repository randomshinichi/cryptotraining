#!/usr/bin/env python3
import argparse
import backtrader as bt


class IchiSignal(bt.Indicator):
    lines = (('signal'),)

    def __init__(self):
        ichi = bt.indicators.Ichimoku()
        self.lines.signal = ichi.tenkan_sen - ichi.kijun_sen


parser = argparse.ArgumentParser(description='A simple backtester')
parser.add_argument("data", help="the CSV for a coin pair")
args = parser.parse_args()

cerebro = bt.Cerebro()
data = bt.feeds.GenericCSVData(dataname=args.data, openinterest=-1, dtformat="%Y-%m-%dT%H:%M:%S")

cerebro.adddata(data)
cerebro.addindicator(bt.indicators.Ichimoku)
cerebro.add_signal(bt.SIGNAL_LONG, IchiSignal)
cerebro.broker.setcash(100000)
print(cerebro.broker.getvalue())
cerebro.run()
print(cerebro.broker.getvalue())
cerebro.plot()
