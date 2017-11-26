import argparse
import json
from datamanager import DataManager
from models import Timeframe, Coin
from multiprocessing import Pool

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--download', action='store_true',
                    help='Download new price data', default=False)
args = parser.parse_args()

dm = DataManager(force_refresh=args.download)
if args.download:  # Download new price data
    dm.download_bittrex()


def search_rsi_increasing_multiple_timeframes(pair):
    coin = Coin(pair)

    coin.run_indicators()
    rsi_increasing, details = coin.rsi_increasing_multiple_timeframes()
    if rsi_increasing:
        print(coin.pair, details)


def search_rsi_is_oversold(pair):
    coin = Coin(pair)
    coin.run_indicators()
    is_oversold = coin.rsi_is_oversold()
    if is_oversold:
        print(coin.pair, "is oversold on the 1d timeframe")


pool = Pool()
pool.map(search_rsi_is_oversold, list(dm.bittrex_markets.keys()))
