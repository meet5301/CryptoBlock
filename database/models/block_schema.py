import time


def create_block_doc(block_obj):
    return {
        "index": block_obj.index,
        "hash": block_obj.hash,
        "previous_hash": block_obj.previous_hash,
        "nonce": block_obj.nonce,
        "timestamp": block_obj.timestamp,
        "tx_count": len(block_obj.transactions),
        "mined_at": time.time(),
    }
