from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    sequence_number: int
    sender: str
    text: str
    signal: str
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)


class ConversationSignals(BaseModel):
    client_message_count: int = 0
    client_engagement_ratio: float = 0.0
    mentions_down_payment: bool = False
    mentions_credit: bool = False
    mentions_cash: bool = False
    mentions_visit_or_test_drive: bool = False
    has_objections: bool = False
    model_detected: str | None = None


class ConversationAnalysisResult(BaseModel):
    conversation_id: str
    lead_id: str | None = None
    company_id: str
    purchase_intent_score: float = Field(ge=0.0, le=1.0)
    urgency: Literal["alta", "media", "baja"]
    down_payment_declared: bool | None = None
    payment_method: Literal["contado", "credito", "no_informa"]
    appointment_requested: bool
    model_detected: str | None = None
    signals: ConversationSignals
    evidence: list[EvidenceItem] = Field(default_factory=list)
    analyzed_at: datetime = Field(default_factory=datetime.now)


class ConversationAnalysisResponse(BaseModel):
    id: UUID
    conversation_id: str
    lead_id: str | None
    company_id: str
    purchase_intent_score: float
    urgency: str
    down_payment_declared: bool | None
    payment_method: str | None
    appointment_requested: bool
    model_detected: str | None
    signals: dict
    evidence: list[dict]
    analyzed_at: datetime
