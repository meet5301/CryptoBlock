from ecdsa import SECP256k1, SigningKey, VerifyingKey

from core.transaction import Transaction


def test_transaction_signature_verification() -> None:
    signing_key = SigningKey.generate(curve=SECP256k1)
    verifying_key = signing_key.get_verifying_key()

    transaction = Transaction(
        sender="alice",
        receiver="bob",
        amount=1,
        timestamp=1,
    )

    transaction.sign(signing_key.to_string().hex())
    assert transaction.verify(verifying_key.to_string().hex()) is True
