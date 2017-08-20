from time import sleep
import requests
import ipdb
import gzip

times = {
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "2h": 7200,
    "4h": 14400,
    "1d": 86400
}

base_url = "https://poloniex.com/public?command=returnChartData&currencyPair={}&start=0000000000&end=9999999999&period={}"
pairs = ['BTC_ETH', 'BTC_ETC', ] # 'BTC_LTC', 'BTC_LBC', 'BTC_STR', 'BTC_ZEC', 'USDT_ETH', 'USDT_BTC', 'USDT_LTC', 'USDT_ZEC']
for p in pairs:
    for t in times:
        url = base_url.format(p, times[t])
        filename = 'data/{}-{}.json.gz'.format(p, t)
        print(url)
        print("Waiting a bit so that Poloniex doesn't throttle us")
        sleep(2)
        resp = requests.get(url)
        with gzip.open(filename, 'wb') as f:
            print("writing", filename)
            f.write(resp.content)

