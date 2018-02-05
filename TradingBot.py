# TradingBot class

import time
from datetime import datetime
import logging

from BotStrategy import BotStrategy
from Utils import Utils
import sys
import numpy as np
import pandas as pd

class TradingBot():
    def __init__(self, symbol, exchange, timeframe, idle_period, stoploss, limit, rsi_range1, rsi_range2, MACD_trend_qty, MACD_flat_qty, MACD_flat_range, RSI_trend_qty, start_time=None, end_time=None):
        #
        self.symbol = symbol
        self.exchange = exchange
        self.timeframe = timeframe
        self.idle_period = idle_period
        self.stoploss = stoploss
        self.limit = limit
        self.start_time = start_time
        self.end_time = end_time
        #
        self.trade_placed = False
        self.trade_side = None
        self.stop_price = None
        #
        
        #
        self.init_logging()

    def init_logging(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # create file handler which logs INFO messages
        fh = logging.FileHandler('log_{}_{}_{}_'.format(self.exchange, self.symbol, self.timeframe) + datetime.now().strftime('%Y-%m-%d_%I-%M-%S') + '.log')
        fh.setLevel(logging.INFO)
        # create console handler which logs INFO messages
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        # create formatter and add it to the handlers
        
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        # add the handlers to logger
        self.logger.addHandler(ch)
        self.logger.addHandler(fh)

    def run(self):
        #
        min_ticker_count = 30

        ticker_count = 0

        while True:
            # #
            if ticker_count==0:
                self.logger.info('Requesting tickers... Please wait.')

            

            if len(tickers) == 0:
                self.logger.error('Failed to read tickers data. Check your input parameters.')
                sys.exit(1)

            ticker_count = len(tickers)

            #
            if (ticker_count >= min_ticker_count):
                #
                ts = tickers.index[-1]
                last_price = tickers.loc[ts]['close']
                

                # Getting signals for strategy
                ts, last_price, signal, _ = self.strategy.get_signal(tickers)

                if (not self.trade_placed):
                    if signal == 'SELL':
                        self.logger.info('Placing %s ORDER... Timestamp: %s | Last Price: %s', signal, ts, last_price)
                        status = self.place_sell_limit_order(amount=2.00, price=last_price)
                        if status['successful']:
                            self.trade_placed = True
                            self.trade_side = "Short"
                            self.stop_price = round(last_price * self.stoploss / 100, 6)
                    elif signal == 'BUY':
                        self.logger.info('Placing %s ORDER... Timestamp: %s | Last Price: %s', signal, ts, last_price)
                        status = self.place_buy_limit_order(amount=2.00, price=last_price)
                        if status['successful']:
                            self.trade_placed = True
                            self.trade_side = "Long"
                            self.stop_price = round(last_price * self.stoploss / 100, 6)
                
                

            #
            time.sleep(int(self.idle_period))

    def backtest(self):
        #
        self.logger.info('Requesting tickers... Please wait.')

        tickers = Utils.get_tickers(self.symbol, self.exchange, self.timeframe, self.limit, self.start_time, self.end_time)

        if len(tickers) == 0:
            self.logger.error('Failed to read tickers data. Check your input parameters.')
            sys.exit(1)

        #
        ts = tickers.index[-1]
        last_price = tickers.loc[ts]['close']
        self.logger.info('%s Tickers requested... Timestamp: %s | Last Price: %s', len(tickers), ts, last_price)

        # Getting signals for strategy
        _, _, _, history = self.strategy.get_signal(tickers, backtesting=True)

        if self.start_time:
            print(history)
            print('Total PNL %f, total return %f, number of deals %i' % (history.trade_pnl.sum(), history.trade_return.sum(), np.count_nonzero(history.trade_pnl)))
            history.to_csv('backtest_{}_{}_{}_'.format(self.exchange, self.symbol, self.timeframe) + datetime.now().strftime('%Y-%m-%d_%I-%M-%S') +'.csv', sep=',', header=True, index=True)


    def place_buy_limit_order(self, amount=0.00, price=0.00):
        """
        :param amount: type Decimal.
        :param price: type Decimal.
        :return: {
            "successful": True/False,
            "order_id": order_id, required if successful is true
        }
        """
        return {
            "successful": True
        }

    def place_sell_limit_order(self, amount=0.00, price=0.00):
        """
        :param amount: type Decimal.
        :param price: type Decimal.
        :return: {
            "successful": True/False,
            "order_id": order_id, required if successful is true
        }
        """
        return {
            "successful": True
        }
