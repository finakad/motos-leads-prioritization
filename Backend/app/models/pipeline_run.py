from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

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