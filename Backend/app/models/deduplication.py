from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class LeadDuplicateCandidate(Base):
    """
    Persisted auditable record of a potential cross-channel duplicate lead pair
    within the same company. Never merges or deletes source rows.
    """

    __tablename__ = "lead_duplicate_candidates"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "primary_lead_id",
            "duplicate_lead_id",
            name="uq_lead_duplicates_pair",
        ),
        CheckConstraint(
            "primary_lead_id <> duplicate_lead_id",
            name="ck_lead_duplicates_distinct",
        ),
        Index("ix_lead_duplicates_company_status", "company_id", "status"),
        Index(
            "ix_lead_duplicates_confidence",
            "company_id",
            "confidence_tier",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    primary_lead_id: Mapped[str] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    duplicate_lead_id: Mapped[str] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    confidence_tier: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )  # ALTA_CONFIANZA, POSIBLE_COINCIDENCIA
    match_score: Mapped[float] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )  # 0.0000 - 1.0000
    match_reasons: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )  # e.g. ["SAME_PHONE_E164", "SAME_CITY"]
    evidence_payload: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )  # Detailed comparison dict

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="SUGERIDO",
        index=True,
    )  # SUGERIDO, PENDIENTE_REVISION, CONFIRMADO, RECHAZADO, CONSOLIDADO
    decision: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="PENDIENTE",
    )  # PENDIENTE, FUSIONAR_VIRTUAL, MANTENER_SEPARADOS
    decision_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    decision_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    primary_lead: Mapped["Lead"] = relationship(
        "Lead",
        foreign_keys=[primary_lead_id],
    )
    duplicate_lead: Mapped["Lead"] = relationship(
        "Lead",
        foreign_keys=[duplicate_lead_id],
    )
    company: Mapped["Company"] = relationship(
        "Company",
        foreign_keys=[company_id],
    )
