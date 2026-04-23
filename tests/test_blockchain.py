from core.blockchain import Blockchain


def test_blockchain_adds_and_validates_blocks() -> None:
    blockchain = Blockchain()
    blockchain.add_block([
        {"sender": "alice", "receiver": "bob", "amount": 10},
    ])

    assert len(blockchain.chain) == 2
    assert blockchain.is_valid() is True
