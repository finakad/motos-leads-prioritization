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
    conversion_probability: float | None = None
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
    conversion_probability: float | None = None
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


class ScoringRunRead(BaseModel):
    id: UUID
    company_id: str
    model_version: str
    leads_scored: int
    high_priority_count: int
    medium_priority_count: int
    low_priority_count: int
    average_score: float
    execution_type: str
    status: str
    started_at: datetime
    finished_at: datetime


class ModelEvaluationReport(BaseModel):
    id: UUID
    model_version: str
    dataset_name: str
    evaluation_type: str
    sample_size: int
    train_size: int
    test_size: int
    metrics: dict[str, Any]
    limitations: dict[str, Any]
    created_at: datetime

