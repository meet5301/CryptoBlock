import threading
import time
from datetime import datetime

from bson import ObjectId


class OrderExecutor:
    def __init__(self):
        self._running = False

    def start(self, get_db, price_engine, record_tx, notify):
        if self._running:
            return
        self._running = True

        def _loop():
            while self._running:
                try:
                    import price_engine as pe
                    self._process(get_db(), pe, record_tx, notify)
                except Exception:
                    pass
                time.sleep(5)

        threading.Thread(target=_loop, daemon=True).start()

    def _process(self, db, price_engine, record_tx, notify):
        all_prices = price_engine.get_all_prices()
        prices = {k: v.get("inr", 0) if isinstance(v, dict) else v
                  for k, v in all_prices.items()}
        pending = list(db.orders.find({"status": "PENDING"}))

        for order in pending:
            coin = order["coin"]
            current = prices.get(coin, 0)
            execute = False

            if order["type"] == "LIMIT":
                if order["action"] == "BUY" and current <= order["target_price"]:
                    execute = True
                elif order["action"] == "SELL" and current >= order["target_price"]:
                    execute = True

            elif order["type"] == "STOP_LOSS":
                if current <= order["target_price"]:
                    execute = True

            if execute:
                self._execute_order(db, order, current, record_tx, notify)

    def _execute_order(self, db, order, price, record_tx, notify):
        email = order["user_email"]
        coin = order["coin"]
        qty = order["qty"]
        action = order["action"]
        cost = price * qty

        user = db.users.find_one({"email": email})
        if not user:
            return

        wallet = user["wallet"]

        if action == "BUY":
            if wallet["cash"] < cost:
                db.orders.update_one({"_id": order["_id"]},
                                     {"$set": {"status": "CANCELLED", "note": "Insufficient balance"}})
                return
            db.users.update_one({"email": email},
                                {"$inc": {"wallet.cash": -cost, f"wallet.coins.{coin}": qty}})

        elif action == "SELL":
            if wallet["coins"].get(coin, 0) < qty:
                db.orders.update_one({"_id": order["_id"]},
                                     {"$set": {"status": "CANCELLED", "note": "Insufficient coins"}})
                return
            db.users.update_one({"email": email},
                                {"$inc": {f"wallet.coins.{coin}": -qty, "wallet.cash": cost}})

        now = datetime.now()
        db.orders.update_one({"_id": order["_id"]}, {"$set": {
            "status": "EXECUTED",
            "executed_price": price,
            "executed_at": now,
        }})

        trade_id = db.trades.insert_one({
            "email": email, "coin": coin,
            "buy_price": price, "qty": qty,
            "status": "CLOSED" if action == "SELL" else "OPEN",
            "created_at": now,
        }).inserted_id

        sender_addr = wallet.get("wallet_address", email)
        record_tx(sender_addr, "MARKET", cost, coin, "TRADE")

        notify(db, email,
               f"{order['type']} {action} order executed: {qty} {coin} @ ₹{price:.2f}",
               "TRADE")


order_executor = OrderExecutor()
