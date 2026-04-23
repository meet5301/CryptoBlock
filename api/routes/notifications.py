from flask import Blueprint, jsonify, session
from database.mongo import get_db

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


@notifications_bp.route("/")
def get_notifications():
    if "user" not in session:
        return jsonify({"notifications": [], "unread": 0})
    db = get_db()
    notifs = list(db.notifications.find({"user_email": session["user"]})
                  .sort("created_at", -1).limit(10))
    for n in notifs:
        n["_id"] = str(n["_id"])
        if hasattr(n.get("created_at"), "strftime"):
            n["created_at"] = n["created_at"].strftime("%d %b %H:%M")
    unread = db.notifications.count_documents({"user_email": session["user"], "read": False})
    return jsonify({"notifications": notifs, "unread": unread})


@notifications_bp.route("/read", methods=["POST"])
def mark_read():
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401
    db = get_db()
    db.notifications.update_many(
        {"user_email": session["user"], "read": False},
        {"$set": {"read": True}}
    )
    return jsonify({"success": True})


@notifications_bp.route("/unread-count")
def unread_count():
    if "user" not in session:
        return jsonify({"count": 0})
    db = get_db()
    count = db.notifications.count_documents({"user_email": session["user"], "read": False})
    return jsonify({"count": count})
