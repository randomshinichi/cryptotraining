import argparse
import json
from datamanager import DataManager
from indicators import Ichimoku, RSI


class Coin:
    """Allows for comparisons between Timeframes"""
    pass


class Timeframe:
    """Holds actual price data and manages the indicators on that data"""
    pass


def seek_rsi_deals(markets, timeframe):
    """
    markets = dm.bittrex_markets
    timeframe = '4h' or '1d'
    """
    cheapo = []
    for pair in markets:
        print(pair, end="\r")
        df = dm.open(pair, timeframe)
        rsi = RSI(df, pair)
        if rsi.is_oversold(period=1):
            cheapo.append(pair)
        print(" " * len(pair), end="\r")
    print("Cheapo? Big dip right now anyway", cheapo)

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--download', action='store_true',
                    help='Download new price data', default=False)
args = parser.parse_args()

dm = DataManager(force_refresh=True)
if args.download:  # Download new price data
    dm.download_bittrex()

seek_rsi_deals(dm.bittrex_markets, '1d')
