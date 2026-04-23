from ai.features import extract_features
from ai.model import train_model
from ai.risk_scorer import calculate_risk_score, get_risk_color, get_risk_label


def detect_anomalies(transactions):
    if not transactions:
        return []

    X = extract_features(transactions)
    model = train_model(X)

    results = []

    if model is None:
        for tx in transactions:
            item = dict(tx)
            item["ai_status"] = "Normal"
            item["risk_score"] = 0
            item["risk_label"] = get_risk_label(0)
            item["risk_color"] = get_risk_color(0)
            results.append(item)
        return results

    predictions = model.predict(X)
    raw_scores = model.score_samples(X)

    for tx, prediction, raw_score in zip(transactions, predictions, raw_scores):
        item = dict(tx)
        item["ai_status"] = "Suspicious" if prediction == -1 else "Normal"

        risk_score = calculate_risk_score(raw_score)
        item["risk_score"] = risk_score
        item["risk_label"] = get_risk_label(risk_score)
        item["risk_color"] = get_risk_color(risk_score)

        results.append(item)

    return results
