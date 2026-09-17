from datetime import date

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)

    sales_points: Mapped[list["SalesPoint"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )

    advisors: Mapped[list["Advisor"]] = relationship(
        back_populates="company",
        overlaps="sales_point",
    )


class SalesPoint(Base):
    __tablename__ = "sales_points"
    __table_args__ = (
        UniqueConstraint(
            "id",
            "company_id",
            name="uq_sales_points_id_company",
        ),
    )

    id: Mapped[str] = mapped_column(String(20), primary_key=True)

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    company: Mapped["Company"] = relationship(back_populates="sales_points")

    advisors: Mapped[list["Advisor"]] = relationship(
        back_populates="sales_point",
        overlaps="company,advisors",
    )


class Advisor(Base):
    __tablename__ = "advisors"
    __table_args__ = (
        CheckConstraint(
            "daily_lead_capacity > 0",
            name="ck_advisors_daily_lead_capacity_positive",
        ),
        ForeignKeyConstraint(
            ["sales_point_id", "company_id"],
            ["sales_points.id", "sales_points.company_id"],
            name="fk_advisors_sales_point_company",
            ondelete="RESTRICT",
        ),
    )

    id: Mapped[str] = mapped_column(String(20), primary_key=True)

    full_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    sales_point_id: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    daily_lead_capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    hired_at: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    company: Mapped["Company"] = relationship(
        back_populates="advisors",
        overlaps="advisors,sales_point",
    )

    sales_point: Mapped["SalesPoint"] = relationship(
        back_populates="advisors",
        primaryjoin=(
            "and_(Advisor.sales_point_id == SalesPoint.id, "
            "Advisor.company_id == SalesPoint.company_id)"
        ),
        overlaps="advisors,company",
    )