import pandas as pd
import time
from datetime import datetime
import logging


from BotStrategy import BotStrategy
from sklearn.grid_search import ParameterGrid
from Utils import Utils, get_next_update_time, datetime_to_str
import sys
import numpy as np


        #
param_grid = {'MACD_trend_qty': [ 4, 3, 2],
              'MACD_flat_qty': [ 3, 2, 4],
              'MACD_flat_range': [0.000005, 0.00001],
              'MACD_step': [0.000005, 0.00001],
              'stop_loss': [0.015, 0.025]
              }

grid = ParameterGrid(param_grid)

symbol = 'BTGBTC'
exchange = 'bitfinex'
timeframe = '30m'
limit = 1000
start_time = int(round(1501234400 * 1000))
RSI_trend_qty = 2
MACD_strategy = 'MACD-zero'
MACD_change_direction = 0.00003
end_time = [int(round( 1510814400 * 1000)), int(round(1510814400 * 1000)), int(round(1507414400 * 1000))]
rsi_range1 = '20,40'
rsi_range2 = '55,70'
both_rsi = 1
take_profit = 0.2
delay = 0

        #
k = 0
df = pd.DataFrame()
for i in range(0,1):

    print(symbol, exchange, timeframe, limit, start_time, end_time[i])
    tickers = Utils.get_tickers(symbol, exchange, timeframe, limit, start_time, end_time[i])
    print(i)
    print(tickers.reset_index(inplace=False).loc[-1:,:] )
    for params in grid:
        k += 1
        strategy = BotStrategy(rsi_range1.split(','), rsi_range2.split(','), both_rsi, params['MACD_trend_qty'], params['MACD_flat_qty'],params['MACD_flat_range'],
                               RSI_trend_qty, params['MACD_step'], MACD_change_direction, MACD_strategy, params['stop_loss'],
                               take_profit, delay)
        _, _, _, history, sharpe_ratio = strategy.get_signal(tickers, backtesting=True)
        print('Total PNL %f, total return %f, Sharpe Ratio %f, number of deals %i' % (
                    history.trade_pnl.sum(), history.trade_return.sum(), sharpe_ratio,
                    np.count_nonzero(history.Actions.apply(lambda x: x == 'OPENBUY').values)))
        df.loc[k,'Pnl'] = history.trade_pnl.sum()
        df.loc[k, 'return'] = history.trade_return.sum()
        df.loc[k, 'end_time'] = end_time[i]
        df.loc[k, 'sharpe_ratio'] = sharpe_ratio
        df.loc[k, 'number_of_deals'] = np.count_nonzero(history.Actions.apply(lambda x: x == 'OPENBUY').values)
        df.loc[k, 'MACD_trend_qty'] = params['MACD_trend_qty']
        df.loc[k, 'MACD_flat_qty'] = params['MACD_flat_qty']
        df.loc[k, 'MACD_flat_range'] = params['MACD_flat_range']
        df.loc[k, 'MACD_step'] = params['MACD_step']
        df.loc[k, 'MACD_change_direction'] = MACD_change_direction
        df.loc[k, 'stop_loss'] = params['stop_loss']


    #
        ts = tickers.index[-1]
        last_price = tickers.loc[ts]['close']
           # Getting signals for strategy
df.to_csv('backtest_log/OPTIMIZE_{}_{}_{}_{}_'.format(exchange, symbol, MACD_strategy, timeframe) + datetime.now().strftime('%Y-%m-%d_%I-%M-%S') +'.csv', sep=',', header=True, index=True)



