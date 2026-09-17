from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Lead(Base):
    __tablename__ = "leads"
    __table_args__ = (
        ForeignKeyConstraint(
            ["sales_point_id", "company_id"],
            ["sales_points.id", "sales_points.company_id"],
            name="fk_leads_sales_point_company",
            ondelete="RESTRICT",
        ),
    )

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sales_point_id: Mapped[str] = mapped_column(String(20), nullable=False)

    registered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    channel: Mapped[str | None] = mapped_column(String(50), nullable=True)
    customer_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    phone_raw: Mapped[str | None] = mapped_column(String(50), nullable=True)
    phone_normalized: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model_interest_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    management_status: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    first_contact_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    campaign: Mapped[str | None] = mapped_column(String(200), nullable=True)

    source_records: Mapped[list["LeadSourceRecord"]] = relationship(
        back_populates="lead",
        cascade="all, delete-orphan",
    )
    score: Mapped["LeadScore | None"] = relationship(
        "LeadScore",
        back_populates="lead",
        uselist=False,
        cascade="all, delete-orphan",
    )
    conversation_analysis: Mapped["ConversationAnalysis | None"] = relationship(
        "ConversationAnalysis",
        back_populates="lead",
        uselist=False,
    )


class LeadSourceRecord(Base):
    __tablename__ = "lead_source_records"
    __table_args__ = (
        UniqueConstraint(
            "source_file",
            "source_row_number",
            name="uq_lead_source_records_file_row",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    lead_id: Mapped[str | None] = mapped_column(
        ForeignKey("leads.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    source_file: Mapped[str] = mapped_column(String(255), nullable=False)
    source_row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    source_lead_id: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False)

    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    lead: Mapped[Lead | None] = relationship(back_populates="source_records")