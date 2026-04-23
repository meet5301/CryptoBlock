from flask import Blueprint, jsonify, redirect, render_template, session, url_for
from database.mongo import get_db

wallet_bp = Blueprint("wallet", __name__, url_prefix="/wallet")


@wallet_bp.route("/detail")
def wallet_detail():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    user = db.users.find_one({"email": session["user"]})
    if not user:
        return redirect(url_for("auth.login"))

    wallet = user.get("wallet", {})
    wallet_address = wallet.get("wallet_address", "")

    sent_txs = list(db.transactions.find({"sender": wallet_address}))
    received_txs = list(db.transactions.find({"receiver": wallet_address}))
    for tx in sent_txs + received_txs:
        tx["_id"] = str(tx["_id"])

    return render_template(
        "wallet_detail.html",
        wallet=wallet,
        sent_txs=sent_txs,
        received_txs=received_txs,
        sent_total=sum(tx.get("amount", 0) for tx in sent_txs),
        received_total=sum(tx.get("amount", 0) for tx in received_txs),
    )


@wallet_bp.route("/history")
def wallet_history():
    if "user" not in session:
        return jsonify({"transactions": []})
    db = get_db()
    user = db.users.find_one({"email": session["user"]})
    if not user:
        return jsonify({"transactions": []})
    addr = user.get("wallet", {}).get("wallet_address", "")
    history = list(
        db.transactions.find({"$or": [{"sender": addr}, {"receiver": addr}]})
        .sort("timestamp", -1).limit(10)
    )
    for tx in history:
        tx["_id"] = str(tx["_id"])
    return jsonify({"transactions": history})
