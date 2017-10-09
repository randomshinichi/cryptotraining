import os
import json
import ccxt
import requests
import time
import pandas as pd
import numpy as np
bittrex_translation = {
    "O": "open",
    "H": "high",
    "L": "low",
    "C": "close",
    "V": "volume",
    "BV": "basevolume",
    "T": "timestamp",
}

ohlc_dict = {
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum',
    'basevolume': 'sum',
}


class DataManager:
    """
    The point of the DataManager is to hide all the candlestick JSON to Pandas Dataframe complexity.
    Whether the resulting DataFrame should have an index, or not, and what its columns should be named
    should be standardized in this class.
    """

    def __init__(self, force_refresh=False):
        # if DataManager is instantiated from code in a different dir,
        # the cwd will be that dir, and DataManager won't find files in
        # its own dir.
        # So we need DataManager to figure out where it is in the filesystem
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(self.dir_path, 'bittrex_markets.json')
        # bittrex_markets is from ccxt.bittrex().load_markets(). saved for
        # offline convenience
        if not force_refresh:
            self.bittrex_markets = json.load(open(file_path))
        else:
            self.bittrex_markets = ccxt.bittrex().load_markets()
            with open(file_path, 'w') as f:
                json.dump(self.bittrex_markets, f)


    def slash_to_dash(self, m):
        """
        Translates 1ST/BTC to BTC-1ST
        Or, if it's already BTC-1ST, just return that
        """
        if '/' in m:
            return self.bittrex_markets[m]['id']
        else:
            return m

    def get_data_path(self, pair, timeframe):
        """
        Input: 'BTC-LTC', '4h' or
        Input: 'LTC/BTC', '4h'
        Returns '/Users/shinichi/source/cryptocoins/datamanager/data/1d/BTC-LTC.json'
        """
        return os.path.join(self.dir_path, "data", timeframe, self.slash_to_dash(pair)+".json")

    def open(self, pair, timeframe, from_time=None, until_time=None, matplotlib=False):
        """
        pair: '1ST/BTC'
        timeframe: '4h', '1d'
        from_time: '2017-09-12 12:00:00' or '2017-09-12'
        until_time: same
        """
        path = self.get_data_path(pair, timeframe)
        with open(path, 'r') as d:
            df = pd.read_json(d, orient='records')

        df = df[['timestamp', 'open', 'high',
                 'low', 'close', 'volume', 'basevolume']]

        df.set_index(pd.DatetimeIndex(df['timestamp']), inplace=True)
        df.drop('timestamp', axis=1, inplace=True)

        return df[from_time:until_time]

    def open_plotter_friendly(self, pair, timeframe):
        """
        Meant for Ichimoku Plotter.
        Like open(), but does not set an index on timestamp.
        Instead, it changes it to a matplotlib friendly number.
        Because of this, from_time and until_time won't work, so
        this warrants its own function.
        """
        path = self.get_data_path(timeframe, pair)
        with open(path, 'r') as d:
            df = pd.read_json(d, orient='records')

        df = df[['timestamp', 'open', 'high',
                 'low', 'close', 'volume', 'basevolume']]

        from matplotlib.dates import date2num
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df['timestamp'] = df['timestamp'].map(date2num)
        return df


    def download_bittrex(self):
        def get(m, period='day'):
            url = 'https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName={}&tickInterval={}'
            resp = requests.get(url.format(m, period)).json()

            df = pd.DataFrame.from_dict(resp["result"])
            df.rename(
                index=str,
                columns=bittrex_translation,
                inplace=True
            )
            # For resampling, we need the index to be a DatetimeIndex
            df.set_index(pd.DatetimeIndex(df['timestamp']), inplace=True)
            # this column is already duplicated in the index
            df.drop("timestamp", axis=1, inplace=True)
            return df

        all_data = {}
        for m in list(self.bittrex_markets.keys()):
            pair_data = {}
            market_name = self.slash_to_dash(m)
            print(market_name, end="", flush=True)

            print(" 4h", end="", flush=True)
            df = get(market_name, 'hour')
            # once we've resampled, we don't want an index anymore
            # because the index is never saved as a column with the data
            df_4h = df.resample('4H', how=ohlc_dict).reset_index()
            pair_data["4h"] = df_4h.to_json(orient='records', date_format='iso')

            print(" 1d")
            df = get(market_name, 'day').reset_index()
            pair_data["1d"] = df.to_json(orient='records', date_format='iso')

            all_data[market_name] = pair_data
            time.sleep(0.5)

        print("Writing Data")
        for m in all_data:
            with open(self.get_data_path(m, "4h"), 'w') as f:
                f.write(all_data[m]["4h"])
            with open(self.get_data_path(m, "1d"), 'w') as f:
                f.write(all_data[m]["1d"])