def build_wallet_graph(transactions):
    graph = {}

    for tx in transactions:
        sender = str(tx.get("sender", "") or "")
        receiver = str(tx.get("receiver", "") or "")
        amount = tx.get("amount", 0) or 0

        if not sender:
            continue

        if sender not in graph:
            graph[sender] = {
                "sent_to": [],
                "total_sent": 0,
                "tx_count": 0,
            }

        if receiver and receiver not in graph[sender]["sent_to"]:
            graph[sender]["sent_to"].append(receiver)

        graph[sender]["total_sent"] += int(amount)
        graph[sender]["tx_count"] += 1

    return graph


def get_suspicious_patterns(graph):
    suspicious = []
    for wallet, details in graph.items():
        if len(details.get("sent_to", [])) > 5:
            suspicious.append(wallet)
    return suspicious
