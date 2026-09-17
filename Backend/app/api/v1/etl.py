from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.etl.runner import run as run_etl
from app.models.pipeline_run import PipelineRun

router = APIRouter(
    prefix="/etl",
    tags=["ETL Audit & Execution"],
)


class PipelineRunResponse(BaseModel):
    id: UUID
    trigger_type: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    records_received: int
    records_processed: int
    records_rejected: int
    error_message: str | None


class TriggerETLResponse(BaseModel):
    status: str
    message: str


@router.get(
    "/runs",
    response_model=list[PipelineRunResponse],
    summary="List ETL execution audit records",
)
def list_etl_runs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[PipelineRunResponse]:
    """
    Returns pipeline audit history ordered by started_at descending.
    """
    runs = db.scalars(
        select(PipelineRun)
        .order_by(desc(PipelineRun.started_at))
        .limit(limit)
        .offset(offset)
    ).all()

    return [
        PipelineRunResponse(
            id=r.id,
            trigger_type=r.trigger_type,
            status=r.status,
            started_at=r.started_at,
            finished_at=r.finished_at,
            records_received=r.records_received,
            records_processed=r.records_processed,
            records_rejected=r.records_rejected,
            error_message=r.error_message,
        )
        for r in runs
    ]


@router.post(
    "/trigger",
    response_model=TriggerETLResponse,
    summary="Trigger the complete ETL ingestion pipeline",
)
def trigger_etl() -> TriggerETLResponse:
    """
    Triggers the ETL pipeline synchronously and records execution in pipeline_runs.
    """
    run_etl()
    return TriggerETLResponse(
        status="success",
        message="Pipeline ETL ejecutado correctamente.",
    )
