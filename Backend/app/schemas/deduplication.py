from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DuplicateEvidence(BaseModel):
    """Structured evidence comparing two potential duplicate leads."""

    model_config = ConfigDict(extra="allow")

    lead_id_a: str
    lead_id_b: str
    phone_a: str | None = None
    phone_b: str | None = None
    email_a: str | None = None
    email_b: str | None = None
    name_a: str | None = None
    name_b: str | None = None
    channel_a: str | None = None
    channel_b: str | None = None
    city_a: str | None = None
    city_b: str | None = None
    model_a: str | None = None
    model_b: str | None = None
    registered_at_a: str | None = None
    registered_at_b: str | None = None
    name_token_similarity: float = 0.0


class DuplicateCandidateRead(BaseModel):
    """Pydantic representation of a persisted lead duplicate candidate."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: str
    primary_lead_id: str
    duplicate_lead_id: str
    confidence_tier: str
    match_score: float
    match_reasons: list[str]
    evidence_payload: dict[str, Any]
    status: str
    decision: str
    decision_by: str | None = None
    decision_notes: str | None = None
    decided_at: datetime | None = None
    detected_at: datetime


class DeduplicationRunSummary(BaseModel):
    """Summary of duplicate detection execution."""

    company_id: str | None = None
    leads_scanned: int = 0
    high_confidence_candidates: int = 0
    possible_matches: int = 0
    total_candidates: int = 0
