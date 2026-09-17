from datetime import datetime
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    JSON,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class HistoricalClosing(Base):
    """Historical lead closing outcome used for statistical calibration."""

    __tablename__ = "historical_closings"
    __table_args__ = (
        ForeignKeyConstraint(
            ["sales_point_id", "company_id"],
            ["sales_points.id", "sales_points.company_id"],
            name="fk_historical_closings_sales_point_company",
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
    quoted_model: Mapped[str | None] = mapped_column(String(150), nullable=True)
    list_price: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    hours_to_first_contact: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    contact_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    down_payment_manifested: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    declared_payment_method: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    requested_appointment: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )
    outcome: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
