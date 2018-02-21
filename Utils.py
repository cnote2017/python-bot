# Utility methods
import logging
import sys
import time
from datetime import datetime, timedelta

import pandas as pd
import requests

import Constants
from Constants import *


class Utils():
    @staticmethod
    def get_ticker(symbol, exchange):
        # Return most recent ticker as dict
        ticker = dict()
        if exchange == 'bitfinex':
            api_path = API_BITFINEX_TICKER + '{}'.format(symbol)
            r = requests.get(API_BITFINEX_ENDPOINT + api_path)

            json_r = r.json()
            if json_r:
                ticker = {k: v for k, v in json_r.items() if k in ['last_price', 'timestamp']}
        elif exchange == 'bittrex':
            pass

        elif exchange == 'binance':
            r = requests.get(API_BINANCE_ENDPOINT + API_BINANCE_TICKER)

            json_r = r.json()
            if json_r:
                filtered = [it for it in json_r if it['symbol'] == symbol]
                if filtered:
                    ticker = filtered[0]
                    ticker = {'last_price': v for k, v in ticker.items() if k in ['price']}
                    ts = datetime.now()
                    ticker['timestamp'] = time.mktime(ts.timetuple())

        return ticker

    @staticmethod
    def get_tickers(symbol, exchange, timeframe, limit=30, start_time=None, end_time=None):
        # Return most recent candles as DataFrame
        tickers_df = pd.DataFrame()
        # Set default params
        interval = timeframe
        if timeframe in bitfinex_tf:
            interval = bitfinex_tf[timeframe]['interval']

        api_path = API_BITFINEX_CANDLES + 'trade:{}:t{}/hist?limit={}'.format(
            interval, symbol.upper(), limit)
        if start_time:
            api_path = API_BITFINEX_CANDLES + 'trade:{}:t{}/hist?limit={}&start={}&end={}'.format(
                interval, symbol.upper(), limit, start_time, end_time)

        try:
            r = requests.get(API_BITFINEX_ENDPOINT + api_path, timeout=30)
            json_r = r.json()
            if json_r:
                tickers = [{'ts': it[0], 'close': it[2]} for it in json_r]
                tickers.reverse()

                df_p = pd.DataFrame(tickers, dtype='f8')
                df_p['ts'] = pd.to_datetime(df_p['ts'], unit='ms')
                df_p = df_p.set_index('ts')

                tickers_df = tickers_df.append(df_p)
                return tickers_df
        except:
            return None

    @staticmethod
    def get_minimum_order_size(symbol, exchange):
        assert exchange == 'bitfinex'

        r = requests.get(API_BITFINEX_SYMBOL_DETAILS)

        json_r = r.json()

        minimum_order_size = None
        for d in json_r:
            if d['pair'] == symbol.lower():
                minimum_order_size = d['minimum_order_size']

        assert minimum_order_size is not None, \
            "Could not get the minimum trade size for symbol: " + symbol

        return float(minimum_order_size)


def get_next_update_time(tframe, prev):
    if prev is None:
        prev = datetime.now()

    intervals = get_update_intervals(tframe)
    mn = prev.minute
    next_mins = [f for f in intervals if f > mn]

    add_hour = False

    if prev.minute >= intervals[-1]:
        minute = intervals[0]
        add_hour = True
    else:
        minute = next_mins[0]

    update_t = datetime(year=prev.year, month=prev.month, day=prev.day,
                        hour=prev.hour, minute=minute)

    if add_hour:
        update_t += timedelta(seconds=3600)

    return update_t


def get_update_intervals(tframe):
    supported_tframes = ['15m', '30m']
    assert tframe in supported_tframes, \
        "Supported update timeframes are: ".format(', '.join(supported_tframes))

    if tframe == '15m':
        return 0, 15, 30, 45
    if tframe == '30m':
        return 0, 30


def datetime_to_str(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def load_keys():
    import os
    if not os.path.exists('keys.txt'):
        print("Could not find 'keys.txt'. Please create the file.")

    with open('keys.txt', 'r') as f:
        lines = f.read().splitlines()
        if len(lines) < 2 or len(lines[0]) != 43 or len(lines[1]) != 43:
            print("Incorrect 'keys.txt' format. API key should be on the first line, secret on the second.")
            sys.exit(1)

        Constants.BITFINEX_API_KEY = lines[0]
        Constants.BITFINEX_API_SECRET = lines[1]


class nonceGenerator():
    current = int(int(time.time()) * int(10000000000))

    def __init__(self):
        pass

    @staticmethod
    def getNonce():
        newTimeStamp = int(int(time.time()) * int(10000000000))
        if newTimeStamp <= nonceGenerator.current:
            nonceGenerator.current = int(nonceGenerator.current) + int(1)
        else:
            nonceGenerator.current = newTimeStamp

        nonce = str(nonceGenerator.current)
        # logger = logging.getLogger('main_log')
        # logger.debug(f'Using nonce: {nonce}')
        return nonce

    
def no_exp_str(num: float):
    s = repr(num)

    if 'e' in s:
        d, e = s.split('e')
        d = d.replace('.', '').replace('-', '')
        e = int(e)
        pad = '0' * (abs(int(e)) - 1)
        sn = '-' if num < 0 else ''
        s = '{}{}{}.0'.format(sn, d, pad) if e > 0 else '{}0.{}{}'.format(sn, pad, d)

    return s
