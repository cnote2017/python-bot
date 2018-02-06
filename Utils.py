    @staticmethod
    def get_ticker(symbol, exchange):
        # Return most recent ticker as dict
        ticker = dict()
        if exchange=='bitfinex':
            api_path = API_BITFINEX_TICKER + '{}'.format(symbol)
            r = requests.get(API_BITFINEX_ENDPOINT + api_path)

            json_r = r.json()
            if json_r:
                ticker = {k:v for k,v in json_r.items() if k in ['last_price', 'timestamp']}
        elif exchange=='bittrex':
            pass
            api_path = API_BITFINEX_CANDLES + 'trade:{}:t{}/hist?limit={}'.format(
                interval, symbol.upper(), limit)
        elif exchange=='binance':
            r = requests.get(API_BINANCE_ENDPOINT + API_BINANCE_TICKER)

            json_r = r.json()
            if json_r:
                filtered = [it for it in json_r if it['symbol']==symbol]
                if filtered:
                    ticker = filtered[0]
                    ticker = {'last_price':v for k,v in ticker.items() if k in ['price']}
                    ts=datetime.now()
                    ticker['timestamp'] = time.mktime(ts.timetuple())

        return ticker

    @staticmethod
    def get_tickers(symbol, exchange, timeframe, limit=30, start_time=None, end_time=None):
        # Return most recent candles as DataFrame
        tickers_df = pd.DataFrame()
        if exchange=='bitfinex':
            # Set default params
            interval = timeframe
            if timeframe in bitfinex_tf:
                interval = bitfinex_tf[timeframe]['interval']

            
            if start_time:
                api_path = API_BITFINEX_CANDLES + 'trade:{}:t{}/hist?limit={}&start={}&end={}'.format(
                    interval, symbol.upper(), limit, start_time, end_time)
            r = requests.get(API_BITFINEX_ENDPOINT + api_path)

            json_r = r.json()
            if json_r:
                tickers = [{'ts':it[0], 'close':it[2]} for it in json_r]
                tickers.reverse()

                df_p=pd.DataFrame(tickers, dtype='f8')
                df_p['ts']=pd.to_datetime(df_p['ts'], unit='ms')
                df_p=df_p.set_index('ts')

                tickers_df = tickers_df.append(df_p)
        elif exchange=='bittrex':
            pass

        elif exchange=='binance':
            # Set default params
            interval = timeframe
            factor = 1
            if 'msg' not in json_r:
                json_r = json_r[-limit:]
                if factor>1:
                    indexed = enumerate(json_r,1)
                    tickers = ({'ts':it[0], 'close':it[4]} for ix, it in indexed if ix%factor==0)
                else:
                    tickers = ({'ts':it[0], 'close':it[4]} for it in json_r)

                df_p=pd.DataFrame(tickers, dtype='f8')
                df_p['ts']=pd.to_datetime(df_p['ts'], unit='ms')
                df_p=df_p.set_index('ts')

                tickers_df = tickers_df.append(df_p)
            if timeframe in binance_tf:
                interval = binance_tf[timeframe]['interval']
                factor = binance_tf[timeframe]['factor']
                limit = factor * limit

            api_path = API_BINANCE_CANDLES + '?symbol={}&interval={}&limit={}'.format(
                symbol.upper(), interval, limit)
            if start_time:
                api_path = API_BINANCE_CANDLES + '?symbol={}&interval={}&startTime={}&endTime={}'.format(
                    symbol.upper(), interval, start_time, end_time)
            r = requests.get(API_BINANCE_ENDPOINT + api_path)

            json_r = r.json()
            

        return tickers_df


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
        return str(nonceGenerator.current)
