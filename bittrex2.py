#!/usr/bin/env python3
import io
import csv
import requests
import ccxt
import time
from datamanager import Data
from resampler import resample

resample_how = {
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum',
    'basevolume': 'sum',
}


bittrex_markets = ccxt.bittrex().load_markets()


def slash_to_dash(m):
    """
    Translates 1ST/BTC to BTC-1ST
    Or, if it's already BTC-1ST, just return that
    """
    if '/' in m:
        return bittrex_markets[m]['id']
    else:
        return m


def get(m, period='day'):
    url = 'https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName={}&tickInterval={}'

    resp = {}
    while resp.get("result") is None:
        resp = requests.get(url.format(m, period)).json()
        if resp["result"] is None:
            print("bittrex fucked up")

    # Bittrex returns each candle as {"T": ..., "O": ...}
    # We want it in our own format that'll be the same across all exchanges.
    result = []
    for candle in resp["result"]:
        candle_2 = {}
        candle_2["timestamp"] = candle.pop("T")
        candle_2["open"] = candle.pop("O")
        candle_2["high"] = candle.pop("H")
        candle_2["low"] = candle.pop("L")
        candle_2["close"] = candle.pop("C")
        candle_2["volume"] = candle.pop("V")

        # remove this for consistency with resampled data
        # (resampler cannot know about columns that other exchanges don't provide)
        # candle_2["basevolume"] = candle.pop("BV")

        result.append(candle_2)
    return result


def csvify(list_of_candles):
    file_buffer = io.StringIO()
    writer = csv.DictWriter(
        file_buffer, ["timestamp", "open", "high", "low", "close", "volume"])
    writer.writeheader()
    writer.writerows(list_of_candles)
    file_buffer.seek(0)
    return file_buffer.read()


timeframes = {}
for m in list(bittrex_markets.keys()):
    market_name = slash_to_dash(m)
    print(market_name, end="", flush=True)

    print(" getting", end="", flush=True)
    """
    TODO
    Clamp hourly's beginning to 12am, otherwise resampled 2H and 4H data do not line up with TradingView
    TradingView: 12am, 4am, 8am...
    """
    hourly = get(market_name, 'hour')
    daily = get(market_name, 'day')

    print(" resampling", end="", flush=True)

    try:
        pair_data = {
            "1h": csvify(hourly),
            "2h": csvify(resample(hourly, 2)),
            "4h": csvify(resample(hourly, 4)),
            "1d": csvify(daily)
        }
    except Exception as e:
        print("something's wrong with {}".format(market_name), e)
    else:
        timeframes[market_name] = pair_data
        print(" ✓")

    time.sleep(0.2)

# timeframes["BTC-QRL"]["4h"] now contains the raw string that should be written to CSV
d = Data()
for m in timeframes:
    d.write(m, "1h", "bittrex", timeframes[m]["1h"])
    d.write(m, "2h", "bittrex", timeframes[m]["2h"])
    d.write(m, "4h", "bittrex", timeframes[m]["4h"])
    d.write(m, "1d", "bittrex", timeframes[m]["1d"])

print("done")
