import hashlib
import secrets


def generate_wallet():
    private_key = secrets.token_hex(32)
    public_key = hashlib.sha256(private_key.encode()).hexdigest()
    wallet_address = "0x" + hashlib.sha256(public_key.encode()).hexdigest()[:16]

    return {
        "private_key": private_key,
        "public_key": public_key,
        "wallet_address": wallet_address,
        "balance": 1000,
    }
