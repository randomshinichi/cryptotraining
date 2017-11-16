#!/usr/bin/env python3

import json
import argparse
import time
import os
import ccxt
from collections import OrderedDict
from beautifultable import BeautifulTable
from ccxt.base.errors import RequestTimeout, ExchangeNotAvailable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

parser = argparse.ArgumentParser()
parser.add_argument('filename', type=str, help='the data.json file')

args = parser.parse_args()
table = BeautifulTable()
table.column_headers = ["pair", "ratio", "size", "note"]

exchanges = {
    "bittrex": ccxt.bittrex(),
    "poloniex": ccxt.poloniex(),
    "bitfinex": ccxt.bitfinex(),
}


class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print("file changed, updating...")
        data = load_data(args.filename)
        refresh_and_print_table(data)


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


def load_data(filename):
    f = open(args.filename, 'r')
    data = json.load(f, object_pairs_hook=OrderedDict)
    f.close()
    return data


def refresh_and_print_table(data):
    table.clear()
    for exchange in data:
        e = exchanges[exchange]

        for pair in data[exchange]:
            entry = data[exchange][pair]

            try:
                current = e.fetch_ticker(translate_dash_to_slash(pair))
                ratio = current['last'] / entry["price"]
            except RequestTimeout:
                ratio = "TMO"
            except ExchangeNotAvailable:
                ratio = "ENA"

            table.append_row([pair, ratio, entry.get("size", "0"), entry.get("note", "")])

    os.system('clear')
    print(table)


data = load_data(args.filename)

fs_handler = MyHandler()
observer = Observer()
observer.schedule(fs_handler, os.path.dirname(args.filename))
observer.start()

try:
    while True:
        refresh_and_print_table(data)
        time.sleep(60)
except KeyboardInterrupt:
    observer.stop()
observer.join()
