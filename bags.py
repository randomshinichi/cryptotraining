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
table.column_headers = ["pair", "price", "ratio", "size", "note"]
table.numeric_precision = 8

exchanges = {
    "bittrex": ccxt.bittrex(),
    "poloniex": ccxt.poloniex(),
    "bitfinex": ccxt.bitfinex(),
    "cryptopia": ccxt.cryptopia(),
    "kraken": ccxt.kraken()
}


def load_data(filename):
    with open(args.filename, 'r') as f:
        data = json.load(f, object_pairs_hook=OrderedDict)
        return data


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


def refresh_and_print_table(data):
    table.clear()
    for exchange in data:
        e = exchanges[exchange]

        for pair in data[exchange]:
            entry = data[exchange][pair]

            try:
                current = e.fetch_ticker(translate_dash_to_slash(pair))
                ratio = current['last'] / entry["price"]
                ratio = int(ratio * 100) / 100.0  # try to truncate so that 10% is just 1.10
            except RequestTimeout:
                ratio = "TMO"
            except ExchangeNotAvailable:
                ratio = "ENA"
            table.append_row([pair, entry["price"], ratio, entry.get("size", "0"), entry.get("note", "")])

    os.system('clear')
    print(table)


class FSHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == args.filename:
            print(event.src_path, "updated, refreshing")
            data = load_data(event.src_path)
            refresh_and_print_table(data)


class Watcher:
    def __init__(self):
        self.observer = Observer()

    def run(self):
        fs_handler = FSHandler()
        self.observer.schedule(fs_handler, os.path.dirname(args.filename))
        self.observer.start()

        try:
            while True:
                data = load_data(args.filename)
                refresh_and_print_table(data)
                print("ok going to sleep")
                time.sleep(60)
        except KeyboardInterrupt:
            self.observer.stop()

        self.observer.join()


w = Watcher()
w.run()
