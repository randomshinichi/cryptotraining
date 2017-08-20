import ipdb
import datetime
import backtrader as bt

from utils import open_json, between


class Ichimoku(bt.indicators.Ichimoku):
    def _plotinit(self):
        self.plotinfo.plotname = 'My Ichimoku'
        self.plotinfo.plotlinevalues = False
        self.plotinfo.plotlinelabels = True


class IchimokuStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.open = self.datas[0].open
        self.close = self.datas[0].close
        self.volume = self.datas[0].volume

        self.ichimoku = Ichimoku(self.datas[0])

        self.order = None

    def should_i_buy(self):
        tenkan_over_kijun = self.ichimoku.tenkan_sen[0] > self.ichimoku.kijun_sen[0]
        chikou_over_price = self.ichimoku.chikou_span[-26] > self.close[-26]  # because chikou_span[0] is actually self.close[26] (from the future)
        price_over_cloud = (self.ichimoku.senkou_span_a[0] < self.close[0]) and (self.ichimoku.senkou_span_b[0] < self.close[0])
        self.log('tenkan_over_kijun: {}\tchikou_over_price: {}\tprice_over_cloud: {}'.format(tenkan_over_kijun, chikou_over_price, price_over_cloud))
        buy_sig = tenkan_over_kijun and chikou_over_price and price_over_cloud
        return buy_sig

    def should_i_sell(self):
        tenkan_below_kijun = self.ichimoku.tenkan_sen[0] < self.ichimoku.kijun_sen[0]
        # TODO: FFS FIND A BETTER SELL SIGNAL
        # chikou_hitting_candles = self.ichimoku.chikou_span[0]
        # use between() for inside kumo?
        return tenkan_below_kijun

    def ichimoku_log(self):
        self.log('Tenkan-sen: %.8f, Kijun-sen: %.8f, Chikou: %.8f, Senkou A: %.8f, Senkou B: %.8f' %
                 (self.ichimoku.tenkan_sen[0],
                  self.ichimoku.kijun_sen[0],
                  self.ichimoku.chikou_span[0],
                  self.ichimoku.senkou_span_a[0],
                  self.ichimoku.senkou_span_b[0])
                 )

    def next(self):
        self.log('CLOSE, %.8f' % self.close[0])
        # Do we already have an order? If so, don't send another one!
        if self.order:
            return

        # check if we are in a position in the market:
        if not self.position:
            if self.should_i_buy():
                self.log('BUY CREATE, %.8f' % self.close[0])
                self.buy()
        else:
            # we're already in the market - find out when to sell!
            if self.should_i_sell():
                self.log('SELL CREATE, %.8f' % self.close[0])
                self.sell()


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(IchimokuStrategy)

    data = bt.feeds.PandasData(
        dataname=open_json('data/USDT_LTC-1d.json.gz', verbose=True),
        openinterest="quoteVolume",
        datetime="date",
    )
    cerebro.adddata(data)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    custom_lcolors = [0, 9, 8, 2, 1]
    cerebro.plot(
        start=datetime.datetime(2017, 1, 1),
        end=datetime.datetime(2017, 8, 1),
        style='candle',
        barup='green',
        grid=True,
    )
