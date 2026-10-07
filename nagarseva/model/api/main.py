"""FastAPI service for the NagarSeva decision-support demo."""

from __future__ import annotations

import logging
from pathlib import Path
import sys
from typing import Any

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "model" / "src"))

from model.src import features  # noqa: E402
from model.src.explain import priority_reasons  # noqa: E402
from model.src.feasibility import FeasibilityInput, sensitivity, simulate  # noqa: E402
from model.src.optimizer import optimise  # noqa: E402
from .schemas import (  # noqa: E402
    CostRequest, EligibilityRequest, FeasibilityRequest, GrievanceRequest,
    InterventionRequest, OptimizeRequest, PriorityRequest,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("nagarseva.api")

app = FastAPI(title="NagarSeva API", version="0.1.0", description="Synthetic-data demo API for equitable urban service planning.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

MODELS: dict[str, Any] = {}
TABLES: dict[str, pd.DataFrame] = {}
GRIEVANCES: list[dict[str, Any]] = []


def _load() -> None:
    """Load models once and use safe heuristic operation if artifacts are absent."""
    for name, path in {"priority": "priority_model.joblib", "intervention": "intervention_model.joblib", "service": "service_gap_model.joblib", "cost": "cost_model.joblib", "nlp": "grievance_model.joblib"}.items():
        try:
            MODELS[name] = joblib.load(features.ARTIFACTS / path)
        except Exception as exc:
            logger.warning("Artifact %s unavailable: %s; using fallback", name, exc)
    try:
        for name in ["slum_pockets", "service_access", "grievances", "redevelopment_projects", "households_sample"]:
            TABLES[name] = features.read_table(f"{name}.csv")
        TABLES["joined"] = TABLES["slum_pockets"].merge(TABLES["service_access"], on="pocket_id", how="left")
    except Exception as exc:
        logger.error("Data unavailable: %s", exc)
    logger.info("NagarSeva loaded %s models and %s tables", len(MODELS), len(TABLES))


@app.on_event("startup")
def startup() -> None:
    _load()


def _row(pocket_id: str) -> pd.Series:
    frame = TABLES.get("joined", pd.DataFrame())
    found = frame[frame.pocket_id == pocket_id]
    if found.empty:
        raise HTTPException(status_code=404, detail=f"Pocket {pocket_id} not found")
    return found.iloc[0]


def _score(row: pd.Series) -> float:
    model = MODELS.get("priority")
    if model:
        values = features.numeric_frame(pd.DataFrame([row]), model["features"])
        return float(np.clip(model["model"].predict(values)[0], 0, 100))
    return float(features.policy_priority(pd.DataFrame([row])).iloc[0])


def _scores(frame: pd.DataFrame) -> np.ndarray:
    """Vectorised score path for map and summary endpoints."""
    model = MODELS.get("priority")
    if model:
        values = features.numeric_frame(frame, model["features"])
        return np.clip(model["model"].predict(values), 0, 100)
    return features.policy_priority(frame).to_numpy()


def _intervention(row: pd.Series) -> dict[str, Any]:
    labels = ["in_situ_SRA", "upgrading", "relocation", "rental_housing"]
    model = MODELS.get("intervention")
    if model:
        values = features.numeric_frame(pd.DataFrame([row]), model["features"])
        estimator = model["model"]
        probs = estimator.predict_proba(values)[0]
        classes = list(estimator.classes_)
        options = sorted(({"type": cls, "probability": round(float(prob), 3)} for cls, prob in zip(classes, probs)), key=lambda x: x["probability"], reverse=True)[:2]
    else:
        choices = [("relocation", .42 if row.get("flood_risk_score", 0) > 80 else .14), ("in_situ_SRA", .49 if row.get("tenure_security_score", 0) > 50 else .22), ("upgrading", .44), ("rental_housing", .18)]
        total = sum(value for _, value in choices)
        options = [{"type": key, "probability": round(value / total, 3)} for key, value in sorted(choices, key=lambda x: x[1], reverse=True)[:2]]
    reasons = []
    if row.get("land_ownership") in {"forest", "CRZ"} or row.get("flood_risk_score", 0) > 80:
        reasons.append("high hazard or restricted land makes a safer alternative important")
    if row.get("tenure_security_score", 0) > 55:
        reasons.append("stronger tenure signal supports in-situ investment")
    if row.get("density_per_ha", 0) > 500:
        reasons.append("dense settlement benefits from phased service upgrading")
    reasons.append("final selection requires resident consultation and statutory review")
    return {"top_options": options, "reasons": reasons}


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "synthetic_demo": True, "models_loaded": sorted(MODELS), "tables_loaded": sorted(TABLES)}


@app.get("/pockets")
def pockets(city: str | None = None, ward: str | None = None, tier: str | None = None, bbox: str | None = Query(None, description="minLon,minLat,maxLon,maxLat")) -> dict[str, Any]:
    frame = TABLES.get("joined", pd.DataFrame()).copy()
    if frame.empty:
        return {"items": [], "total": 0}
    frame["priority_score"] = _scores(frame)
    frame["tier"] = frame.priority_score.map(features.tier)
    if city: frame = frame[frame.city.str.lower() == city.lower()]
    if ward: frame = frame[frame.ward.str.lower() == ward.lower()]
    if tier: frame = frame[frame.tier.str.lower() == tier.lower()]
    if bbox:
        try:
            min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(","))
            frame = frame[frame.lon.between(min_lon, max_lon) & frame.lat.between(min_lat, max_lat)]
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="bbox must be minLon,minLat,maxLon,maxLat") from exc
    frame = frame.sort_values("priority_score", ascending=False)
    items = frame.head(500).replace({np.nan: None}).to_dict("records")
    return {"items": items, "total": len(frame), "synthetic": True}


@app.get("/pockets/{pocket_id}")
def pocket_detail(pocket_id: str) -> dict[str, Any]:
    row = _row(pocket_id)
    score = _score(row)
    data = row.replace({np.nan: None}).to_dict()
    data.update({"priority_score": round(score, 1), "tier": features.tier(score), "shap_reasons": priority_reasons(data), "intervention": _intervention(row), "service_assurance": features.service_index(row), "synthetic": True})
    return data


@app.post("/priority/score")
def priority_score(payload: PriorityRequest) -> dict[str, Any]:
    body = payload.model_dump()
    feature_values = {**body.pop("features", {}), **body}
    row = pd.Series(feature_values)
    score = _score(row)
    return {"priority_score": round(score, 1), "tier": features.tier(score), "reasons": priority_reasons(feature_values), "synthetic": True}


@app.post("/intervention/recommend")
def intervention(payload: InterventionRequest) -> dict[str, Any]:
    body = payload.model_dump()
    feature_values = {**body.pop("features", {}), **body}
    return {**_intervention(pd.Series(feature_values)), "synthetic": True}


@app.get("/service/{pocket_id}/assurance")
def assurance(pocket_id: str) -> dict[str, Any]:
    row = _row(pocket_id)
    indexes = features.service_index(row)
    failures = {"water": float(row.get("water_hours_per_day", 0) < 4), "sanitation": float(row.get("toilets_per_100_people", 0) < 15), "power": float(row.get("outage_hours_per_week", 0) > 12), "waste": float(row.get("waste_collection_frequency", 0) < 3)}
    return {"pocket_id": pocket_id, "assurance_index": round(float(np.mean(list(indexes.values()))), 1), "services": {key: {"score": round(value, 1), "status": "compliant" if value >= 70 else "watch" if value >= 45 else "breach", "failure_probability_90d": round(failures.get(key, 0) * .72, 2)} for key, value in indexes.items()}, "trend": [{"month": f"2025-{m:02d}", "score": round(float(np.clip(np.mean(list(indexes.values())) + (m - 6) * 1.3 + np.sin(m) * 2, 0, 100)), 1)} for m in range(1, 7)], "synthetic": True}


@app.post("/cost/estimate")
def cost(payload: CostRequest) -> dict[str, Any]:
    model = MODELS.get("cost")
    values = pd.DataFrame([payload.model_dump()])
    if model:
        X = values[model["features"]]
        cost_value = float(model["cost"].predict(X)[0]); delay = float(model["delay"].predict(X)[0])
        cost_band = model.get("cost_residual_std", 400) * 1.28; delay_band = model.get("delay_residual_std", 5) * 1.28
    else:
        cost_value = 2200 + payload.land_value_per_sqm / 70 + payload.FSI * 190 + payload.cross_subsidy_ratio * 170
        delay = 10 + payload.units / 400 + payload.FSI * 2
        cost_band, delay_band = 420, 5
    return {"construction_cost_per_sqft": round(cost_value), "cost_interval": [round(max(0, cost_value - cost_band)), round(cost_value + cost_band)], "expected_delay_months": round(delay, 1), "delay_interval": [round(max(0, delay - delay_band), 1), round(delay + delay_band, 1)], "synthetic": True}


@app.post("/feasibility/simulate")
def feasibility(payload: FeasibilityRequest) -> dict[str, Any]:
    values = payload.model_dump()
    return {"result": simulate(values), "sensitivity": sensitivity(values), "synthetic": True}


@app.post("/optimize")
def optimize(payload: OptimizeRequest) -> dict[str, Any]:
    frame = TABLES.get("joined", pd.DataFrame()).copy()
    frame["priority_score"] = _scores(frame)
    return {**optimise(frame, payload.budget_inr, payload.min_vulnerable_share, payload.min_wards), "synthetic": True}


@app.post("/grievance/classify")
def classify_grievance(payload: GrievanceRequest) -> dict[str, Any]:
    model = MODELS.get("nlp")
    if model:
        category = str(model.predict([payload.text])[0])
        probabilities = model.predict_proba([payload.text])[0]
        confidence = float(max(probabilities))
    else:
        lower = payload.text.lower()
        terms = {"water": ["water", "paani", "पानी"], "sanitation": ["toilet", "शौचालय", "safai"], "power": ["light", "bijli", "बिजली"], "waste": ["garbage", "kachra", "कचरा"], "drainage": ["drain", "nala", "नाला"], "health": ["clinic", "fever", "बच्चों"], "safety": ["unsafe", "women", "सुरक्षित"], "housing": ["sra", "rehab", "पुनर्विकास"]}
        category = max(terms, key=lambda key: sum(term in lower for term in terms[key]))
        confidence = .64
    urgency = "urgent" if any(term in payload.text.lower() for term in ["fire", "danger", "unsafe", "fever", "गंदा", "असुरक्षित"]) else "standard"
    return {"category": category, "confidence": round(confidence, 3), "urgency": urgency, "expected_resolution_days": 2 if urgency == "urgent" else 7, "synthetic": True}


@app.post("/grievances")
def create_grievance(payload: GrievanceRequest) -> dict[str, Any]:
    classification = classify_grievance(payload)
    record = {"complaint_id": f"LIVE-{len(GRIEVANCES) + 1:04d}", "text": payload.text, "pocket_id": payload.pocket_id, "language": payload.language, **classification, "status": "received"}
    GRIEVANCES.insert(0, record)
    return record


@app.get("/grievances")
def list_grievances(status: str | None = None) -> dict[str, Any]:
    data = [g for g in GRIEVANCES if not status or g["status"] == status]
    return {"items": data, "total": len(data)}


@app.post("/eligibility/check")
def eligibility(payload: EligibilityRequest) -> dict[str, Any]:
    schemes = []
    reasons = []
    if payload.monthly_income_inr <= 50_000 and payload.has_aadhaar:
        schemes.append("PMAY-U / CLSS"); reasons.append("income is within the demo EWS/LIG screening band and Aadhaar is available")
    if payload.years_in_settlement >= 10 and payload.tenure_document:
        schemes.append("Maharashtra SRA"); reasons.append("settlement duration and tenure document meet the screening rule")
    if payload.monthly_income_inr <= 25_000:
        schemes.append("Affordable rental housing"); reasons.append("income is within the rental-housing screening band")
    documents = ["Aadhaar / identity proof", "ration card or income proof", "address or residence proof", "bank account details"]
    return {"eligible_schemes": schemes, "reasons": reasons or ["more documents or a field verification may be needed"], "documents_required": documents, "next_steps": ["Save this screening result", "Visit the ward help desk for verification", "Do not share original documents with unverified agents"], "disclaimer": "Screening only; final eligibility is decided by the relevant authority.", "synthetic": True}


@app.get("/stats/summary")
def summary() -> dict[str, Any]:
    frame = TABLES.get("joined", pd.DataFrame())
    if frame.empty: return {"synthetic": True}
    scores = _scores(frame)
    gaps = ((frame.water_hours_per_day < 4) | (frame.toilets_per_100_people < 15) | (frame.outage_hours_per_week > 12)).sum()
    return {"pockets_prioritised": len(frame), "households_covered": int(frame.households.sum()), "critical_pockets": int((scores >= 75).sum()), "service_gaps_flagged": int(gaps), "projected_cost_saved_inr": 184_000_000, "avg_assurance_index": round(float(frame.apply(lambda row: np.mean(list(features.service_index(row).values())), axis=1).mean()), 1), "synthetic": True}
