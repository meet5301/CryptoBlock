import numpy as np


class IndicatorEngine:
    def __init__(self, candles: list):
        # candles: [{"t":ms, "o":float, "h":float, "l":float, "c":float}, ...]
        self.candles = candles
        if candles:
            self.closes = np.array([c["c"] for c in candles], dtype=float)
            self.highs  = np.array([c["h"] for c in candles], dtype=float)
            self.lows   = np.array([c["l"] for c in candles], dtype=float)
            self.opens  = np.array([c["o"] for c in candles], dtype=float)
            self.volumes = np.array([c.get("v", 0) for c in candles], dtype=float)
        else:
            self.closes = self.highs = self.lows = self.opens = self.volumes = np.array([])

    def _pad(self, arr, length):
        pad = [None] * (length - len(arr))
        return pad + list(arr)

    def sma(self, period: int) -> list:
        n = len(self.closes)
        if n < period:
            return [None] * n
        result = [None] * (period - 1)
        for i in range(period - 1, n):
            result.append(round(float(np.mean(self.closes[i - period + 1:i + 1])), 4))
        return result

    def ema(self, period: int) -> list:
        n = len(self.closes)
        if n < period:
            return [None] * n
        k = 2.0 / (period + 1)
        result = [None] * (period - 1)
        ema_val = float(np.mean(self.closes[:period]))
        result.append(round(ema_val, 4))
        for price in self.closes[period:]:
            ema_val = price * k + ema_val * (1 - k)
            result.append(round(ema_val, 4))
        return result

    def bollinger_bands(self, period: int = 20, std_dev: float = 2.0) -> dict:
        n = len(self.closes)
        upper, mid, lower = [], [], []
        for i in range(n):
            if i < period - 1:
                upper.append(None); mid.append(None); lower.append(None)
            else:
                window = self.closes[i - period + 1:i + 1]
                m = float(np.mean(window))
                s = float(np.std(window, ddof=0))
                mid.append(round(m, 4))
                upper.append(round(m + std_dev * s, 4))
                lower.append(round(m - std_dev * s, 4))
        return {"upper": upper, "mid": mid, "lower": lower}

    def rsi(self, period: int = 14) -> list:
        n = len(self.closes)
        if n < period + 1:
            return [None] * n
        deltas = np.diff(self.closes)
        gains = np.where(deltas > 0, deltas, 0.0)
        losses = np.where(deltas < 0, -deltas, 0.0)
        result = [None] * period
        avg_gain = float(np.mean(gains[:period]))
        avg_loss = float(np.mean(losses[:period]))
        if avg_loss == 0:
            result.append(100.0)
        else:
            rs = avg_gain / avg_loss
            result.append(round(100 - 100 / (1 + rs), 2))
        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            if avg_loss == 0:
                result.append(100.0)
            else:
                rs = avg_gain / avg_loss
                result.append(round(100 - 100 / (1 + rs), 2))
        return result

    def macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
        ema_fast = self.ema(fast)
        ema_slow = self.ema(slow)
        n = len(self.closes)
        macd_line = []
        for f, s in zip(ema_fast, ema_slow):
            if f is None or s is None:
                macd_line.append(None)
            else:
                macd_line.append(round(f - s, 4))
        valid = [(i, v) for i, v in enumerate(macd_line) if v is not None]
        signal_line = [None] * n
        histogram = [None] * n
        if len(valid) >= signal:
            vals = [v for _, v in valid]
            k = 2.0 / (signal + 1)
            sig = float(np.mean(vals[:signal]))
            start_idx = valid[signal - 1][0]
            signal_line[start_idx] = round(sig, 4)
            histogram[start_idx] = round(macd_line[start_idx] - sig, 4) if macd_line[start_idx] else None
            for j in range(signal, len(valid)):
                idx = valid[j][0]
                sig = vals[j] * k + sig * (1 - k)
                signal_line[idx] = round(sig, 4)
                histogram[idx] = round(macd_line[idx] - sig, 4)
        return {"line": macd_line, "signal": signal_line, "hist": histogram}

    def vwap(self) -> list:
        n = len(self.closes)
        if not np.any(self.volumes):
            return [None] * n
        result = []
        cum_pv = 0.0
        cum_v = 0.0
        for i in range(n):
            typical = (self.highs[i] + self.lows[i] + self.closes[i]) / 3
            cum_pv += typical * self.volumes[i]
            cum_v += self.volumes[i]
            result.append(round(cum_pv / cum_v, 4) if cum_v > 0 else None)
        return result

    def atr(self, period: int = 14) -> list:
        n = len(self.closes)
        if n < 2:
            return [None] * n
        tr_list = [None]
        for i in range(1, n):
            hl = self.highs[i] - self.lows[i]
            hc = abs(self.highs[i] - self.closes[i - 1])
            lc = abs(self.lows[i] - self.closes[i - 1])
            tr_list.append(float(max(hl, hc, lc)))
        result = [None] * period
        valid_tr = [v for v in tr_list if v is not None]
        if len(valid_tr) < period:
            return [None] * n
        atr_val = float(np.mean(valid_tr[:period]))
        result.append(round(atr_val, 4))
        for i in range(period, len(valid_tr)):
            atr_val = (atr_val * (period - 1) + valid_tr[i]) / period
            result.append(round(atr_val, 4))
        return result

    def stochastic(self, k_period: int = 14, d_period: int = 3) -> dict:
        n = len(self.closes)
        k_line = []
        for i in range(n):
            if i < k_period - 1:
                k_line.append(None)
            else:
                low_min = float(np.min(self.lows[i - k_period + 1:i + 1]))
                high_max = float(np.max(self.highs[i - k_period + 1:i + 1]))
                denom = high_max - low_min
                if denom == 0:
                    k_line.append(50.0)
                else:
                    k_line.append(round((self.closes[i] - low_min) / denom * 100, 2))
        d_line = [None] * n
        valid_k = [(i, v) for i, v in enumerate(k_line) if v is not None]
        for j in range(d_period - 1, len(valid_k)):
            idx = valid_k[j][0]
            vals = [valid_k[j - x][1] for x in range(d_period)]
            d_line[idx] = round(float(np.mean(vals)), 2)
        return {"k": k_line, "d": d_line}

    def compute_all(self) -> dict:
        return {
            "sma20":  self.sma(20),
            "sma50":  self.sma(50),
            "sma200": self.sma(200),
            "ema9":   self.ema(9),
            "ema21":  self.ema(21),
            "bb":     self.bollinger_bands(20, 2.0),
            "rsi":    self.rsi(14),
            "macd":   self.macd(12, 26, 9),
            "vwap":   self.vwap(),
            "atr":    self.atr(14),
            "stoch":  self.stochastic(14, 3),
        }
