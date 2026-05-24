import threading
import time
from datetime import datetime

from bson import ObjectId
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO, join_room, emit

from config import SECRET_KEY
from core.blockchain_instance import blockchain
from core.mempool import mempool
from price_engine import start as start_price_engine, get_price, get_all_prices, get_history, set_socketio
from database.mongo import get_db

from api.routes.auth import auth_bp
from api.routes.blockchain import blockchain_bp
from api.routes.ai_monitor import ai_bp
from api.routes.wallet import wallet_bp
from api.routes.transaction import transaction_bp
from api.routes.admin import admin_bp
from api.routes.orders import orders_bp
from api.routes.leaderboard import leaderboard_bp
from api.routes.notifications import notifications_bp
from api.routes.charts import charts_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

app.register_blueprint(auth_bp)
app.register_blueprint(blockchain_bp, url_prefix="/blockchain")
app.register_blueprint(ai_bp, url_prefix="/ai")
app.register_blueprint(wallet_bp, url_prefix="/wallet")
app.register_blueprint(transaction_bp, url_prefix="/transaction")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(orders_bp, url_prefix="/orders")
app.register_blueprint(leaderboard_bp, url_prefix="/leaderboard")
app.register_blueprint(notifications_bp)
app.register_blueprint(charts_bp, url_prefix="/api/charts")

COINS = {
    "BTC":  {"name": "Bitcoin",   "coingecko_id": "bitcoin"},
    "ETH":  {"name": "Ethereum",  "coingecko_id": "ethereum"},
    "BNB":  {"name": "BNB",       "coingecko_id": "binancecoin"},
    "SOL":  {"name": "Solana",    "coingecko_id": "solana"},
    "XRP":  {"name": "XRP",       "coingecko_id": "ripple"},
    "DOGE": {"name": "Dogecoin",  "coingecko_id": "dogecoin"},
    "ADA":  {"name": "Cardano",   "coingecko_id": "cardano"},
    "TRX":  {"name": "TRON",      "coingecko_id": "tron"},
    "MATIC":{"name": "Polygon",   "coingecko_id": "matic-network"},
    "LTC":  {"name": "Litecoin",  "coingecko_id": "litecoin"},
    "AVAX": {"name": "Avalanche", "coingecko_id": "avalanche-2"},
    "LINK": {"name": "Chainlink", "coingecko_id": "chainlink"},
}


# ─── HELPERS ──────────────────────────────────────────────────────────────────
def _blockchain_stats():
    db = get_db()
    return {
        "total_blocks": len(blockchain.chain),
        "chain_valid": blockchain.is_chain_valid(),
        "pending_count": db.transactions.count_documents({"status": "Pending"}),
        "avg_risk": 0.0,
    }


def _record_blockchain_tx(sender_addr, receiver_addr, amount, coin=None, tx_type="TRADE"):
    db = get_db()
    tx_doc = {
        "sender": sender_addr, "receiver": receiver_addr,
        "amount": amount, "coin": coin, "type": tx_type,
        "status": "Pending", "timestamp": datetime.now(),
    }
    db.transactions.insert_one(tx_doc)
    mempool.add_transaction({**tx_doc, "_id": str(tx_doc.get("_id", ""))})


def _notify(db, email, message, ntype="TRADE"):
    db.notifications.insert_one({
        "user_email": email, "message": message,
        "type": ntype, "read": False, "created_at": datetime.now(),
    })


# ─── SOCKETIO EVENTS ──────────────────────────────────────────────────────────
@socketio.on("connect")
def on_connect():
    pass


@socketio.on("subscribe")
def on_subscribe(data):
    symbol = data.get("symbol", "").upper()
    if symbol:
        join_room(symbol)
        price_data = get_all_prices().get(symbol, {})
        emit("price_tick", {
            "symbol": symbol,
            "price": price_data.get("usd", 0),
            "change_24h": price_data.get("change_24h", 0),
            "timestamp": int(time.time() * 1000),
        })


def _live_tick_emitter():
    """Emits price ticks every 3 seconds to all coin rooms."""
    while True:
        time.sleep(3)
        try:
            prices = get_all_prices()
            ts = int(time.time() * 1000)
            for symbol, info in prices.items():
                socketio.emit("price_tick", {
                    "symbol": symbol,
                    "price": info.get("usd", 0),
                    "change_24h": info.get("change_24h", 0),
                    "timestamp": ts,
                }, room=symbol)
        except Exception:
            pass


# ─── PRICE ENDPOINTS ──────────────────────────────────────────────────────────
@app.route("/api/prices")
def prices_json():
    return jsonify(get_all_prices())


@app.route("/api/prices/<symbol>")
def api_price_single(symbol):
    return jsonify({
        "symbol": symbol.upper(),
        "price": get_price(symbol.upper()),
        "history": get_history(symbol.upper()),
    })


# ─── ROOT ─────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return redirect(url_for("home"))


# ─── HOME ─────────────────────────────────────────────────────────────────────
@app.route("/home")
def home():
    prices = get_all_prices()
    bc_stats = _blockchain_stats()
    return render_template("home.html", coins=COINS, prices=prices,
                           user=session.get("user"), bc_stats=bc_stats)


# ─── DASHBOARD ────────────────────────────────────────────────────────────────
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    user = db.users.find_one({"email": session["user"]})
    wallet = user["wallet"]
    prices = get_all_prices()

    coins_data = []
    total_holdings = 0.0
    best_coin = worst_coin = None
    best_pnl = float("-inf")
    worst_pnl = float("inf")

    for coin, qty in wallet.get("coins", {}).items():
        if qty <= 0:
            continue
        raw = prices.get(coin, {})
        current = raw.get("usd", 0) if isinstance(raw, dict) else raw
        avg = wallet.get("avg_price", {}).get(coin, current)
        value = qty * current
        unrealized = round((current - avg) * qty, 2)
        pnl_pct = round((current - avg) / avg * 100, 2) if avg else 0
        total_holdings += value
        coins_data.append({
            "coin": coin, "qty": round(qty, 4),
            "avg_price": round(avg, 2), "current_price": round(current, 2),
            "value": round(value, 2), "unrealized_pnl": unrealized, "pnl_pct": pnl_pct,
        })
        if unrealized > best_pnl:
            best_pnl = unrealized
            best_coin = coin
        if unrealized < worst_pnl:
            worst_pnl = unrealized
            worst_coin = coin

    total_value = round(wallet.get("cash", 0) + total_holdings, 2)

    closed_trades = list(db.profit_loss.find({"email": session["user"], "status": "CLOSED"})
                         .sort("created_at", -1).limit(10))
    day_pnl = sum(t.get("amount", 0) for t in closed_trades)

    recent_trades = list(db.trades.find({"email": session["user"]})
                         .sort("created_at", -1).limit(10))
    for t in recent_trades:
        t["_id"] = str(t["_id"])
        if hasattr(t.get("created_at"), "strftime"):
            t["created_at"] = t["created_at"].strftime("%d %b %H:%M")

    bc_stats = _blockchain_stats()
    wallet_addr = wallet.get("wallet_address", "")
    user_pending = db.transactions.count_documents({
        "$or": [{"sender": wallet_addr}, {"receiver": wallet_addr}],
        "status": "Pending",
    })

    donut_labels = [d["coin"] for d in coins_data]
    donut_values = [d["value"] for d in coins_data]

    return render_template("dashboard.html",
                           user=session["user"], wallet=wallet,
                           coins_data=coins_data, total_value=total_value,
                           day_pnl=round(day_pnl, 2),
                           best_coin=best_coin, worst_coin=worst_coin,
                           recent_trades=recent_trades,
                           bc_stats=bc_stats, user_pending=user_pending,
                           wallet_addr=wallet_addr,
                           donut_labels=donut_labels, donut_values=donut_values)


# ─── PORTFOLIO ────────────────────────────────────────────────────────────────
@app.route("/portfolio")
def portfolio():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    user = db.users.find_one({"email": session["user"]})
    wallet = user["wallet"]
    prices = get_all_prices()

    running_trades = []
    for t in db.trades.find({"email": session["user"], "status": "OPEN"}):
        raw = prices.get(t["coin"], {})
        live_price = raw.get("usd", t["buy_price"]) if isinstance(raw, dict) else t["buy_price"]
        pnl = round((live_price - t["buy_price"]) * t["qty"], 2)
        running_trades.append({
            "coin": t["coin"], "qty": t["qty"],
            "buy_price": t["buy_price"], "live_price": live_price, "pnl": pnl,
        })

    trade_history = list(db.profit_loss.find({"email": session["user"], "status": "CLOSED"}))
    total_profit = sum(t["amount"] for t in trade_history if t["amount"] > 0)
    total_loss = abs(sum(t["amount"] for t in trade_history if t["amount"] < 0))

    active_sips = list(db.sip.find({"email": session["user"], "status": "ACTIVE"}))
    closed_sips = list(db.sip.find({"email": session["user"], "status": {"$in": ["CLOSED", "COMPLETED"]}}))

    sip_returns = []
    for sip in active_sips:
        if not sip.get("executed_months") or not sip.get("units", 0):
            continue
        raw = prices.get(sip["coin"], {})
        cp = raw.get("usd", 0) if isinstance(raw, dict) else raw
        current_value = sip["units"] * cp
        sip_returns.append({
            "coin": sip["coin"], "invested": round(sip["total_invested"], 2),
            "current": round(current_value, 2),
            "pnl": round(current_value - sip["total_invested"], 2),
            "progress": f"{sip['executed_months']}/{sip['months']}",
            "status": sip["status"],
        })

    return render_template("portfolio.html", user=session["user"], wallet=wallet,
                           running_trades=running_trades, trade_history=trade_history,
                           total_profit=round(total_profit, 2), total_loss=round(total_loss, 2),
                           active_sips=active_sips, closed_sips=closed_sips, sip_returns=sip_returns)


# ─── WALLET PAGE ──────────────────────────────────────────────────────────────
@app.route("/wallet_page")
def wallet_page():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    user = db.users.find_one({"email": session["user"]})
    running_trades = list(db.trades.find({"email": session["user"], "status": "OPEN"}))
    return render_template("wallet.html", wallet=user["wallet"], coins=COINS,
                           running_trades=running_trades, user=session.get("user"))


# ─── PROFILE ──────────────────────────────────────────────────────────────────
@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    email = session["user"]
    user_data = db.users.find_one({"email": email})
    
    # Get only THIS user's transfers (not other users' transfers)
    sent = list(db.transfers.find({"sender": email}).sort("created_at", -1).limit(20))
    received = list(db.transfers.find({"receiver": email}).sort("created_at", -1).limit(20))
    
    # Get THIS user's trading activity
    user_trades = list(db.trades.find({"email": email}).sort("created_at", -1).limit(20))
    user_closed_trades = list(db.profit_loss.find({"email": email, "status": "CLOSED"}).sort("created_at", -1).limit(10))
    
    # Get THIS user's notifications
    user_notifications = list(db.notifications.find({"user_email": email}).sort("created_at", -1).limit(15))
    
    return render_template("profile.html", user=email, user_data=user_data,
                           wallet=user_data["wallet"], sent_history=sent, 
                           receive_history=received, trades=user_trades,
                           closed_trades=user_closed_trades, notifications=user_notifications)


# ─── SIP PAGE ─────────────────────────────────────────────────────────────────
@app.route("/sip_page")
def sip_page():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    user = db.users.find_one({"email": session["user"]})
    sip_list = list(db.sip.find({"email": session["user"], "status": "ACTIVE"}))
    return render_template("sip_page.html", sip_list=sip_list, wallet=user["wallet"],
                           coins=COINS, user=session["user"])


# ─── TRADE API (legacy home.html chart trades) ────────────────────────────────
@app.route("/api/trade", methods=["POST"])
def api_trade():
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401
    db = get_db()
    data = request.json or {}
    coin = data.get("coin")
    action = data.get("action")
    qty = float(data.get("qty", 1))
    stoploss = float(data.get("stoploss", 0))
    user = db.users.find_one({"email": session["user"]})
    sender_addr = user["wallet"].get("wallet_address", "")
    price = get_price(coin)
    if not price:
        return jsonify({"error": "Price unavailable, try again"}), 503

    if action == "BUY":
        cost = price * qty
        if user["wallet"]["cash"] < cost:
            return jsonify({"error": "Insufficient balance"}), 400
        
        # Calculate weighted average price
        current_qty = user["wallet"].get("coins", {}).get(coin, 0)
        current_avg = user["wallet"].get("avg_price", {}).get(coin, price)
        
        if current_qty > 0:
            # Weighted average: (old_qty * old_avg + new_qty * new_price) / (old_qty + new_qty)
            new_avg = ((current_qty * current_avg) + (qty * price)) / (current_qty + qty)
        else:
            new_avg = price
        
        db.users.update_one({"email": session["user"]},
                            {"$inc": {"wallet.cash": -cost, f"wallet.coins.{coin}": qty},
                             "$set": {f"wallet.avg_price.{coin}": round(new_avg, 2)}})
        trade_id = db.trades.insert_one({
            "email": session["user"], "coin": coin, "buy_price": price,
            "qty": qty, "stoploss": stoploss, "status": "OPEN", "created_at": datetime.now(),
        }).inserted_id
        db.profit_loss.insert_one({
            "email": session["user"], "coin": coin, "trade_id": trade_id,
            "amount": 0, "status": "OPEN", "created_at": datetime.now(),
        })
        _record_blockchain_tx(sender_addr, "MARKET", cost, coin, "TRADE")
        _notify(db, session["user"], f"BUY {qty} {coin} @ ${price:.2f}", "TRADE")
        return jsonify({"success": True})

    trade = db.trades.find_one({"email": session["user"], "coin": coin, "status": "OPEN"})
    if not trade:
        return jsonify({"error": "No open trade"}), 400
    sell_price = get_price(coin)
    if not sell_price:
        return jsonify({"error": "Price unavailable"}), 503
    pnl = (sell_price - trade["buy_price"]) * trade["qty"]
    
    # Update wallet and remove coins
    user = db.users.find_one({"email": session["user"]})
    current_qty = user["wallet"].get("coins", {}).get(coin, 0)
    
    db.users.update_one({"email": session["user"]},
                        {"$inc": {f"wallet.coins.{coin}": -trade["qty"],
                                  "wallet.cash": sell_price * trade["qty"]}})
    
    # If no coins left, remove avg_price entry
    if current_qty - trade["qty"] <= 0:
        db.users.update_one({"email": session["user"]},
                            {"$unset": {f"wallet.avg_price.{coin}": ""}})
    
    db.trades.update_one({"_id": trade["_id"]},
                         {"$set": {"status": "CLOSED", "sell_price": sell_price, "closed_at": datetime.now()}})
    db.profit_loss.update_one({"trade_id": trade["_id"]},
                              {"$set": {"amount": round(pnl, 2), "status": "CLOSED"}})
    _record_blockchain_tx("MARKET", sender_addr, sell_price * trade["qty"], coin, "TRADE")
    _notify(db, session["user"], f"SELL {trade['qty']} {coin} @ ${sell_price:.2f} | PnL: ${pnl:.2f}", "TRADE")
    return jsonify({"success": True, "pnl": round(pnl, 2)})


@app.route("/api/user/activity")
def user_activity():
    """Get only THIS user's activity (trades, transfers, notifications)"""
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401
    
    db = get_db()
    email = session["user"]
    
    # Get user's recent trades
    trades = list(db.trades.find({"email": email}).sort("created_at", -1).limit(10))
    for t in trades:
        t["_id"] = str(t["_id"])
        if hasattr(t.get("created_at"), "strftime"):
            t["created_at"] = t["created_at"].strftime("%d %b %H:%M")
    
    # Get user's recent transfers (both sent and received)
    transfers = []
    sent = list(db.transfers.find({"sender": email}).sort("created_at", -1).limit(5))
    received = list(db.transfers.find({"receiver": email}).sort("created_at", -1).limit(5))
    
    for t in sent + received:
        t["_id"] = str(t["_id"])
        if hasattr(t.get("created_at"), "strftime"):
            t["created_at"] = t["created_at"].strftime("%d %b %H:%M")
    transfers = sorted(sent + received, key=lambda x: x["created_at"], reverse=True)[:5]
    
    # Get user's recent notifications
    notifications = list(db.notifications.find({"user_email": email}).sort("created_at", -1).limit(5))
    for n in notifications:
        n["_id"] = str(n["_id"])
        if hasattr(n.get("created_at"), "strftime"):
            n["created_at"] = n["created_at"].strftime("%d %b %H:%M")
    
    return jsonify({
        "user": email,
        "trades": trades,
        "transfers": transfers,
        "notifications": notifications
    })
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401
    db = get_db()
    user = db.users.find_one({"email": session["user"]})
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    wallet = user.get("wallet", {})
    prices = get_all_prices()
    
    # Calculate total holdings value
    total_coins_value = 0
    for coin, qty in wallet.get("coins", {}).items():
        if qty > 0:
            price_data = prices.get(coin, {})
            coin_price = price_data.get("usd", 0) if isinstance(price_data, dict) else price_data
            total_coins_value += qty * coin_price
    
    total_value = wallet.get("cash", 0) + total_coins_value
    
    return jsonify({
        "cash": round(wallet.get("cash", 0), 2),
        "coins_value": round(total_coins_value, 2),
        "total": round(total_value, 2),
        "email": session["user"]
    })


# ─── SEND CRYPTO ──────────────────────────────────────────────────────────────
@app.route("/send_crypto", methods=["POST"])
def send_crypto():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    sender_email = session["user"]
    receiver_email = request.form["receiver"].strip()
    rupees = float(request.form.get("rupees", 0))
    if sender_email == receiver_email:
        return "Cannot send to yourself"
    if rupees <= 0:
        return "Invalid amount"
    sender = db.users.find_one({"email": sender_email})
    receiver = db.users.find_one({"email": receiver_email})
    if not receiver:
        return "Receiver not found"
    if sender["wallet"]["cash"] < rupees:
        return "Insufficient balance"
    db.users.update_one({"email": sender_email}, {"$inc": {"wallet.cash": -rupees}})
    db.users.update_one({"email": receiver_email}, {"$inc": {"wallet.cash": rupees}})
    db.transfers.insert_one({
        "sender": sender_email, "receiver": receiver_email,
        "amount": rupees, "type": "CASH_TRANSFER", "created_at": datetime.now(),
    })
    _record_blockchain_tx(
        sender["wallet"].get("wallet_address", sender_email),
        receiver["wallet"].get("wallet_address", receiver_email),
        rupees, None, "TRANSFER",
    )
    _notify(db, sender_email, f"Sent ${rupees} to {receiver_email}", "TRADE")
    _notify(db, receiver_email, f"Received ${rupees} from {sender_email}", "TRADE")
    return redirect(url_for("profile"))


# ─── SIP ROUTES ───────────────────────────────────────────────────────────────
@app.route("/sip/start", methods=["POST"])
def start_sip():
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401
    db = get_db()
    data = request.json
    coin, amount, months = data["coin"], int(data["amount"]), int(data["months"])
    user = db.users.find_one({"email": session["user"]})
    total = amount * months
    if user["wallet"]["cash"] < total:
        return jsonify({"error": "Insufficient balance"})
    db.users.update_one({"email": session["user"]}, {"$inc": {"wallet.cash": -total}})
    sip_id = db.sip.insert_one({
        "email": session["user"], "coin": coin, "amount": amount, "months": months,
        "total": total, "total_invested": 0, "units": 0, "executed_months": 0,
        "status": "ACTIVE", "created_at": datetime.now(),
    }).inserted_id
    return jsonify({"id": str(sip_id), "coin": coin, "amount": amount,
                    "wallet_cash": user["wallet"]["cash"] - total})


@app.route("/sip/close/<sip_id>", methods=["POST"])
def close_sip(sip_id):
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401
    db = get_db()
    sip = db.sip.find_one({"_id": ObjectId(sip_id)})
    if not sip:
        return jsonify({"error": "Invalid SIP"})
    db.users.update_one({"email": session["user"]}, {"$inc": {"wallet.cash": sip["total"]}})
    db.sip.delete_one({"_id": ObjectId(sip_id)})
    user = db.users.find_one({"email": session["user"]})
    return jsonify({"wallet_cash": user["wallet"]["cash"]})


@app.route("/save-investment", methods=["POST"])
def save_investment():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    mode = request.form.get("mode")
    coin = request.form.get("coin")
    amount = int(request.form.get("amount", 0))
    months = int(request.form.get("months", 1))
    user = db.users.find_one({"email": session["user"]})
    total = amount * months if mode == "sip" else amount
    if user["wallet"]["cash"] < total:
        return redirect(url_for("sip_page"))
    db.users.update_one({"email": session["user"]}, {"$inc": {"wallet.cash": -total}})
    db.sip.insert_one({
        "email": session["user"], "mode": mode, "coin": coin, "amount": amount,
        "months": months, "total": total, "total_invested": 0, "units": 0,
        "executed_months": 0, "status": "ACTIVE", "created_at": datetime.now(),
    })
    return redirect(url_for("sip_page"))


# ─── BACKGROUND WORKERS ───────────────────────────────────────────────────────
def _stoploss_watcher():
    while True:
        try:
            db = get_db()
            for t in db.trades.find({"status": "OPEN"}):
                current_price = get_price(t["coin"])
                if not current_price:
                    continue
                if t.get("stoploss", 0) > 0 and current_price <= t["stoploss"]:
                    pnl = (current_price - t["buy_price"]) * t["qty"]
                    db.users.update_one({"email": t["email"]},
                                        {"$inc": {f"wallet.coins.{t['coin']}": -t["qty"],
                                                  "wallet.cash": current_price * t["qty"]}})
                    db.trades.update_one({"_id": t["_id"]},
                                         {"$set": {"status": "CLOSED", "sell_price": current_price,
                                                   "closed_at": datetime.now()}})
                    db.profit_loss.update_one({"trade_id": t["_id"]},
                                              {"$set": {"amount": round(pnl, 2), "status": "CLOSED"}})
                    _notify(db, t["email"],
                            f"Stop-loss triggered: {t['coin']} sold @ ${current_price:.2f}", "TRADE")
        except Exception:
            pass
        time.sleep(30)


def _sip_executor():
    while True:
        time.sleep(60)
        try:
            db = get_db()
            now = datetime.now()
            for sip in db.sip.find({"status": "ACTIVE"}):
                executed = sip.get("executed_months", 0)
                if executed >= sip.get("months", 0):
                    db.sip.update_one({"_id": sip["_id"]}, {"$set": {"status": "COMPLETED"}})
                    continue
                last = sip.get("last_executed_at")
                if last and (now - last).total_seconds() < 60:
                    continue
                user = db.users.find_one({"email": sip["email"]})
                if not user or user["wallet"]["cash"] < sip["amount"]:
                    continue
                price = get_price(sip["coin"])
                if not price:
                    continue
                qty = sip["amount"] / price
                coin = sip["coin"]
                db.users.update_one({"email": sip["email"]},
                                    {"$inc": {"wallet.cash": -sip["amount"],
                                              f"wallet.coins.{coin}": qty}})
                db.sip.update_one({"_id": sip["_id"]}, {"$set": {
                    "executed_months": executed + 1,
                    "total_invested": sip.get("total_invested", 0) + sip["amount"],
                    "units": sip.get("units", 0) + qty,
                    "last_executed_at": now,
                }})
                _notify(db, sip["email"],
                        f"SIP executed: {qty:.4f} {coin} @ ${price:.2f}", "SIP")
        except Exception:
            pass


# ─── ENTRY ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    start_price_engine()
    set_socketio(socketio)

    from core.order_executor import order_executor
    import price_engine as _pe_module
    order_executor.start(get_db, _pe_module, _record_blockchain_tx, _notify)

    threading.Thread(target=_stoploss_watcher, daemon=True).start()
    threading.Thread(target=_sip_executor, daemon=True).start()
    threading.Thread(target=_live_tick_emitter, daemon=True).start()

    socketio.run(app, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)
