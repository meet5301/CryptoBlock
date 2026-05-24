import secrets
from flask import Blueprint, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from database.mongo import get_db

auth_bp = Blueprint("auth", __name__)

COINS = ["BTC", "ETH", "BNB", "SOL", "XRP", "DOGE", "ADA", "TRX", "MATIC", "LTC", "AVAX", "LINK"]


def _create_wallet():
    return {
        "cash": 10000,
        "coins": {c: 0 for c in COINS},
        "avg_price": {},
        "wallet_address": "0x" + secrets.token_hex(20),
        "balance": 0,
    }


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        db = get_db()
        user = db.users.find_one({"email": request.form["email"]})
        if not user or not check_password_hash(user["password"], request.form["password"]):
            return render_template("login.html", error="Invalid credentials")
        session["user"] = user["email"]
        return redirect(url_for("home"))
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        db = get_db()
        email = request.form["email"].strip().lower()
        if db.users.find_one({"email": email}):
            return render_template("register.html", error="Email already registered")
        db.users.insert_one({
            "name": request.form["name"],
            "email": email,
            "password": generate_password_hash(request.form["password"]),
            "wallet": _create_wallet(),
        })
        session["user"] = email
        return redirect(url_for("home"))
    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))
