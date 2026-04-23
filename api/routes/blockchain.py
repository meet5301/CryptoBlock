import time
from datetime import datetime
from flask import Blueprint, jsonify, redirect, render_template, session, url_for
from core.blockchain_instance import blockchain
from core.mempool import mempool
from core.validator import validate_block
from database.models.block_schema import create_block_doc
from database.mongo import get_db

blockchain_bp = Blueprint("blockchain", __name__, url_prefix="/blockchain")

FEE_RATE = 0.001  # 0.1%
TARGET_MINE_TIME = 10  # seconds
DIFFICULTY_ADJUST_INTERVAL = 10  # blocks


def _adjust_difficulty():
    chain = blockchain.chain
    n = len(chain)
    if n < DIFFICULTY_ADJUST_INTERVAL or n % DIFFICULTY_ADJUST_INTERVAL != 0:
        return
    recent = chain[-DIFFICULTY_ADJUST_INTERVAL:]
    times = [recent[i].timestamp - recent[i - 1].timestamp for i in range(1, len(recent))]
    avg_time = sum(times) / len(times) if times else TARGET_MINE_TIME
    if avg_time < TARGET_MINE_TIME * 0.5:
        blockchain.difficulty = min(6, blockchain.difficulty + 1)
    elif avg_time > TARGET_MINE_TIME * 2:
        blockchain.difficulty = max(1, blockchain.difficulty - 1)


def _collect_fees(transactions):
    total_fees = 0.0
    for tx in transactions:
        fee = round(float(tx.get("amount", 0)) * FEE_RATE, 4)
        tx["fee"] = fee
        total_fees += fee
    return round(total_fees, 4)


def _full_stats(db):
    chain = blockchain.chain
    mine_times = []
    for i in range(1, len(chain)):
        dt = chain[i].timestamp - chain[i - 1].timestamp
        mine_times.append(dt)
    avg_mine_time = round(sum(mine_times) / len(mine_times), 2) if mine_times else 0

    total_fees = sum(
        float(tx.get("fee", 0))
        for block in chain
        for tx in block.transactions
    )

    return {
        "total_blocks": len(chain),
        "chain_valid": blockchain.is_chain_valid(),
        "current_difficulty": blockchain.difficulty,
        "avg_mine_time": avg_mine_time,
        "total_fees_collected": round(total_fees, 4),
        "pending_count": db.transactions.count_documents({"status": "Pending"}),
        "total_mined": db.transactions.count_documents({"status": "Mined"}),
    }


@blockchain_bp.route("/mine")
def mine_block():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()

    user = db.users.find_one({"email": session["user"]})
    miner_address = user["wallet"].get("wallet_address", session["user"])

    pending = list(db.transactions.find({"status": "Pending"}))
    if not pending:
        return render_template("blockchain.html", chain=blockchain.chain,
                               message="No pending transactions to mine.",
                               stats=_full_stats(db))

    clean = []
    for tx in pending:
        item = {k: (str(v) if k == "_id" else v) for k, v in tx.items()}
        clean.append(item)

    total_fees = _collect_fees(clean)

    start_time = time.time()
    new_block = blockchain.add_block(clean)
    mine_time = round(time.time() - start_time, 2)

    new_block.total_fees = total_fees
    new_block.miner_address = miner_address
    new_block.difficulty = blockchain.difficulty

    if len(blockchain.chain) >= 2:
        valid, msg = validate_block(new_block, blockchain.chain[-2])
        if not valid:
            blockchain.chain.pop()
            return render_template("blockchain.html", chain=blockchain.chain,
                                   message=f"Block rejected: {msg}", stats=_full_stats(db))

    block_doc = create_block_doc(new_block)
    block_doc["total_fees"] = total_fees
    block_doc["miner_address"] = miner_address
    block_doc["mine_time"] = mine_time
    db.blocks.insert_one(block_doc)

    db.transactions.update_many({"status": "Pending"}, {"$set": {"status": "Mined"}})
    mempool.clear()

    if total_fees > 0:
        db.users.update_one({"email": session["user"]},
                            {"$inc": {"wallet.cash": total_fees}})

    _adjust_difficulty()

    db.notifications.insert_one({
        "user_email": session["user"],
        "message": f"Block #{new_block.index} mined in {mine_time}s! Fees earned: ₹{total_fees}",
        "type": "SYSTEM", "read": False, "created_at": datetime.now(),
    })

    return render_template("blockchain.html", chain=blockchain.chain,
                           message=f"Block #{new_block.index} mined in {mine_time}s! Fees: ₹{total_fees}",
                           stats=_full_stats(db))


@blockchain_bp.route("/view")
def view_chain():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    return render_template("blockchain.html", chain=blockchain.chain,
                           message=None, stats=_full_stats(db))


@blockchain_bp.route("/stats")
def chain_stats():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    return jsonify(_full_stats(db))
