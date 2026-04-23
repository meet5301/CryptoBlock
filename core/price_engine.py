import random
import threading
import time
from collections import deque

COINS = {
    "ALP": {"base": 3200, "volatility": 0.03, "trend": 0.001},
    "VEC": {"base": 2800, "volatility": 0.04, "trend": -0.0005},
    "ORB": {"base": 4100, "volatility": 0.025, "trend": 0.002},
    "NVA": {"base": 2200, "volatility": 0.05, "trend": 0.0},
    "PLS": {"base": 3700, "volatility": 0.035, "trend": 0.001},
    "ZYN": {"base": 2600, "volatility": 0.045, "trend": -0.001},
    "QNT": {"base": 4800, "volatility": 0.02, "trend": 0.003},
    "FLX": {"base": 3100, "volatility": 0.038, "trend": 0.0},
    "CRX": {"base": 2900, "volatility": 0.042, "trend": -0.002},
    "AXN": {"base": 3500, "volatility": 0.03, "trend": 0.001},
    "LUM": {"base": 4200, "volatility": 0.022, "trend": 0.002},
    "PRM": {"base": 3900, "volatility": 0.033, "trend": -0.0005},
}

MAX_HISTORY = 100


class PriceEngine:
    def __init__(self):
        self.prices = {c: float(COINS[c]["base"]) for c in COINS}
        self.history = {c: deque([float(COINS[c]["base"])] * 10, maxlen=MAX_HISTORY) for c in COINS}
        self.open_24h = {c: float(COINS[c]["base"]) for c in COINS}
        self._lock = threading.Lock()
        self._running = False

    def _update(self):
        with self._lock:
            for coin, cfg in COINS.items():
                noise = random.gauss(0, 1)
                change = cfg["trend"] + cfg["volatility"] * noise * 0.1
                new_price = round(self.prices[coin] * (1 + change), 2)
                new_price = max(100.0, new_price)
                self.prices[coin] = new_price
                self.history[coin].append(new_price)

    def start(self):
        if self._running:
            return
        self._running = True

        def _loop():
            while self._running:
                self._update()
                time.sleep(3)

        threading.Thread(target=_loop, daemon=True).start()

    def get_price(self, coin):
        with self._lock:
            return self.prices.get(coin, 0.0)

    def get_all_prices(self):
        with self._lock:
            return dict(self.prices)

    def get_sparkline(self, coin, n=10):
        with self._lock:
            hist = list(self.history[coin])
            return hist[-n:]

    def get_change_24h(self, coin):
        with self._lock:
            current = self.prices[coin]
            open_p = self.open_24h[coin]
            if open_p == 0:
                return 0.0
            return round((current - open_p) / open_p * 100, 2)

    def get_snapshot(self):
        with self._lock:
            result = {}
            for coin in COINS:
                current = self.prices[coin]
                open_p = self.open_24h[coin]
                change = round((current - open_p) / open_p * 100, 2) if open_p else 0.0
                result[coin] = {
                    "price": current,
                    "change_24h": change,
                    "sparkline": list(self.history[coin])[-10:],
                }
            return result


price_engine = PriceEngine()
