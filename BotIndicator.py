# Indicator methods for Trading Bot 

class BotIndicator():

    @staticmethod
    def get_rolling_ema(values, window):
        """Return rolling EMA of given values, using specified window size."""
        # Compatible with Python 3.5+
        return values.ewm(span=window, min_periods=window+1).mean()

    @staticmethod
    def get_rolling_mean(values, window):
        """Return rolling mean of given values, using specified window size."""
        # Compatible with Python 3.5+
        return values.rolling(window=window).mean()

    @staticmethod
    def get_macd_lines(values, slow=26, fast=12):
        """Return MACD and signal lines."""
        ema_fast = BotIndicator.get_rolling_ema(values, fast)
        ema_slow = BotIndicator.get_rolling_ema(values, slow)
        macd = ema_fast - ema_slow
        signal = BotIndicator.get_rolling_ema(macd, 9)

        return macd, signal

    @staticmethod
    def get_macd_histogram(values, slow=26, fast=12, very_fast = 9):
        """return MACD hystogram"""
        ema_fast = BotIndicator.get_rolling_ema(values, fast)
        ema_slow = BotIndicator.get_rolling_ema(values, slow)
        macd = ema_fast - ema_slow
        signal = BotIndicator.get_rolling_ema( macd, very_fast)
        macd_hist = macd -signal

        return macd_hist

    @staticmethod
    def get_sma_lines(values, slow=20, fast=5):
        """Return SMA slow and fast lines."""
        sma_slow = BotIndicator.get_rolling_mean(values, slow)
        sma_fast = BotIndicator.get_rolling_mean(values, fast)

        return sma_slow, sma_fast

    @staticmethod
    def get_ema_lines(values, slow=20, fast=5):
        """Return EMA slow and fast lines."""
        ema_slow = BotIndicator.get_rolling_ema(values, slow)
        ema_fast = BotIndicator.get_rolling_ema(values, fast)

        return ema_slow, ema_fast 

    @staticmethod
    def compute_rsi(values, period=14):
        # Compute Wilder's RSI indicator

        delta = values.diff()
        up, down = delta.copy(), delta.copy()

        up[up < 0] = 0
        down[down > 0] = 0

        ema_up = up.ewm(com=period-1).mean()
        ema_down =down.ewm(com=period-1).mean().abs()
        # 
        rs = ema_up / ema_down
        rsi = 100.0 - (100.0 / (1.0 + rs))

        return rsi

    @staticmethod
    def is_trend_or_flat(L1,L2, epsilon):
        # find, if sequence L is increasing 1 or decreasing -1 or flat 2
        r = 0
        m1 = all(x*(1 + epsilon) < y for x, y in zip(L1, L1[1:]))
        m2 = all(x*(1 - epsilon) > y for x, y in zip(L1, L1[1:]))
        m3 = all(abs((x - y)/x) < epsilon for x, y in zip(L2, L2[1:])) * 2
        if m1:
            r = 1
        if m2:
            r = -1
        if m3:
            r = 2
        return r
    def is_trend(L):
        # find, if sequence L is increasing 1 or decreasing -1
        r = 0
        m1 = all(x  < y for x, y in zip(L, L[1:]))
        m2 = all(x  > y for x, y in zip(L, L[1:]))
        if m1:
            r = 1
        if m2:
            r = -1
        return r

