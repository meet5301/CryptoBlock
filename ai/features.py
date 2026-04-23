import math
from datetime import datetime


def extract_features(transactions):
    features = []

    for tx in transactions:
        amount = float(tx.get("amount", 0) or 0)
        raw_ts = tx.get("timestamp", 0) or 0
        if isinstance(raw_ts, datetime):
            timestamp = raw_ts.timestamp()
            hour_of_day = raw_ts.hour
        else:
            timestamp = float(raw_ts)
            try:
                hour_of_day = datetime.fromtimestamp(timestamp).hour
            except Exception:
                hour_of_day = 12

        is_round_number = 1 if amount % 100 == 0 else 0

        is_night = 1 if 0 <= hour_of_day <= 6 else 0

        try:
            amount_log = math.log(amount + 1)
        except ValueError:
            amount_log = 0

        sender_len = len(str(tx.get("sender", "") or ""))
        receiver_len = len(str(tx.get("receiver", "") or ""))

        features.append(
            [
                amount,
                timestamp,
                is_round_number,
                hour_of_day,
                is_night,
                amount_log,
                sender_len,
                receiver_len,
            ]
        )

    return features
