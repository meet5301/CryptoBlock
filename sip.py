from flask import Blueprint, render_template, request, redirect, url_for, session
from bson import ObjectId
from datetime import datetime

sip_bp = Blueprint("sip", __name__)

def init_sip(app, users_col, sip_col, trades_col, COINS):

    # ================= SIP PAGE =================
    @sip_bp.route("/sip")
    def sip_home():
        if "user" not in session:
            return redirect(url_for("login"))

        user = users_col.find_one({"email": session["user"]})
        sip_list = list(sip_col.find({"email": session["user"]}))

        return render_template(
            "investment.html",
            wallet=user["wallet"],
            coins=COINS,
            sip_list=sip_list,
            user=session["user"]
        )

    # ================= SAVE SIP =================
    @sip_bp.route("/save-sip", methods=["POST"])
    def save_sip():
        if "user" not in session:
            return redirect(url_for("login"))

        coin = request.form.get("coin")
        amount = int(request.form.get("amount", 0))
        months = int(request.form.get("months", 1))

        user = users_col.find_one({"email": session["user"]})
        wallet = user["wallet"]

        total = amount * months

        # 💰 balance check
        if wallet["cash"] < total:
            return redirect(url_for("sip.sip_home"))

        # 💸 cash minus only
        wallet["cash"] -= total

        users_col.update_one(
            {"email": session["user"]},
            {"$set": {"wallet": wallet}}
        )

        sip_col.insert_one({
            "email": session["user"],
            "coin": coin,
            "amount": amount,
            "months": months,
            "total": total,
            "created_at": datetime.now()
        })

        return redirect(url_for("sip.sip_home"))

    # ================= CANCEL SIP =================
    @sip_bp.route("/cancel-sip/<sip_id>", methods=["POST"])
    def cancel_sip(sip_id):
        if "user" not in session:
            return redirect(url_for("login"))

        sip = sip_col.find_one({"_id": ObjectId(sip_id)})

        if not sip:
            return redirect(url_for("sip.sip_home"))

        user = users_col.find_one({"email": session["user"]})
        wallet = user["wallet"]

        # 💰 refund full amount
        wallet["cash"] += sip["total"]

        users_col.update_one(
            {"email": session["user"]},
            {"$set": {"wallet": wallet}}
        )

        sip_col.delete_one({"_id": ObjectId(sip_id)})

        return redirect(url_for("sip.sip_home"))

    # REGISTER BLUEPRINT
    app.register_blueprint(sip_bp)
