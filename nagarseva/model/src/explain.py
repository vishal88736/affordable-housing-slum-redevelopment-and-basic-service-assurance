"""Human-readable feature explanations with optional SHAP integration."""

from __future__ import annotations

from typing import Any

REASONS = {
    "pct_below_poverty": ("high poverty exposure", "increase priority"),
    "density_per_ha": ("high population density", "increase priority"),
    "pct_kutcha_houses": ("many structurally vulnerable homes", "increase priority"),
    "flood_risk_score": ("flood exposure", "increase priority"),
    "fire_risk_score": ("fire exposure", "increase priority"),
    "structural_risk_score": ("structural risk", "increase priority"),
    "distance_to_hospital_km": ("limited access to a hospital", "increase priority"),
    "water_hours_per_day": ("low daily water supply", "increase priority"),
    "outage_hours_per_week": ("frequent power outages", "increase priority"),
    "tenure_security_score": ("tenure uncertainty", "increase priority"),
}


def priority_reasons(row: dict[str, Any], limit: int = 4) -> list[dict[str, Any]]:
    values = []
    for feature, (label, direction) in REASONS.items():
        value = row.get(feature)
        if value is None:
            continue
        numeric = float(value)
        # Simple normalized contribution that remains explainable offline.
        contribution = numeric / 100 if feature not in {"water_hours_per_day", "distance_to_hospital_km", "tenure_security_score"} else (1 - min(numeric / (12 if feature == "water_hours_per_day" else 10 if feature == "distance_to_hospital_km" else 100), 1))
        if feature == "tenure_security_score":
            contribution = 1 - numeric / 100
        if feature == "distance_to_hospital_km":
            contribution = min(numeric / 10, 1)
        values.append({"feature": feature, "label": label, "value": round(numeric, 2), "contribution": round(max(0, contribution) * 100, 1), "direction": direction})
    return sorted(values, key=lambda item: item["contribution"], reverse=True)[:limit]


def shap_values_if_available(model: Any, X: Any) -> Any:
    try:
        import shap  # type: ignore
        return shap.Explainer(model)(X)
    except Exception:
        return None
