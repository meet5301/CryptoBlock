import json
import time

import requests
from flask import Blueprint, jsonify, request

from core.indicator_engine import IndicatorEngine
from price_engine import get_price, COINGECKO_IDS

charts_bp = Blueprint("charts", __name__)

USD_TO_INR = 83.5

INTERVAL_TTL = {"15m": 60, "1h": 60, "4h": 300, "1d": 300, "1w": 3600}
INTERVAL_DAYS = {"15m": 2, "1h": 2, "4h": 7, "1d": 30, "1w": 365}

COINS_META = {
    "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin",
    "SOL": "solana", "XRP": "ripple", "DOGE": "dogecoin",
    "ADA": "cardano", "TRX": "tron", "MATIC": "matic-network",
    "LTC": "litecoin", "AVAX": "avalanche-2", "LINK": "chainlink"
}


def _get_redis():
    try:
        from database.cache.redis_client import get_redis_client
        return get_redis_client()
    except Exception:
        return None


def _cache_get(key):
    r = _get_redis()
    if not r:
        return None
    try:
        val = r.get(key)
        return json.loads(val) if val else None
    except Exception:
        return None


def _cache_set(key, data, ttl):
    r = _get_redis()
    if not r:
        return
    try:
        r.setex(key, ttl, json.dumps(data))
    except Exception:
        pass


def _fetch_ohlc(symbol: str, interval: str) -> list:
    cg_id = COINS_META.get(symbol.upper())
    if not cg_id:
        return []

    days = INTERVAL_DAYS.get(interval, 30)

    # 15m and 1h — use market_chart with hourly interval
    if interval in ("15m", "1h"):
        try:
            r = requests.get(
                f"https://api.coingecko.com/api/v3/coins/{cg_id}/market_chart",
                params={"vs_currency": "usd", "days": days, "interval": "hourly"},
                timeout=10,
                headers={"Accept": "application/json"}
            )
            data = r.json()
            prices = data.get("prices", [])
            candles = []
            for i in range(1, len(prices)):
                t = prices[i][0]
                o = round(prices[i - 1][1] * USD_TO_INR, 2)
                c = round(prices[i][1] * USD_TO_INR, 2)
                h = round(max(o, c) * 1.002, 2)
                l = round(min(o, c) * 0.998, 2)
                candles.append({"t": t, "o": o, "h": h, "l": l, "c": c})
            return candles
        except Exception as e:
            print(f"[Charts] market_chart fetch failed: {e}")
            return []

    # 4h, 1d, 1w — use OHLC endpoint
    try:
        r = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{cg_id}/ohlc",
            params={"vs_currency": "usd", "days": days},
            timeout=10,
            headers={"Accept": "application/json"}
        )
        raw = r.json()
        if not isinstance(raw, list):
            return []
        candles = []
        for row in raw:
            if len(row) < 5:
                continue
            candles.append({
                "t": row[0],
                "o": round(row[1] * USD_TO_INR, 2),
                "h": round(row[2] * USD_TO_INR, 2),
                "l": round(row[3] * USD_TO_INR, 2),
                "c": round(row[4] * USD_TO_INR, 2),
            })
        return candles
    except Exception as e:
        print(f"[Charts] OHLC fetch failed: {e}")
        return []


def _get_candles_cached(symbol: str, interval: str) -> tuple[list, bool]:
    key = f"ohlc:{symbol}:{interval}"
    cached = _cache_get(key)
    if cached:
        return cached, True
    candles = _fetch_ohlc(symbol, interval)
    if candles:
        _cache_set(key, candles, INTERVAL_TTL.get(interval, 300))
    return candles, False


# ── ENDPOINT A: OHLC ─────────────────────────────────────────────────────────
@charts_bp.route("/ohlc/<symbol>")
def ohlc(symbol):
    interval = request.args.get("interval", "1d")
    symbol = symbol.upper()

    candles, from_cache = _get_candles_cached(symbol, interval)

    if not candles:
        return jsonify({
            "error": "Data unavailable",
            "candles": [],
            "coin": symbol,
            "cached": False
        }), 503

    return jsonify({
        "coin": symbol,
        "interval": interval,
        "candles": candles,
        "count": len(candles),
        "cached": from_cache,
    })


# ── ENDPOINT B: INDICATORS ────────────────────────────────────────────────────
@charts_bp.route("/indicators/<symbol>")
def indicators(symbol):
    interval = request.args.get("interval", "1d")
    symbol = symbol.upper()

    cache_key = f"indicators:{symbol}:{interval}"
    cached = _cache_get(cache_key)
    if cached:
        return jsonify(cached)

    candles, _ = _get_candles_cached(symbol, interval)
    if not candles:
        return jsonify({"error": "No OHLC data available"}), 503

    engine = IndicatorEngine(candles)
    result = engine.compute_all()
    result["symbol"] = symbol
    result["interval"] = interval
    result["candle_count"] = len(candles)

    _cache_set(cache_key, result, INTERVAL_TTL.get(interval, 300))
    return jsonify(result)


# ── ENDPOINT C: SIGNALS ───────────────────────────────────────────────────────
@charts_bp.route("/signals/<symbol>")
def signals(symbol):
    interval = request.args.get("interval", "1d")
    symbol = symbol.upper()

    candles, _ = _get_candles_cached(symbol, interval)
    if not candles:
        return jsonify({"error": "No data"}), 503

    engine = IndicatorEngine(candles)
    ind = engine.compute_all()
    current_price = get_price(symbol) or (candles[-1]["c"] if candles else 0)

    sigs = {}
    score = 0
    total_weight = 0

    # RSI signal
    rsi_vals = [v for v in ind["rsi"] if v is not None]
    if rsi_vals:
        rsi_val = rsi_vals[-1]
        if rsi_val < 30:
            rsi_sig = "OVERSOLD"
            score += 20
        elif rsi_val > 70:
            rsi_sig = "OVERBOUGHT"
            score -= 20
        else:
            rsi_sig = "NEUTRAL"
        sigs["rsi"] = {"value": round(rsi_val, 2), "signal": rsi_sig}
        total_weight += 20

    # MACD signal
    hist = [v for v in ind["macd"]["hist"] if v is not None]
    if len(hist) >= 2:
        if hist[-1] > 0 and hist[-2] <= 0:
            macd_sig = "BULLISH"
            score += 25
        elif hist[-1] < 0 and hist[-2] >= 0:
            macd_sig = "BEARISH"
            score -= 25
        elif hist[-1] > 0:
            macd_sig = "BULLISH"
            score += 10
        else:
            macd_sig = "BEARISH"
            score -= 10
        sigs["macd"] = {"value": round(hist[-1], 4), "signal": macd_sig}
        total_weight += 25

    # Bollinger Bands signal
    bb_upper = [v for v in ind["bb"]["upper"] if v is not None]
    bb_lower = [v for v in ind["bb"]["lower"] if v is not None]
    bb_mid   = [v for v in ind["bb"]["mid"] if v is not None]
    if bb_upper and bb_lower and bb_mid:
        u, l, m = bb_upper[-1], bb_lower[-1], bb_mid[-1]
        bw = (u - l) / m * 100 if m else 0
        if bw < 2:
            bb_sig = "SQUEEZE"
        elif current_price > u:
            bb_sig = "BREAKOUT_UP"
            score += 15
        elif current_price < l:
            bb_sig = "BREAKOUT_DOWN"
            score -= 15
        else:
            bb_sig = "NORMAL"
        sigs["bb"] = {"bandwidth": round(bw, 2), "signal": bb_sig}
        total_weight += 15

    # MA trend signal
    sma50  = [v for v in ind["sma50"] if v is not None]
    sma200 = [v for v in ind["sma200"] if v is not None]
    if sma50 and sma200:
        s50, s200 = sma50[-1], sma200[-1]
        if current_price > s50 > s200:
            ma_sig = "UPTREND"
            score += 20
        elif current_price < s50 < s200:
            ma_sig = "DOWNTREND"
            score -= 20
        else:
            ma_sig = "MIXED"
        sigs["ma"] = {"sma50": round(s50, 2), "sma200": round(s200, 2), "signal": ma_sig}
        total_weight += 20

    # Stochastic signal
    stoch_k = [v for v in ind["stoch"]["k"] if v is not None]
    stoch_d = [v for v in ind["stoch"]["d"] if v is not None]
    if stoch_k and stoch_d:
        k, d = stoch_k[-1], stoch_d[-1]
        if k < 20 and d < 20:
            st_sig = "OVERSOLD"
            score += 10
        elif k > 80 and d > 80:
            st_sig = "OVERBOUGHT"
            score -= 10
        else:
            st_sig = "NEUTRAL"
        sigs["stoch"] = {"k": round(k, 2), "d": round(d, 2), "signal": st_sig}
        total_weight += 10

    # Normalize score to 0-100
    if total_weight > 0:
        strength = int(min(100, max(0, (score + total_weight) / (2 * total_weight) * 100)))
    else:
        strength = 50

    if strength >= 60:
        overall = "BUY"
    elif strength <= 40:
        overall = "SELL"
    else:
        overall = "NEUTRAL"

    return jsonify({
        "symbol": symbol,
        "price": current_price,
        "signals": sigs,
        "overall": overall,
        "strength": strength,
    })


# ── ENDPOINT D: ORDER BOOK ────────────────────────────────────────────────────
@charts_bp.route("/orderbook/<symbol>")
def orderbook(symbol):
    symbol = symbol.upper()
    current_price = get_price(symbol) or 0

    try:
        from database.mongo import get_db
        db = get_db()
        pending = list(db.orders.find({
            "coin": symbol,
            "status": "PENDING"
        }))
    except Exception:
        pending = []

    bids = {}
    asks = {}

    for order in pending:
        price_level = round(float(order.get("target_price", current_price)), 2)
        qty = float(order.get("qty", 0))
        if order.get("action") == "BUY":
            bids[price_level] = bids.get(price_level, 0) + qty
        else:
            asks[price_level] = asks.get(price_level, 0) + qty

    # If no real orders, simulate around current price
    if not bids and current_price:
        import random
        for i in range(1, 11):
            p = round(current_price * (1 - i * 0.001), 2)
            bids[p] = round(random.uniform(0.01, 2.0), 4)
    if not asks and current_price:
        import random
        for i in range(1, 11):
            p = round(current_price * (1 + i * 0.001), 2)
            asks[p] = round(random.uniform(0.01, 2.0), 4)

    bid_list = sorted(
        [{"price": p, "qty": round(q, 4), "total": round(p * q, 2)} for p, q in bids.items()],
        key=lambda x: x["price"], reverse=True
    )[:10]

    ask_list = sorted(
        [{"price": p, "qty": round(q, 4), "total": round(p * q, 2)} for p, q in asks.items()],
        key=lambda x: x["price"]
    )[:10]

    spread = round(ask_list[0]["price"] - bid_list[0]["price"], 2) if ask_list and bid_list else 0

    return jsonify({
        "symbol": symbol,
        "price": current_price,
        "bids": bid_list,
        "asks": ask_list,
        "spread": spread,
    })
