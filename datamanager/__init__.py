import os
from pathlib import Path
import pandas as pd


class Data:
    """
    The point of the DataManager is to hide all the candlestick JSON to Pandas Dataframe complexity.
    Whether the resulting DataFrame should have an index, or not, and what its columns should be named
    should be standardized in this class.
    """

    # if DataManager is instantiated from code in a different dir,
    # the cwd will be that dir, and DataManager won't find files in
    # its own dir.
    # So we need DataManager to figure out where it is in the filesystem
    root = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')

    def get_data_path(self, timeframe, exchange):
        """
        Input: '4h', 'binance'
        Returns '/Users/shinichi/source/cryptocoins/datamanager/data/binance/1d/BTC-LTC.json'
        """
        return os.path.join(self.root, exchange, timeframe)

    def open(self, pair, timeframe, exchange):
        """
        pair: 'BTC-LTC'
        timeframe: '4h', '1d'
        exchange: 'binance'
        """
        path = self.get_data_path(timeframe, exchange)
        with open(os.path.join(path, pair + '.csv'), 'r') as d:
            df = pd.read_csv(d)

        df.set_index(pd.DatetimeIndex(df['timestamp']), inplace=True)
        df.drop('timestamp', axis=1, inplace=True)

        return df

    def write(self, pair, timeframe, exchange, data):
        path = self.get_data_path(timeframe, exchange)

        if not os.path.exists(path):
            os.makedirs(path)

        with open(os.path.join(path, pair + '.csv'), 'w') as d:
            d.write(data)

    @property
    def exchanges(self):
        root_path = Path(self.root)
        exchanges = [x.stem for x in root_path.iterdir() if x.is_dir()]
        return exchanges
