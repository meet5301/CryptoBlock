from ai.detector import EnsembleDetector
from ai.features import extract_features
from ai.risk_scorer import score_transaction


def test_feature_extraction_produces_enriched_vector() -> None:
    features = extract_features([
        {"sender": "alice", "receiver": "bob", "amount": 10, "timestamp": 1, "fee": 2, "gas": 3},
    ])

    assert len(features) == 1
    assert len(features[0]) >= 8


def test_risk_score_is_clamped() -> None:
    score = score_transaction({"amount": 1000, "fee": 10, "pattern_flag": True}, ai_status="Suspicious")
    assert 0 <= score <= 100


def test_detector_returns_analyzed_transactions() -> None:
    detector = EnsembleDetector()
    analyzed = detector.fit_predict([
        {"sender": "alice", "receiver": "bob", "amount": 10, "timestamp": 1},
    ])

    assert analyzed[0]["ai_status"] in {"Normal", "Suspicious"}
