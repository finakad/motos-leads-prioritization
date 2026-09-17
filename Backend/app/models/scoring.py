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
    conversion_probability: Mapped[float | None] = mapped_column(Float, nullable=True)

    factors: Mapped[dict] = mapped_column(JSON, nullable=False)
    evidence: Mapped[list] = mapped_column(JSON, nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)

    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    lead: Mapped["Lead"] = relationship("Lead", back_populates="score")


class ScoringRun(Base):
    """Audit log for batch lead prioritization runs."""

    __tablename__ = "scoring_runs"
    __table_args__ = (
        Index("ix_scoring_runs_company_id", "company_id"),
        Index("ix_scoring_runs_company_started", "company_id", "started_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
    )
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    leads_scored: Mapped[int] = mapped_column(nullable=False)
    high_priority_count: Mapped[int] = mapped_column(nullable=False)
    medium_priority_count: Mapped[int] = mapped_column(nullable=False)
    low_priority_count: Mapped[int] = mapped_column(nullable=False)
    average_score: Mapped[float] = mapped_column(Float, nullable=False)
    execution_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="manual",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="COMPLETED",
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    finished_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class ModelEvaluation(Base):
    """Audit table persisting model calibration and evaluation metrics on historical data."""

    __tablename__ = "model_evaluations"
    __table_args__ = (
        Index("ix_model_evaluations_version", "model_version"),
        Index("ix_model_evaluations_created_at", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    dataset_name: Mapped[str] = mapped_column(String(100), nullable=False)
    evaluation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    sample_size: Mapped[int] = mapped_column(nullable=False)
    train_size: Mapped[int] = mapped_column(nullable=False)
    test_size: Mapped[int] = mapped_column(nullable=False)
    metrics: Mapped[dict] = mapped_column(JSON, nullable=False)
    limitations: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

