import json
from datamanager import DataManager
from indicators import Ichimoku, RSI


def update_bullish_list(pairs):
    from datetime import datetime
    try:
        with open('bullish_list.json', 'r') as f:
            historical_data = json.load(f)
    except:
        historical_data = []

    record = {
        "timestamp": datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"),
        "all": pairs,
    }
    historical_data.append(record)

    with open('bullish_list.json', 'w') as f:
        print("Saving list of bullish coins")
        json.dump(historical_data, f, sort_keys=True, indent=4)


def seek_entries_ichimoku(markets, record=False):
    bull_list = []
    for pair in markets:
        print(pair, end="\r")
        df = dm.open(pair, '1d')
        ichi = Ichimoku(df)
        ichi.run()
        result = ichi.analyze()
        if result:
            print(pair, "looks good")
            bull_list.append(pair)
        else:
            print(" " * len(pair), end="\r")

    if record:
        update_bullish_list(bull_list)

dm = DataManager()
# seek_entries(dm.bittrex_markets, record=True)
df = dm.open('LTC/BTC', '1d')
rsi = RSI(df)
rsi.run()