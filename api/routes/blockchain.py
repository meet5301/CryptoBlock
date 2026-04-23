from flask import Blueprint, jsonify, redirect, render_template, session, url_for
from core.blockchain_instance import blockchain
from core.mempool import mempool
from database.models.block_schema import create_block_doc
from database.mongo import get_db

blockchain_bp = Blueprint("blockchain", __name__, url_prefix="/blockchain")


@blockchain_bp.route("/mine")
def mine_block():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    pending = list(db.transactions.find({"status": "Pending"}))
    if not pending:
        return render_template("blockchain.html",
                               chain=blockchain.chain,
                               message="No pending transactions to mine.",
                               stats=_stats(db))
    clean = [{**{k: str(v) if k == "_id" else v for k, v in tx.items()}} for tx in pending]
    new_block = blockchain.add_block(clean)
    db.blocks.insert_one(create_block_doc(new_block))
    db.transactions.update_many({"status": "Pending"}, {"$set": {"status": "Mined"}})
    mempool.clear()
    return render_template("blockchain.html",
                           chain=blockchain.chain,
                           message=f"Block #{new_block.index} mined successfully!",
                           stats=_stats(db))


@blockchain_bp.route("/view")
def view_chain():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    return render_template("blockchain.html", chain=blockchain.chain, message=None, stats=_stats(db))


@blockchain_bp.route("/stats")
def chain_stats():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    return jsonify(_stats(db))


def _stats(db):
    return {
        "total_blocks": len(blockchain.chain),
        "total_mined": db.transactions.count_documents({"status": "Mined"}),
        "pending_count": db.transactions.count_documents({"status": "Pending"}),
        "chain_valid": blockchain.is_chain_valid(),
        "difficulty": blockchain.difficulty,
    }
