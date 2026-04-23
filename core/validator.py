import hashlib
import hmac


def sign_transaction(tx: dict, private_key: str) -> str:
    payload = f"{tx.get('sender','')}{tx.get('receiver','')}{tx.get('amount',0)}"
    return hmac.new(private_key.encode(), payload.encode(), hashlib.sha256).hexdigest()


def verify_transaction_signature(tx: dict, private_key: str) -> bool:
    expected = sign_transaction(tx, private_key)
    return hmac.compare_digest(expected, tx.get("signature", ""))


def validate_transaction(tx: dict, user: dict) -> tuple[bool, str]:
    amount = tx.get("amount", 0)
    if not isinstance(amount, (int, float)) or amount <= 0:
        return False, "Invalid amount"

    wallet = user.get("wallet", {})
    tx_type = tx.get("type", "TRANSFER")

    if tx_type == "TRANSFER":
        if wallet.get("balance", 0) < amount:
            return False, "Insufficient blockchain balance"

    private_key = wallet.get("private_key", "")
    if private_key and tx.get("signature"):
        if not verify_transaction_signature(tx, private_key):
            return False, "Invalid signature"

    return True, "OK"


def validate_block(block, prev_block) -> tuple[bool, str]:
    if block.previous_hash != prev_block.hash:
        return False, "Previous hash mismatch"

    if block.hash != block.calculate_hash():
        return False, "Block hash invalid"

    difficulty = getattr(block, "difficulty", 3)
    if not block.hash.startswith("0" * difficulty):
        return False, f"PoW not satisfied (difficulty={difficulty})"

    return True, "OK"
