import json
import argparse
import time
import os
import ccxt
from beautifultable import BeautifulTable
from ccxt.base.errors import RequestTimeout, ExchangeNotAvailable

def translate_dash_to_slash(pair):
    """
    Translates BTC-1ST to 1ST/BTC
    Or, if it's already 1ST/BTC, just return that
    """
    try:
        base, alt = pair.split('-')
        return '/'.join([alt, base])
    except ValueError:
        # It's probably already in the right format
        return pair


parser = argparse.ArgumentParser()
parser.add_argument('filename', type=str, help='the entries.json file')

args = parser.parse_args()
table = BeautifulTable()
table.column_headers = ["pair", "ratio", "size", "note"]

exchanges = {
    "bittrex": ccxt.bittrex(),
}
exch = exchanges["bittrex"]

f = open(args.filename, 'r')
entries = json.load(f)
f.close()

entries_sorted = sorted(entries)

while True:
    table.clear()
    for k in entries_sorted:
        entry = entries[k]

        try:
            current = exch.fetch_ticker(translate_dash_to_slash(k))
            ratio = current['last'] / entry["price"]
        except RequestTimeout:
            ratio = "TMO"
        except ExchangeNotAvailable:
            ratio = "ENA"

        table.append_row([k, ratio, entry.get("size", "0"), entry.get("note", "")])

    os.system('clear')
    print(table)
    time.sleep(60)
