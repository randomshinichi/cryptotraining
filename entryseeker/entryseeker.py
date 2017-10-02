import json
from datamanager import DataManager
from indicators import Ichimoku, RSI


def seek_entries_ichimoku(markets):
    for pair in markets:
        print(pair, end="\r")
        df = dm.open(pair, '1d')
        ichi = Ichimoku(df)
        result = ichi.is_all_clear()
        if result:
            print(pair, "looks good")
        else:
            print(" " * len(pair), end="\r")


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


dm = DataManager(force_refresh=False)
# dm.download_bittrex()

seek_rsi_deals(dm.bittrex_markets, '1d')
