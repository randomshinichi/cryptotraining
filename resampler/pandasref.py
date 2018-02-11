import pandas as pd


ohlc_dict = {
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum',
    'basevolume': 'sum',
}


df = pd.read_csv('data.csv')

df.set_index(pd.DatetimeIndex(df['timestamp']), inplace=True)
df.drop('timestamp', axis=1, inplace=True)

ans = df.resample('4H', how=ohlc_dict)
print(len(df), len(ans))