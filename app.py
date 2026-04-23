import random
import threading
import time
from datetime import datetime

from bson import ObjectId
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from config import SECRET_KEY
from core.blockchain_instance import blockchain
from core.mempool import mempool
from database.mongo import get_db

from api.routes.auth import auth_bp
from api.routes.blockchain import blockchain_bp
from api.routes.ai_monitor import ai_bp
from api.routes.wallet import wallet_bp
from api.routes.transaction import transaction_bp
from api.routes.admin import admin_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY

app.register_blueprint(auth_bp)
app.register_blueprint(blockchain_bp, url_prefix="/blockchain")
app.register_blueprint(ai_bp, url_prefix="/ai")
app.register_blueprint(wallet_bp, url_prefix="/wallet")
app.register_blueprint(transaction_bp, url_prefix="/transaction")
app.register_blueprint(admin_bp, url_prefix="/admin")

# ─── COINS ────────────────────────────────────────────────────────────────────
COINS = {
    "ALP": "AlphaCoin", "VEC": "VectorCoin", "ORB": "OrbitCoin",
    "NVA": "NovaCoin",  "PLS": "PulseCoin",  "ZYN": "ZynexCoin",
    "QNT": "Quantia",   "FLX": "Fluxon",     "CRX": "Corex",
    "AXN": "Axion",     "LUM": "Lumina",     "PRM": "Prisma",
}


# ─── HELPERS ──────────────────────────────────────────────────────────────────
def _blockchain_stats():
    db = get_db()
    mined = list(db.transactions.find({"status": "Mined"}))
    avg_risk = 0.0
    if mined:
        from ai.detector import detect_anomalies
        analyzed = detect_anomalies([{**tx, "_id": str(tx["_id"])} for tx in mined])
        scores = [t.get("risk_score") or 0 for t in analyzed]
        avg_risk = round(sum(scores) / len(scores), 1) if scores else 0.0
    return {
        "total_blocks": len(blockchain.chain),
        "chain_valid": blockchain.is_chain_valid(),
        "pending_count": db.transactions.count_documents({"status": "Pending"}),
        "avg_risk": avg_risk,
    }


def _record_blockchain_tx(sender_addr, receiver_addr, amount, coin=None, tx_type="TRADE"):
    db = get_db()
    tx_doc = {
        "sender": sender_addr,
        "receiver": receiver_addr,
        "amount": amount,
        "coin": coin,
        "type": tx_type,
        "status": "Pending",
        "timestamp": datetime.now(),
    }
    db.transactions.insert_one(tx_doc)
    mempool.add_transaction({**tx_doc, "_id": str(tx_doc.get("_id", ""))})


# ─── ROOT ─────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return redirect(url_for("home"))


# ─── HOME ─────────────────────────────────────────────────────────────────────
@app.route("/home")
def home():
    prices = {c: random.randint(2000, 5000) for c in COINS}
    bc_stats = _blockchain_stats()
    return render_template("home.html", coins=COINS, prices=prices,
                           user=session.get("user"), bc_stats=bc_stats)


# ─── PORTFOLIO ────────────────────────────────────────────────────────────────
@app.route("/portfolio")
def portfolio():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    user = db.users.find_one({"email": session["user"]})
    wallet = user["wallet"]

    running_trades = []
    for t in db.trades.find({"email": session["user"], "status": "OPEN"}):
        live_price = random.randint(2000, 5000)
        running_trades.append({
            "coin": t["coin"], "qty": t["qty"],
            "pnl": round((live_price - t["buy_price"]) * t["qty"], 2),
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
        total_invested = sip["total_invested"]
        units = sip["units"]
        current_value = units * random.randint(2000, 5000)
        sip_returns.append({
            "coin": sip["coin"], "invested": round(total_invested, 2),
            "current": round(current_value, 2),
            "pnl": round(current_value - total_invested, 2),
            "progress": f"{sip['executed_months']}/{sip['months']}",
            "status": sip["status"],
        })

    return render_template("portfolio.html", user=session["user"], wallet=wallet,
                           running_trades=running_trades, trade_history=trade_history,
                           total_profit=round(total_profit, 2), total_loss=round(total_loss, 2),
                           active_sips=active_sips, closed_sips=closed_sips, sip_returns=sip_returns)


# ─── WALLET ───────────────────────────────────────────────────────────────────
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
    sent = list(db.transfers.find({"sender": email}).sort("created_at", -1))
    received = list(db.transfers.find({"receiver": email}).sort("created_at", -1))
    return render_template("profile.html", user=email, user_data=user_data,
                           wallet=user_data["wallet"], sent_history=sent, receive_history=received)


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


# ─── TRADE API ────────────────────────────────────────────────────────────────
@app.route("/api/trade", methods=["POST"])
def api_trade():
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401
    db = get_db()
    data = request.json or {}
    coin = data.get("coin")
    action = data.get("action")
    qty = int(data.get("qty", 1))
    stoploss = float(data.get("stoploss", 0))
    user = db.users.find_one({"email": session["user"]})
    sender_addr = user["wallet"].get("wallet_address", "")

    if action == "BUY":
        price = float(data.get("price", 0))
        cost = price * qty
        if user["wallet"]["cash"] < cost:
            return jsonify({"error": "Insufficient balance"}), 400
        db.users.update_one({"email": session["user"]},
                            {"$inc": {"wallet.cash": -cost, f"wallet.coins.{coin}": qty}})
        trade_id = db.trades.insert_one({
            "email": session["user"], "coin": coin, "buy_price": price,
            "qty": qty, "stoploss": stoploss, "status": "OPEN", "created_at": datetime.now(),
        }).inserted_id
        db.profit_loss.insert_one({
            "email": session["user"], "coin": coin, "trade_id": trade_id,
            "amount": 0, "status": "OPEN", "created_at": datetime.now(),
        })
        _record_blockchain_tx(sender_addr, "MARKET", cost, coin, "TRADE")
        return jsonify({"success": True})

    trade = db.trades.find_one({"email": session["user"], "coin": coin, "status": "OPEN"})
    if not trade:
        return jsonify({"error": "No open trade"}), 400
    movement = random.uniform(-0.15, 0.15)
    sell_price = round(trade["buy_price"] * (1 + movement), 2)
    pnl = (sell_price - trade["buy_price"]) * trade["qty"]
    db.users.update_one({"email": session["user"]},
                        {"$inc": {f"wallet.coins.{coin}": -trade["qty"],
                                  "wallet.cash": sell_price * trade["qty"]}})
    db.trades.update_one({"_id": trade["_id"]},
                         {"$set": {"status": "CLOSED", "sell_price": sell_price, "closed_at": datetime.now()}})
    db.profit_loss.update_one({"trade_id": trade["_id"]},
                              {"$set": {"amount": round(pnl, 2), "status": "CLOSED"}})
    _record_blockchain_tx("MARKET", sender_addr, sell_price * trade["qty"], coin, "TRADE")
    return jsonify({"success": True, "pnl": round(pnl, 2)})


# ─── WALLET API ───────────────────────────────────────────────────────────────
@app.route("/api/wallet")
def api_wallet():
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401
    db = get_db()
    user = db.users.find_one({"email": session["user"]})
    return jsonify({"cash": user["wallet"]["cash"]})


# ─── SEND CRYPTO (CASH TRANSFER) ──────────────────────────────────────────────
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
                movement = random.uniform(-0.15, 0.05)
                current_price = round(t["buy_price"] * (1 + movement), 2)
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
        except Exception:
            pass
        time.sleep(5)


def _sip_executor():
    while True:
        time.sleep(10)
        try:
            db = get_db()
            now = datetime.now()
            for sip in db.sip.find({"status": "ACTIVE"}):
                executed = sip.get("executed_months", 0)
                if executed >= sip.get("months", 0):
                    db.sip.update_one({"_id": sip["_id"]}, {"$set": {"status": "COMPLETED"}})
                    continue
                last = sip.get("last_executed_at")
                if last and (now - last).total_seconds() < 10:
                    continue
                user = db.users.find_one({"email": sip["email"]})
                if not user or user["wallet"]["cash"] < sip["amount"]:
                    continue
                price = round(random.randint(2000, 5000) * random.uniform(0.8, 1.2), 2)
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
        except Exception:
            pass


# ─── ENTRY ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    threading.Thread(target=_stoploss_watcher, daemon=True).start()
    threading.Thread(target=_sip_executor, daemon=True).start()
    app.run(debug=True)
