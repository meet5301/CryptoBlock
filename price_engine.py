import requests
import threading
import time
from collections import deque

COINGECKO_IDS = {
    "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin",
    "SOL": "solana", "XRP": "ripple", "DOGE": "dogecoin",
    "ADA": "cardano", "TRX": "tron", "MATIC": "matic-network",
    "LTC": "litecoin", "AVAX": "avalanche-2", "LINK": "chainlink"
}

# Fallback prices (USD) in case API is down
_FALLBACK_USD = {
    "BTC": 97000, "ETH": 3200, "BNB": 580, "SOL": 145,
    "XRP": 0.52, "DOGE": 0.12, "ADA": 0.38, "TRX": 0.11,
    "MATIC": 0.55, "LTC": 85, "AVAX": 28, "LINK": 13
}

USD_TO_INR = 83.5

_cache = {}
_history = {s: deque(maxlen=30) for s in COINGECKO_IDS}


def _init_fallback():
    for symbol, usd in _FALLBACK_USD.items():
        inr = round(usd * USD_TO_INR, 2)
        _cache[symbol] = {"inr": inr, "change_24h": 0.0}
        _history[symbol].append(inr)


def fetch_prices():
    ids = ",".join(COINGECKO_IDS.values())
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": ids,
                "vs_currencies": "usd",
                "include_24hr_change": "true"
            },
            timeout=10,
            headers={"Accept": "application/json"}
        )
        data = r.json()

        if not isinstance(data, dict):
            print(f"[PriceEngine] Unexpected response: {data}")
            return

        updated = 0
        for symbol, cg_id in COINGECKO_IDS.items():
            if cg_id in data and "usd" in data[cg_id]:
                usd_price = data[cg_id]["usd"]
                inr_price = round(usd_price * USD_TO_INR, 2)
                change = round(data[cg_id].get("usd_24h_change", 0.0), 2)
                _cache[symbol] = {"inr": inr_price, "change_24h": change}
                _history[symbol].append(inr_price)
                updated += 1

        print(f"[PriceEngine] Updated {updated} prices")

    except Exception as e:
        print(f"[PriceEngine] Fetch failed: {e} — using cached/fallback prices")


def get_price(symbol):
    return _cache.get(symbol, {}).get("inr", 0)


def get_all_prices():
    return _cache


def get_history(symbol):
    return list(_history.get(symbol, []))


# For order_executor compatibility (it calls price_engine.get_all_prices())
def get_snapshot():
    return _cache


def _updater():
    while True:
        time.sleep(60)
        fetch_prices()


def start():
    _init_fallback()
    fetch_prices()
    threading.Thread(target=_updater, daemon=True).start()
    print("[PriceEngine] Started — real CoinGecko prices active")
