"""Pydantic request and response contracts for the NagarSeva API."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field, ConfigDict


class PriorityRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    features: dict[str, float] = Field(default_factory=dict)


class InterventionRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    features: dict[str, Any] = Field(default_factory=dict)


class CostRequest(BaseModel):
    units: int = Field(500, ge=1)
    carpet_area_sqft: float = Field(300, gt=0)
    land_value_per_sqm: float = Field(40_000, ge=0)
    FSI: float = Field(2.5, gt=0)
    cross_subsidy_ratio: float = Field(.5, ge=0, le=1)


class FeasibilityRequest(BaseModel):
    land_area_sqm: float = Field(..., gt=0)
    fsi: float = Field(..., gt=0, le=10)
    eligible_households: int = Field(..., ge=0)
    rehab_area_sqft: float = Field(300, gt=0)
    construction_cost_per_sqft: float = Field(3200, gt=0)
    market_sale_rate_per_sqft: float = Field(14500, gt=0)
    tdr_value_per_sqft: float = Field(900, ge=0)
    premiums_and_fees_pct: float = Field(.12, ge=0, le=1)
    sales_share_pct: float = Field(.65, ge=0, le=1)
    cost_inflation_pct: float = Field(0, ge=-50, le=200)


class OptimizeRequest(BaseModel):
    budget_inr: float = Field(..., gt=0)
    min_vulnerable_share: float = Field(.25, ge=0, le=1)
    min_wards: int = Field(3, ge=1, le=20)


class GrievanceRequest(BaseModel):
    text: str = Field(..., min_length=3, max_length=2_000)
    pocket_id: str | None = None
    language: str = Field("en", pattern="^(en|hi|mr)$")


class EligibilityRequest(BaseModel):
    monthly_income_inr: float = Field(..., ge=0)
    family_size: int = Field(..., ge=1, le=20)
    has_aadhaar: bool = False
    has_ration_card: bool = False
    has_address_proof: bool = False
    years_in_settlement: int = Field(0, ge=0)
    tenure_document: bool = False
