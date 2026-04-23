from datetime import datetime
from bson import ObjectId
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from database.mongo import get_db

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")


def _price_engine():
    from core.price_engine import price_engine
    return price_engine


def _notify(db, email, message, ntype="TRADE"):
    db.notifications.insert_one({
        "user_email": email, "message": message,
        "type": ntype, "read": False, "created_at": datetime.now(),
    })


@orders_bp.route("/")
def orders_page():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    pending = list(db.orders.find({"user_email": session["user"], "status": "PENDING"}).sort("created_at", -1))
    recent = list(db.orders.find({"user_email": session["user"], "status": {"$in": ["EXECUTED", "CANCELLED"]}})
                  .sort("created_at", -1).limit(10))
    for o in pending + recent:
        o["_id"] = str(o["_id"])
    user = db.users.find_one({"email": session["user"]})
    return render_template("orders.html", pending=pending, recent=recent,
                           wallet=user["wallet"], user=session["user"])


@orders_bp.route("/place", methods=["POST"])
def place_order():
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401

    db = get_db()
    data = request.json or {}
    coin = data.get("coin", "").upper()
    order_type = data.get("type", "MARKET").upper()
    action = data.get("action", "BUY").upper()
    qty = int(data.get("qty", 1))
    target_price = float(data.get("target_price", 0) or 0)

    pe = _price_engine()
    current_price = pe.get_price(coin)

    if order_type == "MARKET":
        user = db.users.find_one({"email": session["user"]})
        wallet = user["wallet"]
        cost = current_price * qty

        if action == "BUY":
            if wallet["cash"] < cost:
                return jsonify({"error": "Insufficient balance"}), 400
            db.users.update_one({"email": session["user"]},
                                {"$inc": {"wallet.cash": -cost, f"wallet.coins.{coin}": qty}})
        else:
            if wallet["coins"].get(coin, 0) < qty:
                return jsonify({"error": "Insufficient coins"}), 400
            db.users.update_one({"email": session["user"]},
                                {"$inc": {f"wallet.coins.{coin}": -qty, "wallet.cash": cost}})

        trade_id = db.trades.insert_one({
            "email": session["user"], "coin": coin,
            "buy_price": current_price, "qty": qty,
            "stoploss": 0, "status": "OPEN" if action == "BUY" else "CLOSED",
            "created_at": datetime.now(),
        }).inserted_id

        if action == "BUY":
            db.profit_loss.insert_one({
                "email": session["user"], "coin": coin, "trade_id": trade_id,
                "amount": 0, "status": "OPEN", "created_at": datetime.now(),
            })

        db.orders.insert_one({
            "user_email": session["user"], "coin": coin, "type": "MARKET",
            "action": action, "qty": qty, "target_price": current_price,
            "status": "EXECUTED", "executed_price": current_price,
            "created_at": datetime.now(), "executed_at": datetime.now(),
        })

        _notify(db, session["user"],
                f"MARKET {action}: {qty} {coin} @ ₹{current_price:.2f}", "TRADE")

        return jsonify({"success": True, "executed_price": current_price})

    else:
        if target_price <= 0:
            return jsonify({"error": "target_price required for LIMIT/STOP_LOSS"}), 400

        db.orders.insert_one({
            "user_email": session["user"], "coin": coin,
            "type": order_type, "action": action,
            "qty": qty, "target_price": target_price,
            "status": "PENDING", "created_at": datetime.now(),
        })
        return jsonify({"success": True, "message": f"{order_type} order placed"})


@orders_bp.route("/pending")
def pending_orders():
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401
    db = get_db()
    orders = list(db.orders.find({"user_email": session["user"], "status": "PENDING"})
                  .sort("created_at", -1))
    for o in orders:
        o["_id"] = str(o["_id"])
        o["created_at"] = o["created_at"].strftime("%d %b %H:%M") if hasattr(o.get("created_at"), "strftime") else str(o.get("created_at", ""))
    return jsonify({"orders": orders})


@orders_bp.route("/cancel/<order_id>", methods=["POST"])
def cancel_order(order_id):
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401
    db = get_db()
    result = db.orders.update_one(
        {"_id": ObjectId(order_id), "user_email": session["user"], "status": "PENDING"},
        {"$set": {"status": "CANCELLED"}}
    )
    if result.modified_count:
        return jsonify({"success": True})
    return jsonify({"error": "Order not found"}), 404
