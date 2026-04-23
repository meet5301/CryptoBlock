from flask import Blueprint, jsonify, redirect, session, url_for
from core.blockchain_instance import blockchain
from core.mempool import mempool
from database.mongo import get_db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/stats")
def stats():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    return jsonify({
        "total_users": db.users.count_documents({}),
        "total_transactions": db.transactions.count_documents({}),
        "total_blocks": db.blocks.count_documents({}),
        "total_trades": db.trades.count_documents({}),
        "chain_valid": blockchain.is_chain_valid(),
        "mining_difficulty": blockchain.difficulty,
        "mempool_pending": mempool.get_count(),
    })


@admin_bp.route("/reset-mempool")
def reset_mempool():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    mempool.clear()
    return jsonify({"status": "mempool cleared", "count": 0})
