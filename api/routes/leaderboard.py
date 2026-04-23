from flask import Blueprint, jsonify, render_template, session, redirect, url_for
from database.mongo import get_db

leaderboard_bp = Blueprint("leaderboard", __name__, url_prefix="/leaderboard")


def _build_leaderboard(db, price_engine):
    prices = price_engine.get_all_prices()
    users = list(db.users.find({}, {"name": 1, "email": 1, "wallet": 1}))
    rows = []

    for u in users:
        wallet = u.get("wallet", {})
        cash = wallet.get("cash", 0)
        coins = wallet.get("coins", {})
        holdings_value = sum(coins.get(c, 0) * prices.get(c, 0) for c in coins)
        total = round(cash + holdings_value, 2)

        trade_count = db.trades.count_documents({"email": u["email"]})

        best_coin = None
        best_val = 0
        for c, qty in coins.items():
            val = qty * prices.get(c, 0)
            if val > best_val:
                best_val = val
                best_coin = c

        risk_alerts = db.alerts.count_documents({"wallet": wallet.get("wallet_address", ""), "resolved": False})
        risk_score = min(100, risk_alerts * 10)

        rows.append({
            "name": u.get("name", u["email"].split("@")[0]),
            "email": u["email"],
            "portfolio_value": total,
            "best_coin": best_coin or "—",
            "trade_count": trade_count,
            "risk_score": risk_score,
        })

    rows.sort(key=lambda x: x["portfolio_value"], reverse=True)
    for i, r in enumerate(rows):
        r["rank"] = i + 1
    return rows


@leaderboard_bp.route("/")
def leaderboard():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    from core.price_engine import price_engine
    db = get_db()
    rows = _build_leaderboard(db, price_engine)
    return render_template("leaderboard.html", rows=rows,
                           current_user=session["user"], user=session["user"])


@leaderboard_bp.route("/api")
def leaderboard_api():
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401
    from core.price_engine import price_engine
    db = get_db()
    rows = _build_leaderboard(db, price_engine)
    return jsonify({"rows": rows})
