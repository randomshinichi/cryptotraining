#!/usr/bin/env python3
import argparse
from datamanager import Data
from models import Coin
from multiprocessing import Pool


def search_ema_daily(pair, exchange):
    """
    Find recent bullish crosses (recent being < 10 days ago)
    Remember to take the market condition and type of coin into account.
    Finds these kinds of coins:
    1. pumps that are just about to dump (look at the slope)
    2. pumps in the process of dumping
    3. gradual, weak bullish crosses that'll peter out soon
    4. gradual small bullish crosses that'll could become something big
    """
    coin = Coin(pair, exchange)
    bullish_cross, days_ago = coin.ema_bullish_cross(timeframe="1d", fast_period=9, slow_period=26)
    if bullish_cross and days_ago <= 10:
        print(coin.pair, "({})".format(coin.exchange), "EMA 9-26 bullish cross {} days ago".format(days_ago))


def search_ema_daily_mature(pair, exchange):
    """
    Finds older bullish crosses that are probably a stronger upwards trend.
    1. Bullruns that are just about to end
    2. Pumps that are slowly dying out
    3. Look for the ones that haven't increased so much since then, and are slowly rising.
    """
    coin = Coin(pair, exchange)
    bullish_cross, days_ago = coin.ema_bullish_cross(timeframe="1d", fast_period=9, slow_period=26)
    if bullish_cross and (8 <= days_ago <= 20):
        print(coin.pair, "({})".format(coin.exchange), "EMA 9-26 bullish cross, confirmed by {} days".format(days_ago))


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


parser = argparse.ArgumentParser()
parser.add_argument('search_method', help="search_ema_daily, search_stochrsi...whatever")
parser.add_argument('exchange', help="binance/bittrex")
args = parser.parse_args()

search_method_map = {
    "search_ema_daily": search_ema_daily,
    "search_ema_daily_mature": search_ema_daily_mature,
    "search_ema_hourly": search_ema_hourly,
    "search_rsi_increasing_all_timeframes": search_rsi_increasing_all_timeframes,
    "search_stochrsi_oversold_all_timeframes": search_stochrsi_oversold_all_timeframes
}

pool = Pool()
"""
pool.map() only supports (func, arg)
pool.starmap() supports (func, (as many args as you want in a tuple))
"""
pairs_exchange = [(p, args.exchange) for p in Data().pairs(args.exchange)]
pool.starmap(search_method_map[args.search_method], pairs_exchange)
