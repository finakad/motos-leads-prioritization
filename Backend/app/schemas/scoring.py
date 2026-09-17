from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class FactorDetail(BaseModel):
    name: str
    weight_pct: float
    score_obtained: float
    max_score: float
    description: str
    evidence: list[str] = Field(default_factory=list)


class LeadScoreDetail(BaseModel):
    id: UUID | None = None
    lead_id: str
    company_id: str
    sales_point_id: str
    customer_name: str | None
    phone_normalized: str | None
    channel: str | None
    model_interest_text: str | None
    score: float
    priority_tier: Literal["ALTA", "MEDIA", "BAJA"]
    factors: dict[str, FactorDetail]
    evidence: list[dict[str, Any]]
    model_version: str
    calculated_at: datetime


class LeadPrioritizedItem(BaseModel):
    lead_id: str
    company_id: str
    sales_point_id: str
    customer_name: str | None
    phone: str | None
    channel: str | None
    model_interest: str | None
    score: float
    priority_tier: Literal["ALTA", "MEDIA", "BAJA"]
    urgency: str | None = None
    has_conversation: bool = False
    calculated_at: datetime


class PrioritizationSummary(BaseModel):
    company_id: str
    total_leads_evaluated: int
    scores_calculated: int
    tier_distribution: dict[str, int]
    average_score: float
    model_version: str
    calculated_at: datetime
