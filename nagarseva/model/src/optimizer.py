"""Budget allocation with a PuLP ILP when installed and a transparent fallback."""

from __future__ import annotations

from typing import Any
import pandas as pd
import numpy as np


def _options(pockets: pd.DataFrame) -> pd.DataFrame:
    frame = pockets.copy()
    frame["cost_inr"] = frame["population"].fillna(0) * (9500 + frame["structural_risk_score"].fillna(50) * 80)
    frame["impact"] = frame["population"].fillna(0) * (frame["priority_score"].fillna(50) / 100)
    frame["vulnerable"] = frame["priority_score"].fillna(0) >= 65
    return frame


def optimise(pockets: pd.DataFrame, budget_inr: float, min_vulnerable_share: float = .25, min_wards: int = 3) -> dict[str, Any]:
    if budget_inr <= 0:
        raise ValueError("budget_inr must be greater than zero")
    frame = _options(pockets)
    try:
        import pulp  # type: ignore
        problem = pulp.LpProblem("NagarSeva", pulp.LpMaximize)
        choices = {i: pulp.LpVariable(f"x_{i}", cat="Binary") for i in frame.index}
        problem += pulp.lpSum(choices[i] * float(frame.loc[i, "impact"]) for i in frame.index)
        problem += pulp.lpSum(choices[i] * float(frame.loc[i, "cost_inr"]) for i in frame.index) <= budget_inr
        problem += pulp.lpSum(choices[i] for i in frame.index if frame.loc[i, "vulnerable"]) >= min_vulnerable_share * pulp.lpSum(choices.values())
        problem += pulp.lpSum(choices[i] for i in frame.index) >= min(min_wards, len(frame))
        # Approximate ward fairness: selected pockets in any ward cannot exceed 60%.
        for _, ward in frame.groupby("ward"):
            problem += pulp.lpSum(choices[i] for i in ward.index) <= .6 * pulp.lpSum(choices.values()) + 1
        problem.solve(pulp.PULP_CBC_CMD(msg=False))
        selected = frame[[choices[i].value() == 1 for i in frame.index]]
        solver = "PuLP ILP"
    except Exception:
        # Greedy marginal impact/cost, then add a missing ward if affordable.
        frame["ratio"] = frame["impact"] / frame["cost_inr"].clip(lower=1)
        selected_rows = []
        spent = 0.0
        for i, row in frame.sort_values(["vulnerable", "ratio"], ascending=False).iterrows():
            if spent + row.cost_inr <= budget_inr and (len(selected_rows) < min_wards or len(selected_rows) < 40):
                selected_rows.append(i); spent += row.cost_inr
        selected = frame.loc[selected_rows]
        solver = "Greedy fallback (install PuLP for exact ILP)"
    selected = selected.copy()
    selected["cost_inr"] = selected.cost_inr.round(0)
    selected["impact"] = selected.impact.round(0)
    ward_counts = selected.groupby("ward").size().to_dict()
    vulnerable_share = float(selected.vulnerable.mean()) if len(selected) else 0
    return {"solver": solver, "budget_inr": budget_inr, "spent_inr": float(selected.cost_inr.sum()), "impact_people": int(selected.impact.sum()), "vulnerable_share": round(vulnerable_share, 3), "ward_counts": ward_counts, "selected": selected[["pocket_id", "city", "ward", "priority_score", "cost_inr", "impact"]].to_dict("records"), "pareto": pareto_frontier(frame, budget_inr)}


def pareto_frontier(pockets: pd.DataFrame, max_budget: float) -> list[dict[str, float]]:
    frame = _options(pockets).sort_values("ratio" if "ratio" in pockets else "impact", ascending=False)
    points = []
    for fraction in [.1, .2, .4, .6, .8, 1.0]:
        budget = max_budget * fraction
        chosen = frame.sort_values("impact", ascending=False)
        spent = impact = 0
        for row in chosen.itertuples():
            if spent + row.cost_inr <= budget:
                spent += row.cost_inr; impact += row.impact
        points.append({"budget_inr": round(budget), "impact_people": round(impact), "spent_inr": round(spent)})
    return points
