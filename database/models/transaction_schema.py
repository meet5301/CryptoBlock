import hashlib
import time


def create_tx_doc(sender, receiver, amount):
    return {
        "sender": sender,
        "receiver": receiver,
        "amount": amount,
        "status": "Pending",
        "timestamp": time.time(),
        "tx_id": hashlib.sha256(f"{sender}{receiver}{amount}{time.time()}".encode()).hexdigest()[:16],
        "ai_status": None,
        "risk_score": None,
    }
