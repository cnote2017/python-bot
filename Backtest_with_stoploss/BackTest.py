#!/usr/bin/env python3
# BackTest.py - Backtesting of Python Trading Bot
# Strategy: 
# Buy signal: MACD Hist Up + Low < RSI < High
# Sell signal: MACD Hist Down + Low < RSI < High

from Parsing import parse_arguments
from TradingBot import TradingBot

def run():
    args = parse_arguments()

    trading_bot = TradingBot(symbol=args.symbol, exchange=args.exchange, timeframe=args.timeframe,
                             idle_period=args.idle,
                             limit=args.limit, rsi_range1=args.rsi_range1, rsi_range2=args.rsi_range2,
                             both_rsi=args.both_rsi, MACD_trend_qty=args.MACD_trend_qty,
                             MACD_flat_qty=args.MACD_flat_qty, MACD_flat_range=args.MACD_flat_range,
                             RSI_trend_qty=args.RSI_trend_qty, MACD_step=args.MACD_step,
                             MACD_change_direction=args.MACD_change_direction, MACD_strategy=args.MACD_strategy, stop_loss = args.stop_loss,
                             take_profit =args.take_profit, start_time=args.start_time,
                             end_time=args.end_time)

    trading_bot.backtest()

    print(':: End of program ::')
    print('Done.')


if __name__ == "__main__":
    run()
