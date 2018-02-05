class BotStrategy(object):
    def __init__(self, rsi_range1, rsi_range2, MACD_trend_qty, MACD_flat_qty, MACD_flat_range, RSI_trend_qty):
        self.rsi_range1 = rsi_range1
        self.rsi_range2 = rsi_range2
        
        self.MACD_flat_qty = MACD_flat_qty
        self.MACD_flat_range = MACD_flat_range
        self.RSI_trend_qty = RSI_trend_qty

    def get_macd_signal(self, tickers):
        # Compute MACD lines
        macd_hist = indicator.get_macd_histogram(tickers['close'])
        df_p = tickers.copy()
        # Compute MACD signal
        df_p['crossover']=0
        
        
        df_p['crossover_shift']= df_p['crossover'].shift(1)
        # df_p['buy/sell'] = df_p['crossover'] - df_p['crossover_shift']
        df_p['buy/sell']=df_p['buy/sell'].where(df_p['crossover_shift']!=0, 0)
        df_p['buy/sell'] /= 2
        df_p['macd'] = df_p['buy/sell']
        # Set return vars
        ts=df_p.index[-1]
        last_price=round(df_p.loc[ts]['close'], 6)
        bs=df_p.loc[ts]['buy/sell']
        

        return ts, last_price, signal_out, df_p.macd

    def get_macd_signal_with_trend(self, tickers, MACD_trend_qty, MACD_flat_qty, MACD_flat_range):
        m = MACD_trend_qty
        n = MACD_flat_qty
        epsilon = MACD_flat_range
        # Compute MACD lines