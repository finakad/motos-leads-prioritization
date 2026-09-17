from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.etl.runner import run as run_etl
from app.models.pipeline_run import PipelineRun, PipelineStepRun

router = APIRouter(
    prefix="/etl",
    tags=["ETL Audit & Execution"],
)


class PipelineStepRunResponse(BaseModel):
    id: UUID
    step_name: str
    step_order: int
    status: str
    started_at: datetime
    finished_at: datetime | None
    records_received: int
    records_processed: int
    records_rejected: int
    error_message: str | None
    step_metadata: dict[str, Any] | None = None


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


class PipelineRunDetailResponse(PipelineRunResponse):
    steps: list[PipelineStepRunResponse] = Field(default_factory=list)


class TriggerETLRequest(BaseModel):
    from_step: str | None = Field(
        default=None,
        description="Resume or start from a specific step (e.g. 'conversation_analysis')",
    )
    steps: list[str] | None = Field(
        default=None,
        description="Explicit list of steps to execute in order",
    )


class TriggerETLResponse(BaseModel):
    run_id: UUID
    status: str
    message: str
    records_processed: int
    records_rejected: int


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


@router.get(
    "/runs/{run_id}",
    response_model=PipelineRunDetailResponse,
    summary="Get detailed ETL run audit with all step breakdowns",
)
def get_etl_run_detail(
    run_id: UUID,
    db: Session = Depends(get_db),
) -> PipelineRunDetailResponse:
    """
    Returns full execution details of a specific pipeline run, including each step's
    status, start/end timestamps, records counts, error messages, and metadata.
    """
    pipeline_run = db.scalar(
        select(PipelineRun)
        .where(PipelineRun.id == run_id)
        .options(joinedload(PipelineRun.steps))
    )

    if pipeline_run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline run '{run_id}' was not found.",
        )

    return PipelineRunDetailResponse(
        id=pipeline_run.id,
        trigger_type=pipeline_run.trigger_type,
        status=pipeline_run.status,
        started_at=pipeline_run.started_at,
        finished_at=pipeline_run.finished_at,
        records_received=pipeline_run.records_received,
        records_processed=pipeline_run.records_processed,
        records_rejected=pipeline_run.records_rejected,
        error_message=pipeline_run.error_message,
        steps=[
            PipelineStepRunResponse(
                id=s.id,
                step_name=s.step_name,
                step_order=s.step_order,
                status=s.status,
                started_at=s.started_at,
                finished_at=s.finished_at,
                records_received=s.records_received,
                records_processed=s.records_processed,
                records_rejected=s.records_rejected,
                error_message=s.error_message,
                step_metadata=s.step_metadata,
            )
            for s in pipeline_run.steps
        ],
    )


@router.post(
    "/trigger",
    response_model=TriggerETLResponse,
    summary="Trigger the complete or partial ETL ingestion and processing pipeline",
)
def trigger_etl(
    payload: TriggerETLRequest | None = None,
) -> TriggerETLResponse:
    """
    Triggers the ETL pipeline synchronously and records execution and steps in audit tables.
    Supports optional step filtering and resuming from a failed step.
    """
    from_step = payload.from_step if payload else None
    steps = payload.steps if payload else None

    pipeline_run = run_etl(
        trigger_type="api",
        from_step=from_step,
        steps=steps,
    )

    return TriggerETLResponse(
        run_id=pipeline_run.id,
        status=pipeline_run.status,
        message="Pipeline ETL ejecutado correctamente.",
        records_processed=pipeline_run.records_processed,
        records_rejected=pipeline_run.records_rejected,
    )
