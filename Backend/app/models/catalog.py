from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Motorcycle(Base):
    __tablename__ = "motorcycles"
    __table_args__ = (
        CheckConstraint(
            "engine_displacement_cc > 0",
            name="ck_motorcycles_engine_displacement_positive",
        ),
        CheckConstraint(
            "list_price > 0",
            name="ck_motorcycles_list_price_positive",
        ),
        CheckConstraint(
            "reported_available_units >= 0",
            name="ck_motorcycles_reported_available_units_non_negative",
        ),
    )

    sku: Mapped[str] = mapped_column(String(20), primary_key=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    line: Mapped[str] = mapped_column(String(150), nullable=False)
    engine_displacement_cc: Mapped[int] = mapped_column(Integer, nullable=False)
    segment: Mapped[str] = mapped_column(String(100), nullable=False)
    list_price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reported_available_units: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    availability_records: Mapped[list["MotorcycleAvailability"]] = relationship(
        back_populates="motorcycle",
        cascade="all, delete-orphan",
    )


class MotorcycleAvailability(Base):
    __tablename__ = "motorcycle_availability"

    motorcycle_sku: Mapped[str] = mapped_column(
        ForeignKey("motorcycles.sku", ondelete="RESTRICT"),
        primary_key=True,
    )
    sales_point_id: Mapped[str] = mapped_column(
        ForeignKey("sales_points.id", ondelete="RESTRICT"),
        primary_key=True,
    )

    motorcycle: Mapped["Motorcycle"] = relationship(
        back_populates="availability_records",
    )