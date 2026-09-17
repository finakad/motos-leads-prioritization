from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    JSON,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ConversationAnalysis(Base):
    """Structured and verifiable AI analysis of a WhatsApp lead conversation."""

    __tablename__ = "conversation_analyses"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    lead_id: Mapped[str | None] = mapped_column(
        ForeignKey("leads.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    purchase_intent_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    urgency: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="baja",
    )
    down_payment_declared: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )
    payment_method: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    appointment_requested: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    model_detected: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    signals: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    evidence: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="analysis",
    )
    lead: Mapped["Lead | None"] = relationship(
        "Lead",
        back_populates="conversation_analysis",
    )


class LeadScore(Base):
    """Stores explainable multi-tenant prioritization score for a lead."""

    __tablename__ = "lead_scores"
    __table_args__ = (
        UniqueConstraint("lead_id", name="uq_lead_scores_lead_id"),
        Index("ix_lead_scores_company_score", "company_id", "score"),
        Index("ix_lead_scores_company_tier", "company_id", "priority_tier"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    lead_id: Mapped[str] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    score: Mapped[float] = mapped_column(Float, nullable=False)
    priority_tier: Mapped[str] = mapped_column(String(20), nullable=False)

    factors: Mapped[dict] = mapped_column(JSON, nullable=False)
    evidence: Mapped[list] = mapped_column(JSON, nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)

    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    lead: Mapped["Lead"] = relationship("Lead", back_populates="score")
