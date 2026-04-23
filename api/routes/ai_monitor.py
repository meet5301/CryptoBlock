from flask import Blueprint, redirect, render_template, session, url_for
from ai.detector import detect_anomalies
from database.mongo import get_db

ai_bp = Blueprint("ai", __name__, url_prefix="/ai")


@ai_bp.route("/monitor")
def monitor():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    transactions = list(db.transactions.find({"status": "Mined"}))
    for tx in transactions:
        tx["_id"] = str(tx["_id"])

    analyzed = detect_anomalies(transactions)
    total = len(analyzed)
    suspicious = sum(1 for tx in analyzed if tx.get("ai_status") == "Suspicious")
    high_risk = sum(1 for tx in analyzed if (tx.get("risk_score") or 0) > 60)
    avg_risk = round(sum((tx.get("risk_score") or 0) for tx in analyzed) / total, 1) if total else 0.0

    summary = {"total": total, "suspicious": suspicious, "high_risk": high_risk, "avg_risk": avg_risk}
    return render_template("ai_monitor.html", transactions=analyzed, summary=summary)
