#!/usr/bin/env python3
# BackTest.py - Backtesting of Python Trading Bot
# Strategy: 
# Buy signal: MACD Hist Up + Low < RSI < High
# Sell signal: MACD Hist Down + Low < RSI < High

import time
import argparse
from datetime import datetime
import logging
import random

from TradingBot import TradingBot


if __name__ == "__main__":

	print(':: Start of program ::')
	# Capture command line params
	parser = argparse.ArgumentParser(
		description=__doc__,
		formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument(
		'-s', '--symbol',
		help='Symbol eg. LTCBTC')
	parser.add_argument(
		'-e', '--exchange',
		help='Exchange name. eg. bitfinex, binance')	
	
	parser.add_argument(
		'-lt', '--limit',
		help='Number of candle bars requested. Default: 60',
		type=int,
		default=60)
	parser.add_argument(
		'-t', '--timeframe',
		help='Time interval (eg. 15m, 3h, 1d) of candles. Default: 1h',
		default='1h')
	parser.add_argument(
		'-st', '--start_time',
		help='Start time filter (Unix timestamp). Default: 0',
		type=int)
	parser.add_argument(
		'-et', '--end_time',
		help='End time filter (Unix timestamp). Default: 0',
		type=int)
	parser.add_argument(
		'-rs1', '--rsi_range1',
		help='RSI range parameter (First). Default: 60,80',
		default='60,80')
	
	parser.add_argument(
		'-MACD_trend_qty',
		help='MACD trend points qty. Default: 2',
		default=2)
	parser.add_argument(
		'-MACD_flat_qty',
		help='MACD flat part points qty. Default: 2',
		default=2)
	parser.add_argument(
		'-MACD_flat_range',
		help='MACD range for considering flat. Default: 0.1',
		default=0.1)
	parser.add_argument(
		'-RSI_trend_qty',
		help='RSI trend points qty. Default: 2',
		default=2)



	args = parser.parse_args()
	symbol = args.symbol
	exchange = args.exchange
	timeframe = args.timeframe
	idle_period = ''
	stoploss = ''
	limit = args.limit	
	rsi_range1 = args.rsi_range1.split(',')
	rsi_range2 = args.rsi_range2.split(',')
	MACD_trend_qty = args.MACD_trend_qty
	MACD_flat_qty = args.MACD_flat_qty
	MACD_flat_range = args.MACD_flat_range
	RSI_trend_qty = args.RSI_trend_qty
	start_time = None
	end_time = None
	if args.start_time:
		start_time = int(round(args.start_time * 1000))
	if args.end_time:
		end_time = int(round(args.end_time * 1000))	

	trading_bot = TradingBot(symbol, exchange, timeframe, idle_period, stoploss, limit, rsi_range1, rsi_range2, MACD_trend_qty, MACD_flat_qty, MACD_flat_range, RSI_trend_qty, start_time, end_time)
	trading_bot.backtest()

	print(':: End of program ::')
	print('Done.')