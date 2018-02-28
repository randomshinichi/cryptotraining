import argparse
from datamanager import Data
from models import Coin
from multiprocessing import Pool

parser = argparse.ArgumentParser()
parser.add_argument('exchange', help="binance/bittrex")
args = parser.parse_args()


def search_ema_daily(pair, exchange):
    coin = Coin(pair, exchange)
    bullish_cross, days_ago = coin.ema_bullish_cross(timeframe="1d", fast_period=9, slow_period=26)
    if bullish_cross and days_ago <= 10:
        print(coin.pair, "({})".format(coin.exchange), "EMA 9-26 bullish cross {} days ago".format(days_ago))


def search_ema_hourly(pair, exchange):
    coin = Coin(pair, exchange)
    bullish_cross, hours_ago = coin.ema_bullish_cross(timeframe="1h", fast_period=4, slow_period=18)
    if bullish_cross and hours_ago <= 5:
        print(coin.pair, "({})".format(coin.exchange), "EMA 4-18 bullish cross {} hours ago".format(hours_ago))


def search_rsi_increasing_all_timeframes(pair, exchange):
    coin = Coin(pair, exchange)
    is_increasing = coin.rsi_increasing_all_timeframes(period=20)
    if is_increasing:
        print(coin.pair, "({})".format(coin.exchange), "RSI increasing across all timeframes")


def search_stochrsi_oversold_all_timeframes(pair, exchange):
    coin = Coin(pair, exchange)
    is_oversold = coin.stochrsi_oversold_all_timeframes()
    if is_oversold:
        print(coin.pair, "({})".format(coin.exchange), "StochRSI oversold on all timeframes")


pool = Pool()

"""
pool.map() only supports (func, arg)
pool.starmap() supports (func, (as many args as you want in a tuple))
"""
pairs_exchange = [(p, args.exchange) for p in Data().pairs(args.exchange)]
pool.starmap(search_ema_daily, pairs_exchange)
