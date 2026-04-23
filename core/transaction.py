import hashlib
import json
import time


def create_transaction(sender, receiver, amount):
    return {
        "sender": sender,
        "receiver": receiver,
        "amount": amount,
        "timestamp": time.time(),
    }


def sign_transaction(private_key, tx_data):
    tx_string = json.dumps(tx_data, sort_keys=True)
    signature = hashlib.sha256((tx_string + private_key).encode()).hexdigest()
    return signature


def verify_transaction(public_key, tx_data, signature):
    tx_string = json.dumps(tx_data, sort_keys=True)
    check_signature = hashlib.sha256((tx_string + public_key).encode()).hexdigest()
    return signature == check_signature
