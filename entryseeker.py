import argparse
from datamanager import Data
from models import Coin
from multiprocessing import Pool

parser = argparse.ArgumentParser()
args = parser.parse_args()


def search_emafast_over_emaslow(pair, exchange):
    coin = Coin(pair, exchange)
    emafast_over_emaslow, days_ago = coin.emafast_over_emaslow_daily()
    if emafast_over_emaslow and days_ago <= 10:
        print(coin.pair, "({})".format(coin.exchange), "EMA-9 vs EMA-26 bullish cross {} days ago".format(days_ago))


def search_rsi_increasing_all_timeframes(pair, exchange):
    coin = Coin(pair, exchange)
    is_increasing = coin.rsi_increasing_all_timeframes(period=20)
    if is_increasing:
        print(coin.pair, "({})".format(coin.exchange), "RSI increasing across all timeframes")


pool = Pool()

"""
pool.map() only supports (func, arg)
pool.starmap() supports (func, (as many args as you want in a tuple))
"""
pairs_exchange = [(p, 'bittrex') for p in Data().pairs('bittrex')]
pool.starmap(search_emafast_over_emaslow, pairs_exchange)
