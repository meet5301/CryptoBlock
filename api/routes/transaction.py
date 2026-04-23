from datetime import datetime
from flask import Blueprint, redirect, render_template, request, session, url_for
from core.mempool import mempool
from database.mongo import get_db

transaction_bp = Blueprint("transaction", __name__, url_prefix="/transaction")


@transaction_bp.route("/send", methods=["GET", "POST"])
def send_transaction():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    if request.method == "POST":
        sender = db.users.find_one({"email": session["user"]})
        receiver_addr = request.form.get("receiver", "").strip()
        amount = int(request.form.get("amount", 0) or 0)

        receiver = db.users.find_one({"wallet.wallet_address": receiver_addr})
        if not receiver:
            return render_template("transaction.html", error="Receiver wallet not found")
        if sender["wallet"]["balance"] < amount:
            return render_template("transaction.html", error="Insufficient blockchain balance")

        db.users.update_one({"email": session["user"]}, {"$inc": {"wallet.balance": -amount}})
        db.users.update_one({"_id": receiver["_id"]}, {"$inc": {"wallet.balance": amount}})

        tx_doc = {
            "sender": sender["wallet"]["wallet_address"],
            "receiver": receiver_addr,
            "amount": amount,
            "type": "TRANSFER",
            "status": "Pending",
            "timestamp": datetime.now(),
        }
        db.transactions.insert_one(tx_doc)
        mempool.add_transaction({**tx_doc, "_id": str(tx_doc.get("_id", ""))})
        return redirect(url_for("home"))
    return render_template("transaction.html", error=None)
