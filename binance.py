import csv
import io
import ccxt
from datetime import datetime
from datamanager import Data


def slash_to_dash(m):
    """
    Translates 1ST/BTC to BTC-1ST
    Or, if it's already BTC-1ST, just return that
    """
    pair, base = m.split('/')
    return '-'.join([base, pair])


def csvify(list_of_candles):
    file_buffer = io.StringIO()
    writer = csv.DictWriter(
        file_buffer, ["timestamp", "open", "high", "low", "close", "volume"])
    writer.writeheader()
    writer.writerows(list_of_candles)
    file_buffer.seek(0)
    return file_buffer.read()


def dictify(list_of_candles):
    # input: [[1518879600000, 0.0010727, 0.001082, 0.0010666, 0.0010685, 74415.73],...]
    # output: [{"timestamp": "2018-08-12 00:00:00", "open": 0.0010727, "high":
    # 0.001082, "low": 0.0010666, "close": 0.0010685, "volume": 74415.73},...]

    ans = []
    for candle in list_of_candles:
        candle = {
            "timestamp": datetime.utcfromtimestamp(candle[0] / 1000).strftime("%Y-%m-%d %H:%M:%S"),
            "open": candle[1],
            "high": candle[2],
            "low": candle[3],
            "close": candle[4],
            "volume": candle[5],
        }
        ans.append(candle)
    return ans


binance = ccxt.binance()
markets = list(binance.load_markets().keys())
d = Data()
coins = {}

for market_name in markets:
    print(market_name, "getting")
    pair_data = {
        "1h": csvify(dictify(binance.fetchOhlcv(market_name, timeframe='1h'))),
        "2h": csvify(dictify(binance.fetchOhlcv(market_name, timeframe='2h'))),
        "4h": csvify(dictify(binance.fetchOhlcv(market_name, timeframe='4h'))),
        "1d": csvify(dictify(binance.fetchOhlcv(market_name, timeframe='1d'))),
    }
    coins[market_name] = pair_data

for c in coins:
    d.write(slash_to_dash(c), "1h", "binance", coins[c]["1h"])
    d.write(slash_to_dash(c), "2h", "binance", coins[c]["2h"])
    d.write(slash_to_dash(c), "4h", "binance", coins[c]["4h"])
    d.write(slash_to_dash(c), "1d", "binance", coins[c]["1d"])

print("done")
