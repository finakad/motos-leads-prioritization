from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PipelineRun(Base):
    """Stores the audit record for one pipeline execution."""

    __tablename__ = "pipeline_runs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    trigger_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    records_received: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    records_processed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    records_rejected: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    steps: Mapped[list["PipelineStepRun"]] = relationship(
        "PipelineStepRun",
        back_populates="pipeline_run",
        cascade="all, delete-orphan",
        order_by="PipelineStepRun.step_order",
    )


class PipelineStepRun(Base):
    """Stores the audit record for an individual step within a pipeline execution."""

    __tablename__ = "pipeline_step_runs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    pipeline_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("pipeline_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    records_received: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    records_processed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    records_rejected: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    step_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    pipeline_run: Mapped["PipelineRun"] = relationship(
        "PipelineRun",
        back_populates="steps",
    )