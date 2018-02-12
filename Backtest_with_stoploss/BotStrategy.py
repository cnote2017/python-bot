# Strategies for Trading Bot 
# MACD histogram, RSI, EMA
import math
import numpy as np
from BotIndicator import BotIndicator as indicator


class BotStrategy(object):
    def __init__(self, rsi_range1, rsi_range2, both_rsi, MACD_trend_qty, MACD_flat_qty, MACD_flat_range, RSI_trend_qty, MACD_step, MACD_change_direction, MACD_strategy, stop_loss, take_profit):
        self.rsi_range1 = rsi_range1
        self.rsi_range2 = rsi_range2
        self.MACD_trend_qty = MACD_trend_qty
        self.MACD_flat_qty = MACD_flat_qty
        self.MACD_flat_range = MACD_flat_range
        self.RSI_trend_qty = RSI_trend_qty
        self.MACD_step = MACD_step
        self.MACD_change_direction = MACD_change_direction
        self.MACD_strategy = MACD_strategy
        self.both_rsi = both_rsi
        self.stop_loss = stop_loss
        self.take_profit = take_profit


    def get_macd_signal(self, tickers):
        # Compute MACD lines
        macd_hist = indicator.get_macd_histogram(tickers['close'])
        df_p = tickers.copy()
        # Compute MACD signal
        df_p['crossover']=0
        df_p['crossover']=df_p['crossover'].where(~(macd_hist > 0), 1)
        df_p['crossover']=df_p['crossover'].where(~(macd_hist < 0), -1)
        df_p['crossover_shift']= df_p['crossover'].shift(1)
        df_p['buy/sell'] = df_p['crossover'] - df_p['crossover_shift']
        df_p['buy/sell']=df_p['buy/sell'].where(df_p['crossover_shift']!=0, 0)
        df_p['buy/sell'] /= 2
        df_p['macd'] = df_p['buy/sell']
        # Set return vars
        ts=df_p.index[-1]
        last_price=round(df_p.loc[ts]['close'], 6)
        bs=df_p.loc[ts]['buy/sell']
        signal_out='UP' if bs>0 else 'DOWN' if bs<0 else ''

        return ts, last_price, signal_out, df_p.macd

    def get_macd_signal_with_trend(self, tickers, MACD_trend_qty, MACD_flat_qty, MACD_flat_range, MACD_step, MACD_change_direction):
        m = MACD_trend_qty
        n = MACD_flat_qty
        epsilon1 = MACD_flat_range
        epsilon2 = MACD_step
        epsilon3 = MACD_change_direction
        # Compute MACD lines
        macd_hist = indicator.get_macd_histogram(tickers['close'])
        df_p = tickers.copy()
        df_p['MACD'] = macd_hist
        df_p['MACDsignal'] = 0
        df_p.reset_index(inplace=True)
        # Compute MACD signal
        # MACDsigal 1 up trend, -1 down trend, 2 became flattish, 3 break up trend, -3 break down trend
        for i in range(m,len(df_p)):
            if ~math.isnan(df_p.loc[i-m, 'MACD']):
                df_p.loc[i,'MACDsignal'] = indicator.is_trend_or_flat(df_p.loc[i - m:i,'MACD'],df_p.loc[i - n:i, 'MACD'], epsilon1, epsilon2)

                if (df_p.loc[i-1,'MACDsignal'] == 1 or df_p.loc[i-1,'MACDsignal'] == 0) and df_p.loc[i,'MACDsignal'] != -1 and (df_p.loc[i,'MACD']+epsilon3 < (df_p.loc[i-1,'MACD'])):
                    df_p.loc[i, 'MACDsignal'] = 3

        df_p.index = df_p.ts
        ts=df_p.index[-1]
        last_price=round(df_p.loc[ts]['close'], 6)

        return ts, last_price, df_p.MACDsignal, df_p.MACD


    def get_ma_signal(self, tickers, timeframe='short', ratio=0.0):
        if timeframe=='short':
            # Compute SMA lines
            slow, fast = indicator.get_sma_lines(tickers['close'], slow=15, fast=5)
        else:
            # Compute EMA lines
            slow, fast = indicator.get_ema_lines(tickers['close'], slow=20, fast=5)

        #
        test_buy = fast - slow > 0
        test_sell = slow - fast < 0
        if ratio>0.0:
            delta = 100 * (fast / slow - 1)
            test_buy = delta >= ratio
            # 
            delta = 100 * (slow / fast - 1)
            test_sell = delta >= ratio

        df_p = tickers.copy()
        # Compute MA signal
        df_p['crossover']=0
        df_p['crossover']=df_p['crossover'].where(~(test_buy), 1)
        df_p['crossover']=df_p['crossover'].where(~(test_sell), -1)
        df_p['buy/sell']=df_p['crossover']
        # if ratio==0.0:
        #   df_p['buy/sell']=df_p[['crossover']].apply(lambda x: x - x.shift())
        df_p['buy/sell']=df_p['buy/sell'].where(df_p['crossover']!=0, 0)
        df_p['ema'] = df_p['buy/sell']

        # Set return vars
        ts=df_p.index[-1]
        last_price=round(df_p.loc[ts]['close'], 6)
        bs=df_p.loc[ts]['buy/sell']
        signal_out='BUY' if bs>0 else 'SELL' if bs<0 else ''

        return ts, last_price, signal_out, df_p.ema

    def get_rsi_signal(self, tickers,rsi_range1, rsi_range2):
        # Compute RSI
        rsi = indicator.compute_rsi(tickers['close'])
        df_p = tickers.copy()
        df_p['Real_RSI'] = rsi
        df_p['RSIsignal'] = 0
        if self.both_rsi == 1 :
            low1 = float(rsi_range1[0])
            high1 = float(rsi_range1[-1])
            low2 = float(rsi_range2[0])
            high2 = float(rsi_range2[-1])
            # Compute RSI signal
            df_p['R1'] = 0
            df_p['R2'] = 0
            df_p['R3'] = 0
            df_p['R4'] = 0
            df_p['R1']=df_p['R1'].where(~((low1 < rsi) & (rsi < high1 )), 1)
            df_p['R2'] = df_p['R2'].where(~((low2 < rsi) & (rsi < high2)), 2)
            df_p['R3'] = df_p['R3'].where(~((rsi > high1) & (rsi < low2)), 3)
            df_p['R4'] = df_p['R4'].where(~(rsi > high2), 4)
            df_p['RSIsignal'] = df_p['R1'] | df_p['R2'] | df_p['R3'] | df_p['R4']
        elif self.both_rsi == 0:
            low1 = float(rsi_range1[0])
            high1 = float(rsi_range1[-1])
            # Compute RSI signal
            df_p['R1'] = 0
            df_p['R3'] = 0
            df_p['R1'] = df_p['R1'].where(~((low1 < rsi) & (rsi < high1)), 1)
            df_p['R3'] = df_p['R3'].where(~(rsi > high1), 3)
            df_p['RSIsignal'] = df_p['R1'] | df_p['R3']
        # Set return vars
        ts=df_p.index[-1]
        last_price=round(df_p.loc[ts]['close'], 6)

        return ts, last_price, df_p.RSIsignal, df_p.Real_RSI

    def get_rsi_signal_with_trend(self, tickers, rsi_range, RSI_trend_qty):
        #compute RSI
        rsi = indicator.compute_rsi(tickers['close'])
        low = float(rsi_range[0])
        high = float(rsi_range[-1])
        df_p = tickers.copy()
        m =  RSI_trend_qty
        df_p['RSI'] = rsi
        df_p['RSIsignal'] = 0
        df_p['signal_zone'] = 0
        df_p['RSItrend'] = 0
        df_p['signal_zone'] = df_p['signal_zone'].where(~((low < rsi) & (rsi < high)), 1)
        df_p.reset_index(inplace=True)
        for i in range(m,len(df_p)):
            if ~math.isnan(df_p.loc[i-m, 'RSI']):
                # Checking if there is a trend in RSI lines
                df_p.loc[i,'RSItrend'] = indicator.is_trend(df_p.loc[i - m:i,'RSI'])

        # Setting signal : trend + low<RSI<high
        df_p['RSIsignal'] = df_p['RSItrend'] * df_p['signal_zone']
        df_p.index = df_p.ts
        ts = df_p.index[-1]
        last_price = round(df_p.loc[ts]['close'], 6)
        bs = df_p.loc[ts]['RSIsignal']
        signal_out = 'BUY' if bs > 0 else 'SELL' if bs<0 else ''

        return ts, last_price, signal_out, df_p.RSIsignal, df_p.RSI



    def get_signal(self, tickers, backtesting=False):
        _, _, macd, real_MACD = \
                self.get_macd_signal_with_trend(tickers, self.MACD_trend_qty, self.MACD_flat_qty,
                                        self.MACD_flat_range, self.MACD_step, self.MACD_change_direction)
        ts, last_price, rsi, real_rsi = self.get_rsi_signal(tickers, self.rsi_range1, self.rsi_range2)
        tickers = tickers.join(macd)
        tickers = tickers.join(rsi)

        signal = None

        if backtesting == False:
            # Stategy
            # Buy signal: MACD trend is up, going from negative to positive  and + Low < RSI < High
            # MACD flat or RSI is out of the range 1 or range 2 - close the position
            # MACD breaking upped trend - closebuy
            tickers = tickers.join(real_MACD)
            tickers = tickers.join(real_rsi)
            if self.MACD_strategy == 'MACD-zero':
                actions, signal = self.get_actions_MACD_zero(tickers, False)
            elif self.MACD_strategy == 'MACD-uptrend':
                actions, signal = self.get_actions_MACD_uptrend(tickers, False)

        else:
            tickers = tickers.join(real_MACD)
            tickers = tickers.join(real_rsi)
            # Buy signal: MACD trend is up, going from negative to positive  and + Low < RSI < High
            # MACD flat or RSI is out of the range 1 or range 2 - close the position
            # MACD breaking upped trend - closebuy
            if self.MACD_strategy == 'MACD-zero':
                actions, signal = self.get_actions_MACD_zero(tickers, True)
            elif self.MACD_strategy == 'MACD-uptrend':
                actions, signal = self.get_actions_MACD_uptrend(tickers, True)
            tickers = tickers.join(actions)
            pnl, ret = self.calculate_pnl(tickers)
            tickers = tickers.join(pnl)
            tickers = tickers.join(ret)
            index = (ret != 0)
            sharpe_ratio = ret[index].mean()/ret[index].std()


        return ts, last_price, signal, tickers, sharpe_ratio

    def get_actions_MACD_zero(self, tickers, is_stoploss):
        df_p = tickers.copy()
        df_p.reset_index(inplace=True)
        df_p['Actions'] = 0
        sign = 0
        count = 0
        sum = 0
        if self.both_rsi==1:
            for i in range(1,len(df_p)):
                if df_p.loc[i,'MACDsignal'] == 1 and df_p.loc[i-1,'MACD'] <= 0 \
                        and df_p.loc[i, 'MACD'] >= 0 and  df_p.loc[i,'RSIsignal'] == 1:
                    df_p.loc[i,'Actions'] = 'OPENBUY'
                    sign = 1
                    count += 1
                    sum += df_p.loc[i,'close']
                if df_p.loc[i, 'MACDsignal'] == 1 and df_p.loc[i - 1, 'MACD'] <= 0 \
                        and df_p.loc[i, 'MACD'] >= 0 and df_p.loc[i, 'RSIsignal'] == 2:
                    df_p.loc[i,'Actions'] = 'OPENBUY'
                    sign = 2
                    count +=1
                    sum += df_p.loc[i, 'close']
                if sign == 1 and df_p.loc[i,'MACDsignal'] == 1 and df_p.loc[i,'RSIsignal'] == 1:
                    df_p.loc[i,'Actions'] = 'OPENBUY'
                    count += 1
                    sum += df_p.loc[i, 'close']
                if sign == 2  and df_p.loc[i, 'MACDsignal'] == 1 and df_p.loc[i, 'RSIsignal'] == 2:
                    df_p.loc[i, 'Actions'] = 'OPENBUY'
                    count += 1
                    sum += df_p.loc[i, 'close']
                if sign == 1 and (df_p.loc[i,'RSIsignal'] == 3 or (df_p.loc[i,'MACDsignal'] == 3 or df_p.loc[i,'MACDsignal'] == 2 or df_p.loc[i,'MACDsignal'] == -1)):
                    df_p.loc[i, 'Actions'] = 'CLOSEBUY'
                    sign = 0
                    count = 0
                    sum = 0
                if sign == 2 and (df_p.loc[i,'RSIsignal'] == 4 or (df_p.loc[i,'MACDsignal'] == 3 or df_p.loc[i,'MACDsignal'] == 2 or df_p.loc[i,'MACDsignal'] == -1)):
                    df_p.loc[i, 'Actions'] = 'CLOSEBUY'
                    sign = 0
                    count = 0
                    sum = 0
                if is_stoploss and sign != 0 and ((sum/count)- df_p.loc[i,'close'])/(sum/count) > self.stop_loss:
                    df_p.loc[i, 'Actions'] = 'STOPLOSS'
                    sign = 0
                    count = 0
                    sum = 0
                if is_stoploss and sign != 0 and ( df_p.loc[i, 'close']-(sum / count)) / (
                    sum / count) > self.take_profit:
                    df_p.loc[i, 'Actions'] = 'TAKEPROFIT'
                    sign = 0
                    count = 0
                    sum = 0
        elif self.both_rsi == 0:
            for i in range(1,len(df_p)):
                if df_p.loc[i,'MACDsignal'] == 1 and df_p.loc[i-1,'MACD'] <= 0 \
                        and df_p.loc[i, 'MACD'] >= 0 and  df_p.loc[i,'RSIsignal'] == 1:
                    df_p.loc[i,'Actions'] = 'OPENBUY'
                    sign = 1
                    count += 1
                    sum += df_p.loc[i, 'close']
                if sign == 1 and df_p.loc[i,'MACDsignal'] == 1 and df_p.loc[i,'RSIsignal'] == 1:
                    df_p.loc[i,'Actions'] = 'OPENBUY'
                    count += 1
                    sum += df_p.loc[i, 'close']
                if sign == 1 and (df_p.loc[i,'RSIsignal'] == 3 or (df_p.loc[i,'MACDsignal'] == 3 or df_p.loc[i,'MACDsignal'] == 2 or df_p.loc[i,'MACDsignal'] == -1)):
                    df_p.loc[i, 'Actions'] = 'CLOSEBUY'
                    sign = 0
                    count = 0
                    sum = 0
                if is_stoploss and sign != 0 and ((sum/count)- df_p.loc[i,'close'])/(sum/count) > self.stop_loss:
                    df_p.loc[i, 'Actions'] = 'STOPLOSS'
                    sign = 0
                    count = 0
                    sum = 0
                if is_stoploss and sign != 0 and ( df_p.loc[i, 'close']-(sum / count)) / (
                    sum / count) > self.take_profit:
                    df_p.loc[i, 'Actions'] = 'TAKEPROFIT'
                    sign = 0
                    count = 0
        df_p.index = df_p.ts
        ts = df_p.index[-1]
        signal = df_p.loc[ts]['Actions']
        if signal == 0:
            signal = ''
        return df_p.Actions, signal

    def get_actions_MACD_uptrend(self, tickers, is_stoploss):
        df_p = tickers.copy()
        df_p.reset_index(inplace=True)
        df_p['Actions'] = 0
        sign = 0
        count = 0
        sum = 0
        if self.both_rsi == 1:
            for i in range(1, len(df_p)):
                if df_p.loc[i, 'MACDsignal'] == 1 and df_p.loc[i, 'RSIsignal'] == 1:
                    df_p.loc[i, 'Actions'] = 'OPENBUY'
                    sign = 1
                    count += 1
                    sum += df_p.loc[i, 'close']
                if df_p.loc[i, 'MACDsignal'] == 1 and df_p.loc[i, 'RSIsignal'] == 2:
                    df_p.loc[i, 'Actions'] = 'OPENBUY'
                    sign = 2
                    count += 1
                    sum += df_p.loc[i, 'close']
                if sign == 1 and (df_p.loc[i, 'RSIsignal'] == 3 or (
                        df_p.loc[i, 'MACDsignal'] == 2 or df_p.loc[i, 'MACDsignal'] == -1 or df_p.loc[i,'MACDsignal'] == 3)):
                    df_p.loc[i, 'Actions'] = 'CLOSEBUY'
                    sign = 0
                    count = 0
                    sum = 0
                if sign == 2 and (df_p.loc[i, 'RSIsignal'] == 4 or (
                        df_p.loc[i, 'MACDsignal'] == 2 or df_p.loc[i, 'MACDsignal'] == -1 or df_p.loc[i,'MACDsignal'] == 3)):
                    df_p.loc[i, 'Actions'] = 'CLOSEBUY'
                    sign = 0
                    count = 0
                    sum = 0
                if is_stoploss and sign != 0 and ((sum/count)- df_p.loc[i,'close'])/(sum/count) > self.stop_loss:
                    df_p.loc[i, 'Actions'] = 'STOPLOSS'
                    sign = 0
                    count = 0
                    sum = 0
                if is_stoploss and sign != 0 and ( df_p.loc[i, 'close']-(sum / count)) / (
                    sum / count) > self.take_profit:
                    df_p.loc[i, 'Actions'] = 'TAKEPROFIT'
                    sign = 0
                    count = 0
                    sum = 0
        elif self.both_rsi == 0:
            for i in range(1, len(df_p)):
                if df_p.loc[i, 'MACDsignal'] == 1 and df_p.loc[i, 'RSIsignal'] == 1:
                    df_p.loc[i, 'Actions'] = 'OPENBUY'
                    sign = 1
                    count += 1
                    sum += df_p.loc[i, 'close']
                if sign == 1 and (df_p.loc[i, 'RSIsignal'] == 3 or (
                        df_p.loc[i, 'MACDsignal'] == 2 or df_p.loc[i, 'MACDsignal'] == -1) or df_p.loc[i,'MACDsignal'] == 3):
                    df_p.loc[i, 'Actions'] = 'CLOSEBUY'
                    sign = 0
                    count = 0
                    sum = 0
                if is_stoploss and sign != 0 and ((sum/count)- df_p.loc[i,'close'])/(sum/count) > self.stop_loss:
                    df_p.loc[i, 'Actions'] = 'STOPLOSS'
                    sign = 0
                    count = 0
                    sum = 0
                if is_stoploss and sign != 0 and ( df_p.loc[i, 'close']-(sum / count)) / (
                    sum / count) > self.take_profit:
                    df_p.loc[i, 'Actions'] = 'TAKEPROFIT'
                    sign = 0
                    count = 0
                    sum = 0
        df_p.index = df_p.ts
        ts = df_p.index[-1]
        signal = df_p.loc[ts]['Actions']
        if signal == 0:
            signal = ''
        return df_p.Actions, signal

    def calculate_pnl(self, tickers):
        df_p = tickers.copy()
        df_p.reset_index(inplace=True)
        Buy_position = False
        Sell_position =False
        start = 0
        trade_pnl = 0
        trade_return = 0
        open_pos = []
        sign = 0
        position_count = 0
        for i in range(1,len(df_p)-1):
            trade_pnl = 0
            trade_return = 0
            if df_p.loc[i,'Actions'] == 'OPENBUY' and ~Sell_position:
                start += df_p.loc[i,'close']
                open_pos.append(df_p.loc[i,'close'])
                position_count += 1
                sign = 1
                Buy_position =True

            if df_p.loc[i,'Actions'] == 'CLOSEBUY' and Buy_position:
                Buy_position = False
                trade_pnl = (df_p.loc[i, 'close'] * position_count - start) * sign
                trade_return = np.sum((-x+df_p.loc[i, 'close'])/x for x in open_pos)
                start = 0
                sign = 0
                position_count = 0
                open_pos = []
            if df_p.loc[i, 'Actions'] == 'STOPLOSS' and Buy_position:
                Buy_position = False
                trade_pnl = start *(-self.stop_loss)
                trade_return = np.sum((-x + start *(1-self.stop_loss)/position_count) / x for x in open_pos)
                start = 0
                sign = 0
                position_count = 0
                open_pos = []
            if df_p.loc[i, 'Actions'] == 'TAKEPROFIT' and Buy_position:
                Buy_position = False
                trade_pnl = start * self.take_profit
                trade_return = np.sum((-x + start *(1+self.stop_loss)/position_count) / x for x in open_pos)
                start = 0
                sign = 0
                position_count = 0
                open_pos = []

            if df_p.loc[i,'MACDsignal'] == -1 and Buy_position:
                Buy_position = False
                trade_pnl = (df_p.loc[i, 'close'] * position_count - start) * 1
                trade_return = np.sum((-x + df_p.loc[i, 'close']) / x for x in open_pos)
                start = 0
                sign = 0
                position_count = 0
                open_pos = []
            df_p.loc[i,'trade_pnl'] = trade_pnl
            df_p.loc[i, 'trade_return'] = trade_return
        df_p.index = df_p.ts
        return df_p.trade_pnl, df_p.trade_return


