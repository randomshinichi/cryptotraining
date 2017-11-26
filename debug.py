from models import Coin
from indicators import RSI, StochasticRSI

coin = Coin("BTC-TKN")
coin.run_indicators(stochrsi=True)
coin.stochrsi_less_than_20()