import pandas as pd
import requests
import json

from pyti.smoothed_moving_average import smoothed_moving_average as sma
from plotly.offline import plot
import plotly.graph_objs as go

class TradingBot:
	def __init__(self, symbol='BTCUSDT'):
		self.symbol = symbol
		self.df = self.getData()

	def getData(self):
		# get url
		base = 'https://api.binance.com'
		endpoint = '/api/v3/klines'
		params = '?&symbol=' + self.symbol + '&interval=1h'

		url = base + endpoint + params
		print("Fetching data from " + url)

		# fetch data
		data = requests.get(url)
		dictionary = json.loads(data.text)

		# clean up
		df = pd.DataFrame.from_dict(dictionary).drop(range(6,12), axis=1)
		col_names = ['time', 'open', 'high', 'low', 'close', 'volume']
		df.columns = col_names

		print(df)

		for col in col_names:
			df[col] = df[col].astype(float)

		# calculate SMAs
		df['fast_sma'] = sma(df['close'].tolist(), 10)
		df['slow_sma'] = sma(df['close'].tolist(), 30)
		
		return df

	def strategy(self):
		df = self.df

		buy_signals = []

		for i in range(1, len(df['close'])):
			if df['slow_sma'][i] > df['low'][i] and (df['slow_sma'][i] - df['low'][i]) > 0.03 * df['low'][i]:
				buy_signals.append([df['time'][i], df['low'][i]])

		self.plotData(buy_signals = buy_signals)
	
	def plotData(self, buy_signals = False):
		df = self.df

		# plot candlestick chart
		candle = go.Candlestick(
			x = df['time'],
			open = df['open'],
			close = df['close'],
			high = df['high'],
			low = df['low'],
			name = "Candlesticks")

		# plot MAs
		fsma = go.Scatter(
			x = df['time'],
			y = df['fast_sma'],
			name = "Fast SMA",
			line = dict(color = ('rgba(102, 207, 255, 50)')))

		ssma = go.Scatter(
			x = df['time'],
			y = df['slow_sma'],
			name = "Slow SMA",
			line = dict(color = ('rgba(255, 207, 102, 50)')))

		data = [candle, ssma, fsma]

		if buy_signals:
			buys = go.Scatter(
					x = [item[0] for item in buy_signals],
					y = [item[1] for item in buy_signals],
					name = "Buy Signals",
					mode = "markers",
				)

			sells = go.Scatter(
					x = [item[0] for item in buy_signals],
					y = [item[1]*1.02 for item in buy_signals],
					name = "Sell Signals",
					mode = "markers",
				)

			data = [candle, ssma, fsma, buys, sells]


		# style and display
		layout = go.Layout(title = self.symbol)
		fig = go.Figure(data = data, layout = layout)

		plot(fig, filename=self.symbol)


	


model = TradingBot()
model.strategy()