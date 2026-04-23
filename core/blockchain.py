from core.block import Block


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 3

    def create_genesis_block(self):
        return Block(0, [], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, transactions):
        new_block = Block(
            index=len(self.chain),
            transactions=transactions,
            previous_hash=self.get_latest_block().hash,
        )
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        return new_block

    def is_chain_valid(self):
        for index in range(1, len(self.chain)):
            current = self.chain[index]
            previous = self.chain[index - 1]

            if current.hash != current.calculate_hash():
                return False

            if current.previous_hash != previous.hash:
                return False

        return True

    def get_chain_stats(self):
        return {
            "total_blocks": len(self.chain),
            "difficulty": self.difficulty,
            "latest_hash": self.get_latest_block().hash,
            "is_valid": self.is_chain_valid(),
        }
