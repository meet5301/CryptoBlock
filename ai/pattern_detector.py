from datetime import datetime, timedelta


def _now():
    return datetime.now()


def detect_wash_trading(db, wallet_address):
    cutoff = _now() - timedelta(seconds=60)
    txs = list(db.transactions.find({
        "$or": [{"sender": wallet_address}, {"receiver": wallet_address}],
        "timestamp": {"$gte": cutoff},
    }))
    coins_seen = {}
    for tx in txs:
        coin = tx.get("coin")
        if not coin:
            continue
        if coin not in coins_seen:
            coins_seen[coin] = {"buy": 0, "sell": 0}
        if tx.get("sender") == wallet_address:
            coins_seen[coin]["sell"] += 1
        else:
            coins_seen[coin]["buy"] += 1

    alerts = []
    for coin, counts in coins_seen.items():
        if counts["buy"] >= 2 and counts["sell"] >= 2:
            alerts.append({
                "wallet": wallet_address,
                "pattern_type": "WASH_TRADING",
                "severity": "HIGH",
                "details": f"Coin {coin}: {counts['buy']} buys + {counts['sell']} sells in 60s",
                "timestamp": _now(),
                "resolved": False,
            })
    return alerts


def detect_rapid_fire(db, wallet_address):
    cutoff = _now() - timedelta(seconds=60)
    count = db.transactions.count_documents({
        "$or": [{"sender": wallet_address}, {"receiver": wallet_address}],
        "timestamp": {"$gte": cutoff},
    })
    if count > 10:
        return [{
            "wallet": wallet_address,
            "pattern_type": "RAPID_FIRE",
            "severity": "CRITICAL",
            "details": f"{count} transactions in 60 seconds",
            "timestamp": _now(),
            "resolved": False,
        }]
    return []


def detect_whale_alert(db, tx):
    coin = tx.get("coin")
    amount = tx.get("amount", 0)
    if not coin or not amount:
        return []

    cutoff = _now() - timedelta(hours=24)
    pipeline = [
        {"$match": {"coin": coin, "timestamp": {"$gte": cutoff}}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
    ]
    result = list(db.transactions.aggregate(pipeline))
    total_volume = result[0]["total"] if result else 0

    if total_volume > 0 and (amount / total_volume) > 0.10:
        return [{
            "wallet": tx.get("sender", "unknown"),
            "pattern_type": "WHALE_ALERT",
            "severity": "HIGH",
            "details": f"{coin}: single tx ₹{amount:.0f} = {amount/total_volume*100:.1f}% of 24h volume",
            "timestamp": _now(),
            "resolved": False,
        }]
    return []


def detect_pump_and_dump(db, wallet_address, price_engine):
    cutoff = _now() - timedelta(minutes=10)
    sells = list(db.transactions.find({
        "sender": wallet_address,
        "timestamp": {"$gte": cutoff},
    }))

    alerts = []
    for tx in sells:
        coin = tx.get("coin")
        if not coin:
            continue
        sparkline = price_engine.get_sparkline(coin, 10)
        if len(sparkline) < 5:
            continue
        peak = max(sparkline)
        current = sparkline[-1]
        if peak > 0 and (peak - current) / peak > 0.08:
            alerts.append({
                "wallet": wallet_address,
                "pattern_type": "PUMP_AND_DUMP",
                "severity": "CRITICAL",
                "details": f"{coin}: price dropped {(peak-current)/peak*100:.1f}% after large sell",
                "timestamp": _now(),
                "resolved": False,
            })
    return alerts


def run_all_detectors(db, wallet_address, price_engine, recent_tx=None):
    alerts = []
    alerts += detect_wash_trading(db, wallet_address)
    alerts += detect_rapid_fire(db, wallet_address)
    alerts += detect_pump_and_dump(db, wallet_address, price_engine)
    if recent_tx:
        alerts += detect_whale_alert(db, recent_tx)

    for alert in alerts:
        existing = db.alerts.find_one({
            "wallet": alert["wallet"],
            "pattern_type": alert["pattern_type"],
            "resolved": False,
            "timestamp": {"$gte": _now() - timedelta(minutes=5)},
        })
        if not existing:
            db.alerts.insert_one(alert)

    return alerts
