import ipdb
import os
import json
import pandas as pd
import webbrowser
import poloniex

from cmd import Cmd
from time import time
from decimal import Decimal
from pprint import pprint as pp


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


class PoloCmd(Cmd):

    def _refresh(self):
        self.prices = self.polo.returnTicker()
        with open('entries.json') as f:
            self.entries = json.load(f)

    def preloop(self):
        self.polo = poloniex.Poloniex(
            os.environ['POLONIEX_API_KEY'],
            os.environ['POLONIEX_SECRET'],
        )
        print('Connected to Poloniex')
        self.entries = {}
        self._refresh()
        print('Loaded current prices/entries')

    def do_r(self, args):
        """Refreshes the current prices from Poloniex (all pairs)"""
        self._refresh()

    def do_bal(self, args):
        def _changed(coin_name):
            entry = self.entries.get(coin_name)
            if entry:
                p = pair(entry["base"], coin_name)
                percentage = Decimal(self.prices[p]["last"]) / Decimal(entry['price'])
                return percentage.quantize(Decimal('0.01'))
            else:
                return ''

        def nonzero_balances_only(r):
            nonzero = {}
            for coin_name in r:
                if r[coin_name]['btcValue'] != '0.00000000':
                    nonzero[coin_name] = r[coin_name]
            return nonzero

        balances = nonzero_balances_only(self.polo.returnCompleteBalances())
        b = []
        for coin in balances:
            b.append([coin, balances[coin]['available'], balances[coin]['onOrders'], _changed(coin)])
        output = pd.DataFrame(b, columns=['coin', 'available', 'in orders', 'changed'])
        print(output)

    def chart_data(self, pair, period, how_far_back):
        raw = self.polo.returnChartData(pair, period=period, start=time() - how_far_back)
        df = pd.DataFrame(raw)
        df['date'] = pd.to_datetime(df["date"], unit='s')
        df.dropna(inplace=True)
        print(df)

    def do_orderbook(self, args):
        """
        Returns the orderbook.
        Arguments: BTC_ETH, (depth, can use -1 for infinite)
        """
        a = parse(args)
        try:
            base, coin = a[0], a[1]
        except Exception:
            print("Please give me a base and a coin, at least!")
            return
        depth = a[2] if len(a) > 2 else 10

        resp = self.polo.returnOrderBook(pair(base, coin), depth)
        asks = self.pandaify_orderbook(resp['asks'])
        buys = self.pandaify_orderbook(resp['bids'])
        print("SELLs", '\n', asks, '\n\n')
        print("BUYs", '\n', buys, '\n\n')

    def do_walls(self, args):
        def find_walls(orders):
            return orders[orders.volume > orders.volume.std()]
        a = parse(args)
        try:
            base, coin = a[0], a[1]
        except Exception:
            print("Please give me a base and a coin, at least!")
            return
        depth = a[2] if len(a) > 2 else 10

        resp = self.polo.returnOrderBook(pair(base, coin), depth)
        asks = self.pandaify_orderbook(resp['asks'])
        buys = self.pandaify_orderbook(resp['bids'])
        print("Sell Walls (walls for the seller)?")
        print(find_walls(buys))
        print("Buy Walls (walls for the buyer?")
        print(find_walls(asks), "\n")

    def do_orders(self, args):
        """What orders do I have open at the moment? Doesn't include stops"""
        if parse(args):
            m = self.polo.returnOpenOrders(parse(args))
        else:
            m = self.polo.returnOpenOrders()

        # as usual, Polo returns all markets even when I don't have orders in them
        # so I have to clean it here
        markets = {}
        for key in m:
            if m[key]:
                markets[key] = m[key]

        for pair in markets:
            base, coin = unpair(pair)
            orders = markets[pair]  # because for each market you might have more than one order
            for o in orders:
                print("{} {} {} at {} for a total of {} {}".format(o['type'], o['startingAmount'], coin, o['rate'], o['total'], base))

    def do_loansactive(self, args):
        """Which of my loan offers are being used at the moment?"""
        loans_active = self.polo.returnActiveLoans()['provided']
        for l in loans_active:
            print("Lending {} {} at {} (earned {} so far)".format(l['amount'], l['currency'], l['rate'], l['fees']))

    def do_offers(self, args):
        """How do other people's loan offers look like?"""
        loans_offers = self.polo.returnLoanOrders('BTC')['offers']
        print(pd.DataFrame(loans_offers))

    def do_hist(self, args):
        """Returns trading history for the last 3 days"""
        pp(self.polo.returnTradeHistory(start=time() - (self.polo.DAY * 3)))

    def do_price(self, args):
        base, coin = parse(args)
        print(self.prices[pair(base, coin).upper()]["last"])

    def do_open(self, args):
        """quickly open Poloniex's exchange webpage"""
        webbrowser.open_new('https://poloniex.com/exchange#%s_%s' % parse(args))

    def do_twit(self, args):
        """quickly open Twitter search for some currency"""
        webbrowser.open_new('https://twitter.com/search?f=tweets&vertical=default&q=%24{}&src=typd'.format(args))

    def do_deep(self, args):
        """ipdb.set_trace() to play with internals"""
        ipdb.set_trace()

    def do_q(self, args):
        """Quits!"""
        return True

    def pandaify_orderbook(self, raw_orderbook):
        df = pd.DataFrame(raw_orderbook, columns=['price', 'amount'])
        # Convert str into Decimal
        df = df.applymap(Decimal)
        # I wanna know how many BTC/ETH people risked in their positions
        df['volume'] = df['price'] * df['amount']
        # OK, the volume doesn't need that much precision
        # so I convert it back into float64 so I can use more pandas functions
        df['volume'] = df['volume'].apply(pd.to_numeric)
        # I don't need that much precision for the volume
        df['volume'] = df['volume'].round(3)
        return df


def parse(args):
    return tuple(args.split())


def pair(base, coin):
    return '%s_%s' % (base, coin)


def unpair(pair):
    return pair.split('_')


def quantize(n):
    return n.quantize(Decimal('1.000'))

p = PoloCmd()
p.prompt = '> '
p.cmdloop()
