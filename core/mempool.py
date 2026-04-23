class Mempool:
    def __init__(self):
        self.pending = []

    def add_transaction(self, tx_dict):
        self.pending.append(tx_dict)

    def get_pending(self):
        return self.pending

    def clear(self):
        self.pending = []

    def get_count(self):
        return len(self.pending)

    def has_transactions(self):
        return len(self.pending) > 0


mempool = Mempool()
