#!/usr/bin/env python3
# LiveTradeBot.py - Python Trading Bot
# Strategy:
# Buy signal: MACD Hist Up + Low < RSI < High
# Sell signal: MACD Hist Down + Low < RSI < High
# Crypto Currency Exchange APIs: Bitfinex and Binance

from Parsing import parse_arguments
from TradingBot import TradingBot
from Utils import load_keys


def run():
    load_keys()
    args = parse_arguments()
    args.exchange = 'bitfinex'

    trading_bot = TradingBot(symbol=args.symbol, timeframe=args.timeframe,
                             idle_period=args.idle, exchange=args.exchange,
                             stop_loss=args.stop_loss, take_profit=args.take_profit,
                             both_rsi=args.both_rsi,
                             limit=args.limit, rsi_range1=args.rsi_range1, rsi_range2=args.rsi_range2,
                             MACD_trend_qty=args.MACD_trend_qty,
                             MACD_flat_qty=args.MACD_flat_qty, MACD_flat_range=args.MACD_flat_range,
                             RSI_trend_qty=args.RSI_trend_qty, MACD_step=args.MACD_step,
                             MACD_change_direction=args.MACD_change_direction, max_orders=args.max_orders,
                             MACD_strategy=args.MACD_strategy
                             )

    trading_bot.run()

    print(':: End of program ::')
    print('Done.')


if __name__ == "__main__":
    run()
