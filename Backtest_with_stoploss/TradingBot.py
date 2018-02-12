# TradingBot class

import time
from datetime import datetime
import logging

import Constants
from BotStrategy import BotStrategy
from Orders import OrderManager
from Utils import Utils, get_next_update_time, datetime_to_str
import sys
import numpy as np

class TradingBot():
    def __init__(self, symbol='', exchange='', timeframe='', idle_period=None,
                 limit=None, rsi_range1=None, rsi_range2=None,both_rsi=None, MACD_trend_qty=None, MACD_flat_qty=None,
                 MACD_flat_range=None, RSI_trend_qty=None, MACD_step=None, MACD_change_direction = None,
                 MACD_strategy=None, stop_loss=None, take_profit=None, start_time=None, end_time=None, max_orders=None, paper_trade=False):
        #
        self.symbol = symbol
        self.exchange = exchange
        self.timeframe = timeframe
        self.idle_period = int(idle_period)
        self.limit = limit
        self.start_time = start_time
        self.end_time = end_time
        self.max_orders = max_orders
        self.MACD_strategy = MACD_strategy
        self.paper_trade = paper_trade
        self.both_rsi = both_rsi
        self.stop_loss =stop_loss
        self.take_profit = take_profit
        #
        self.logger = None
        #
        if rsi_range2[0] > rsi_range1[1]:
            self.strategy = BotStrategy(rsi_range1, rsi_range2, both_rsi, MACD_trend_qty, MACD_flat_qty, MACD_flat_range, RSI_trend_qty, MACD_step, MACD_change_direction, MACD_strategy, stop_loss, take_profit)
        else:
            print(':: ERROR ::')
            print('Incorrect values for RSI ranges. Please input rsi1 < rsi2')
            assert((rsi_range2[0] > rsi_range1[1]))

        self.order_size = None
        self.order_manager = OrderManager(self)
        self.init_logging()

    def init_logging(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # create file handler which logs INFO messages
        fh = logging.FileHandler(
            'just_log/log_{}_{}_{}_'.format(self.exchange, self.symbol, self.timeframe) + datetime.now().strftime(
                '%Y-%m-%d_%I-%M-%S') + '.log')
        fh.setLevel(logging.INFO)
        # create console handler which logs INFO messages
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        # add the handlers to logger
        self.logger.addHandler(ch)
        self.logger.addHandler(fh)

    def set_minimum_order_size(self):
        """ While testing, use the minimum order size for the symbol."""
        self.order_size = Utils.get_minimum_order_size(self.symbol, self.exchange)
        self.logger.info('Setting the order size to minimum for %s: %.3f'
                         % (self.symbol, self.order_size))

    def get_current_price(self):
        """ Price of the latest trade on the exchange."""
        r = Utils.get_ticker(self.symbol, self.exchange)
        price = float(r['last_price'])
        return price

    def run(self):
        if Constants.BITFINEX_API_SECRET:
            input("!!! Using API KEY. Press enter to continue. ")

        min_ticker_count = 100
        self.set_minimum_order_size()

        next_update_time = get_next_update_time(self.timeframe, datetime.utcnow())
        self.logger.info("Bot started. Waiting for the next data update on "
                         + datetime_to_str(next_update_time))
        print("UTC time: " + datetime_to_str(datetime.utcnow()))
        next_order_update_time = None

        while True:
            if next_order_update_time is None or time.time() > next_order_update_time:
                next_order_update_time = time.time() + Constants.ORDER_UPDATE_INTERVAL
                self.order_manager.update_orders()

            if datetime.utcnow() > next_update_time:
                tickers = self.update_data()
                assert(self.timeframe in ('15m', '30m'))
                delay = (next_update_time - tickers.index[-1]).seconds / 60
                if delay > 10:
                    time.sleep(20)
                    continue

                ticker_count = len(tickers)

                self.logger.info('Received tickers.')
                if ticker_count == 0:
                    self.logger.error('Failed to read tickers data. Check your input parameters.')
                    sys.exit(1)

                if ticker_count < min_ticker_count:
                    self.logger.error('Insufficient number of tickers. Check your input parameters.')
                    sys.exit(1)

                ts = tickers.index[-1]
                last_price = tickers.loc[ts]['close']
                self.logger.info('%s Tickers received... Last timestamp: %s | Last Price: %s', len(tickers), ts,
                                 last_price)

                # Getting signals for strategy
                ts, last_price, signal, _,_ = self.strategy.get_signal(tickers)
                if signal is not None:
                    self.order_manager.handle_trade_signal(signal)
                    self.logger.info('Finished processing the signal.')
                else:
                    self.logger.info('No signal to trade.')

                next_update_time = get_next_update_time(self.timeframe, next_update_time)
                self.logger.info("Waiting for the next data update on "
                                 + datetime_to_str(next_update_time))

            time.sleep(Constants.TICKER_UPDATE_INTERVAL)

    def update_data(self):
        for _ in range(20):
            tickers = Utils.get_tickers(self.symbol, self.exchange, self.timeframe, self.limit)

            if tickers is None:
                self.logger.info('Could not get the data from the exchange. Will try again in 10 seconds.')
                time.sleep(10)
            else:
                # self.logger.info('Received tickers from the exchange.')
                return tickers

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
        _, _, _, history,sharpe_ratio = self.strategy.get_signal(tickers, backtesting=True)

        if self.start_time:
            print(history)
            print('Total PNL %f, total return %f, Sharpe Ratio %f, number of deals %i' % (history.trade_pnl.sum(), history.trade_return.sum(), sharpe_ratio, np.count_nonzero(history.Actions.apply(lambda x: x == 'OPENBUY').values)))
            history.to_csv('backtest_log/backtest_{}_{}_{}_{}_'.format(self.exchange, self.symbol,self.MACD_strategy, self.timeframe) + datetime.now().strftime('%Y-%m-%d_%I-%M-%S') +'.csv', sep=',', header=True, index=True)
