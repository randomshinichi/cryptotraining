import json
import argparse
import time
import os
import ccxt
from beautifultable import BeautifulTable


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
table.column_headers = ["pair", "ratio", "note"]

trex = ccxt.bittrex()


f = open(args.filename, 'r')
entries = json.load(f)
f.close()

entries_sorted = sorted(entries)

while True:
    table.clear()
    for k in entries_sorted:
        entry_price = entries[k]["price"]

        k_ccxt = translate_dash_to_slash(k)
        current = trex.fetch_ticker(k_ccxt)

        ratio = current['last'] / entry_price
        table.append_row([k, ratio, entries[k]["note"]])

    os.system('clear')
    print(table)
    time.sleep(30)
