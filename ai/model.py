from sklearn.ensemble import IsolationForest


def train_model(X):
    if not X or len(X) <= 1:
        return None

    model = IsolationForest(
        n_estimators=100,
        contamination=0.1,
        random_state=42,
    )
    model.fit(X)
    return model


def get_model_info():
    return {
        "model_type": "IsolationForest",
        "features": 8,
        "contamination": 0.1,
    }
