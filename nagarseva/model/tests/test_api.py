from fastapi.testclient import TestClient

from model.api.main import app


def test_core_api_contracts():
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/pockets").json()["total"] >= 1
        assert client.get("/pockets/NS-0001").json()["shap_reasons"]
        assert client.get("/service/NS-0001/assurance").json()["services"]
        assert client.post("/priority/score", json={"features": {"flood_risk_score": 90, "pct_below_poverty": .8}}).status_code == 200
        assert client.post("/intervention/recommend", json={"features": {"land_ownership": "state", "flood_risk_score": 82}}).status_code == 200
        assert client.post("/cost/estimate", json={}).status_code == 200
        assert client.post("/feasibility/simulate", json={"land_area_sqm": 5000, "fsi": 2.5, "eligible_households": 200}).status_code == 200
        assert client.post("/optimize", json={"budget_inr": 50_000_000}).status_code == 200
        assert client.post("/grievance/classify", json={"text": "Paani nahi aa raha"}).status_code == 200
        assert client.post("/grievances", json={"text": "Garbage kachra not collected"}).status_code == 200
        assert client.get("/grievances").json()["total"] == 1
        assert client.post("/eligibility/check", json={"monthly_income_inr": 18000, "family_size": 4, "has_aadhaar": True}).status_code == 200
        assert client.get("/stats/summary").status_code == 200
