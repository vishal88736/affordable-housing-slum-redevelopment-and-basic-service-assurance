import pandas as pd

from model.src.optimizer import optimise


def test_optimizer_respects_budget_and_returns_frontier():
    pockets = pd.DataFrame({
        "pocket_id": ["a", "b", "c", "d"], "city": ["A"] * 4, "ward": ["w1", "w1", "w2", "w3"],
        "population": [100, 200, 300, 150], "structural_risk_score": [90, 20, 75, 50], "priority_score": [90, 35, 80, 65],
    })
    result = optimise(pockets, 5_000_000, min_vulnerable_share=.25, min_wards=2)
    assert result["spent_inr"] <= 5_000_000
    assert result["vulnerable_share"] >= .25
    assert result["pareto"]
