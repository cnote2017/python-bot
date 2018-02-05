	parser.add_argument(
		'-i', '--idle',
		help='Idle period in seconds. Default: 300',
		default='300')
	parser.add_argument(
		'-l', '--stoploss',
		help='Stop Loss percentage. Default: 0.00%%',
		type=float,
		default='0.0')
	parser.add_argument(
		'-lt', '--limit',
		help='Number of candle bars requested. Default: 30',
		type=int,
		default=30)
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
		'-MACD_flat_rang',
		help='MACD range for considering flat. Default: 0.000001',
		default=0.000001)
	parser.add_argument(
		'-RSI_trend_qty',
		help='RSI trend points qty. Default: 2',
		default=2)

	args = parser.parse_args()
	symbol = args.symbol
	exchange = args.exchange
	timeframe = args.timeframe
	idle_period = args.idle
	stoploss = args.stoploss
	limit = args.limit
	rsi_range1 = args.rsi_range1.split(',')
	rsi_range2 = args.rsi_range2.split(',')
	MACD_trend_qty = args.MACD_trend_qty
	MACD_flat_qty = args.MACD_flat_qty
	MACD_flat_rang = args.MACD_flat_rang
	RSI_trend_qty = args.RSI_trend_qty

	trading_bot = BitfinexTradingBot(symbol, timeframe, idle_period, stoploss, limit, rsi_range1, rsi_range2, MACD_trend_qty, MACD_flat_qty, MACD_flat_rang, RSI_trend_qty)
	trading_bot.run()

	print(':: End of program ::')
	print('Done.')