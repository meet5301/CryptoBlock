def calculate_risk_score(raw_score):
    risk = int((1 - ((raw_score + 0.5) / 1.0)) * 100)
    return max(0, min(100, risk))


def get_risk_label(score):
    if score <= 30:
        return "Low Risk"
    if score <= 60:
        return "Medium Risk"
    return "High Risk"


def get_risk_color(score):
    if score <= 30:
        return "positive"
    if score <= 60:
        return "warning"
    return "danger"
