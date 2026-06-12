import os
import json
from typing import Dict, Any

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

FEATURE_COLUMNS = [
    "certifications_match_pct",
    "requirements_matched_pct",
    "past_relationship",
    "budget_alignment_score",
    "technical_score_pct",
    "estimated_competitor_count",
]


class WinProbabilityModel:
    def __init__(self):
        df = pd.read_csv(os.path.join(DATA_DIR, "historical_bids.csv"))
        self.df = df

        X = df[FEATURE_COLUMNS].copy()
        y = (df["outcome"] == "win").astype(int)

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        self.model = LogisticRegression(max_iter=1000)
        self.model.fit(X_scaled, y)

        self.train_accuracy = round(float(self.model.score(X_scaled, y)), 3)
        self.base_win_rate = round(float(y.mean()), 3)

        coefs = self.model.coef_[0]
        self.feature_importance = sorted(
            [
                {"feature": f, "coefficient": round(float(c), 3)}
                for f, c in zip(FEATURE_COLUMNS, coefs)
            ],
            key=lambda x: abs(x["coefficient"]),
            reverse=True,
        )

    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        row = pd.DataFrame([{c: features.get(c, 0) for c in FEATURE_COLUMNS}])
        row_scaled = self.scaler.transform(row[FEATURE_COLUMNS])
        proba = float(self.model.predict_proba(row_scaled)[0][1])

        contributions = []
        for f, coef, val_scaled in zip(FEATURE_COLUMNS, self.model.coef_[0], row_scaled[0]):
            contributions.append({
                "feature": f,
                "value": features.get(f, 0),
                "contribution": round(float(coef * val_scaled), 3),
            })
        contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)

        return {
            "win_probability": round(proba, 3),
            "win_probability_pct": round(proba * 100, 1),
            "base_win_rate_pct": round(self.base_win_rate * 100, 1),
            "model_train_accuracy_pct": round(self.train_accuracy * 100, 1),
            "top_contributing_factors": contributions[:4],
        }


def go_no_go_decision(
    win_probability_pct: float,
    gap_count: int,
    total_requirements: int,
    budget_alignment_score: float,
) -> Dict[str, Any]:
    """Heuristic GO/NO-GO recommendation combining win probability with
    hard compliance/eligibility blockers."""

    gap_pct = (gap_count / total_requirements * 100) if total_requirements else 0
    reasons = []

    if gap_pct > 25:
        decision = "NO-GO"
        reasons.append(
            f"{gap_count} of {total_requirements} mandatory requirements "
            f"({round(gap_pct,1)}%) are unmet -- high disqualification risk."
        )
    elif budget_alignment_score < 0.55:
        decision = "NO-GO"
        reasons.append(
            "Budget alignment score is low -- the opportunity's budget "
            "appears misaligned with typical project economics."
        )
    elif win_probability_pct >= 55:
        decision = "GO"
        reasons.append(
            f"Modeled win probability ({win_probability_pct}%) exceeds the "
            f"55% threshold based on similar historical bids."
        )
    elif win_probability_pct >= 35:
        decision = "CONDITIONAL GO"
        reasons.append(
            f"Win probability ({win_probability_pct}%) is moderate. "
            f"Recommend closing the {gap_count} compliance gap(s) before committing."
        )
    else:
        decision = "NO-GO"
        reasons.append(
            f"Win probability ({win_probability_pct}%) is below the 35% "
            f"viability threshold based on similar historical bids."
        )

    if gap_count > 0 and decision != "NO-GO":
        reasons.append(
            f"{gap_count} requirement(s) currently lack supporting evidence "
            f"in the capability library -- prioritize these first."
        )

    return {"decision": decision, "reasons": reasons, "gap_pct": round(gap_pct, 1)}


if __name__ == "__main__":
    model = WinProbabilityModel()
    print("Base win rate:", model.base_win_rate)
    print("Train accuracy:", model.train_accuracy)
    print("Feature importance:", json.dumps(model.feature_importance, indent=2))

    sample = model.predict({
        "certifications_match_pct": 75,
        "requirements_matched_pct": 64.7,
        "past_relationship": 0,
        "budget_alignment_score": 0.85,
        "technical_score_pct": 80,
        "estimated_competitor_count": 5,
    })
    print(json.dumps(sample, indent=2))

    decision = go_no_go_decision(
        win_probability_pct=sample["win_probability_pct"],
        gap_count=4,
        total_requirements=17,
        budget_alignment_score=0.85,
    )
    print(json.dumps(decision, indent=2))
