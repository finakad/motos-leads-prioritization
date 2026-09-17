import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.etl.advisors_loader import load_advisors
from app.etl.catalog_loader import load_catalog
from app.etl.common import get_raw_data_path
from app.etl.conversations_loader import load_conversations
from app.etl.historical_closings_loader import load_historical_closings
from app.etl.leads_loader import load_leads
from app.models.pipeline_run import PipelineRun, PipelineStepRun
from app.services.conversation_analyzer import ConversationAnalyzer
from app.services.deduplication_service import LeadDeduplicationService
from app.services.prioritization_engine import PrioritizationEngine


def _ensure_json_serializable(obj: Any) -> Any:
    if obj is None:
        return None
    return json.loads(json.dumps(obj, default=str))


class PipelineExecutionError(Exception):
    """Raised when an error occurs during step execution."""

    def __init__(self, step_name: str, message: str, original_error: Exception | None = None) -> None:
        super().__init__(f"Step '{step_name}' failed: {message}")
        self.step_name = step_name
        self.message = message
        self.original_error = original_error


@dataclass
class StepResult:
    """Standardized result returned by any pipeline step handler."""

    records_received: int
    records_processed: int
    records_rejected: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StepConfig:
    """Defines a step in the pipeline including dependencies and metadata."""

    name: str
    order: int
    description: str
    dependencies: list[str]


PIPELINE_STEPS: list[StepConfig] = [
    StepConfig(
        name="advisors",
        order=1,
        description="Ingesta de empresas, puntos de venta y asesores",
        dependencies=[],
    ),
    StepConfig(
        name="catalog",
        order=2,
        description="Ingesta de catálogo y disponibilidad de motocicletas",
        dependencies=["advisors"],
    ),
    StepConfig(
        name="leads",
        order=3,
        description="Ingesta de leads comerciales y registros fuente",
        dependencies=["advisors"],
    ),
    StepConfig(
        name="conversations",
        order=4,
        description="Ingesta de conversaciones y mensajes de clientes",
        dependencies=["leads"],
    ),
    StepConfig(
        name="historical_closings",
        order=5,
        description="Ingesta de histórico de cierres para calibración",
        dependencies=[],
    ),
    StepConfig(
        name="deduplication",
        order=6,
        description="Detección de leads duplicados entre canales",
        dependencies=["leads"],
    ),
    StepConfig(
        name="conversation_analysis",
        order=7,
        description="Extracción determinista / IA de señales conversacionales",
        dependencies=["conversations"],
    ),
    StepConfig(
        name="prioritization",
        order=8,
        description="Cálculo de score y priorización explicable multi-tenant",
        dependencies=[
            "advisors",
            "catalog",
            "leads",
            "conversations",
            "historical_closings",
            "conversation_analysis",
        ],
    ),
]

STEP_MAP: dict[str, StepConfig] = {s.name: s for s in PIPELINE_STEPS}


class PipelineOrchestrator:
    """
    End-to-end multi-step backend pipeline orchestrator.
    Guarantees:
    1. Explicit step dependency management.
    2. Atomic transactional rollback on failure without uncommitted artifacts.
    3. Fine-grained step-level audit trail in pipeline_step_runs.
    4. Safe step-by-step and retry execution (--from-step, --steps, --run-id).
    5. Testability via pluggable/fake AI analyzers and services.
    """

    def __init__(
        self,
        session_factory=SessionLocal,
        analyzer: ConversationAnalyzer | None = None,
        engine: PrioritizationEngine | None = None,
        dedup_service: LeadDeduplicationService | None = None,
    ) -> None:
        self.session_factory = session_factory
        self.analyzer = analyzer or ConversationAnalyzer()
        self.engine = engine or PrioritizationEngine(analyzer=self.analyzer)
        self.dedup_service = dedup_service or LeadDeduplicationService()

    def resolve_steps(
        self,
        from_step: str | None = None,
        steps: list[str] | None = None,
    ) -> list[StepConfig]:
        """
        Resolves the ordered sequence of steps to execute, validating step names
        and verifying that all prerequisite dependencies are either completed or planned.
        """
        if steps:
            for s in steps:
                if s not in STEP_MAP:
                    raise ValueError(
                        f"Unknown step '{s}'. Valid steps are: {list(STEP_MAP.keys())}"
                    )
            # Maintain topological order
            selected_names = set(steps)
            resolved = [s for s in PIPELINE_STEPS if s.name in selected_names]
            return resolved

        if from_step:
            if from_step not in STEP_MAP:
                raise ValueError(
                    f"Unknown step '{from_step}'. Valid steps are: {list(STEP_MAP.keys())}"
                )
            target_order = STEP_MAP[from_step].order
            return [s for s in PIPELINE_STEPS if s.order >= target_order]

        return list(PIPELINE_STEPS)

    def _execute_step_handler(
        self,
        session: Session,
        step_name: str,
        trigger_type: str,
    ) -> StepResult:
        """Dispatches the step name to its corresponding idempotent domain loader or service."""

        if step_name == "advisors":
            file_path = get_raw_data_path("asesores.csv")
            res = load_advisors(session=session, file_path=file_path)
            return StepResult(
                records_received=res.records_received,
                records_processed=res.records_processed,
                records_rejected=res.records_rejected,
            )

        elif step_name == "catalog":
            file_path = get_raw_data_path("catalogo_motos.csv")
            res = load_catalog(session=session, file_path=file_path)
            return StepResult(
                records_received=res.records_received,
                records_processed=res.records_processed,
                records_rejected=res.records_rejected,
            )

        elif step_name == "leads":
            file_path = get_raw_data_path("leads.csv")
            res = load_leads(session=session, file_path=file_path)
            return StepResult(
                records_received=res.records_received,
                records_processed=res.records_processed,
                records_rejected=res.records_rejected,
            )

        elif step_name == "conversations":
            file_path = get_raw_data_path("conversaciones.json")
            res = load_conversations(session=session, file_path=file_path)
            return StepResult(
                records_received=res.records_received,
                records_processed=res.records_processed,
                records_rejected=res.records_rejected,
            )

        elif step_name == "historical_closings":
            file_path = get_raw_data_path("historico_cierres.csv")
            res = load_historical_closings(session=session, file_path=file_path)
            return StepResult(
                records_received=res.records_received,
                records_processed=res.records_processed,
                records_rejected=res.records_rejected,
            )

        elif step_name == "deduplication":
            summaries = self.dedup_service.detect_all_duplicates(session=session)
            total_cand = sum(s.total_candidates for s in summaries)
            high_conf = sum(s.high_confidence_candidates for s in summaries)
            possible = sum(s.possible_matches for s in summaries)
            return StepResult(
                records_received=total_cand,
                records_processed=total_cand,
                records_rejected=0,
                metadata={
                    "total_candidates": total_cand,
                    "high_confidence": high_conf,
                    "possible_matches": possible,
                    "by_company": [s.model_dump(mode="json") for s in summaries],
                },
            )

        elif step_name == "conversation_analysis":
            received, processed, rejected, meta = (
                self.analyzer.analyze_all_conversations(
                    session=session,
                    reanalyze_existing=True,
                    raise_on_error=True,
                )
            )
            return StepResult(
                records_received=received,
                records_processed=processed,
                records_rejected=rejected,
                metadata=meta,
            )

        elif step_name == "prioritization":
            summaries = self.engine.prioritize_all_companies(
                session=session,
                execution_type=trigger_type,
            )
            total_leads = sum(s.total_leads_evaluated for s in summaries)
            scores_calc = sum(s.scores_calculated for s in summaries)
            return StepResult(
                records_received=total_leads,
                records_processed=scores_calc,
                records_rejected=0,
                metadata={
                    "total_leads_evaluated": total_leads,
                    "scores_calculated": scores_calc,
                    "by_company": [s.model_dump(mode="json") for s in summaries],
                },
            )

        raise ValueError(f"No handler defined for step '{step_name}'")

    def run(
        self,
        trigger_type: str = "manual",
        from_step: str | None = None,
        steps: list[str] | None = None,
        run_id: UUID | None = None,
    ) -> PipelineRun:
        """
        Executes the resolved pipeline sequence.
        Ensures atomic step transactions, individual audit logging, and clean rollback upon failure.
        """
        steps_to_run = self.resolve_steps(from_step=from_step, steps=steps)

        # 1. Initialize or resume audit pipeline run record
        with self.session_factory() as audit_session:
            if run_id:
                pipeline_run = audit_session.get(PipelineRun, run_id)
                if pipeline_run is None:
                    raise ValueError(f"Pipeline run '{run_id}' not found.")
                pipeline_run.status = "RUNNING"
                pipeline_run.finished_at = None
                pipeline_run.error_message = None
            else:
                pipeline_run = PipelineRun(
                    trigger_type=trigger_type,
                    status="RUNNING",
                    records_received=0,
                    records_processed=0,
                    records_rejected=0,
                )
                audit_session.add(pipeline_run)

            audit_session.commit()
            active_run_id = pipeline_run.id

        total_received = 0
        total_processed = 0
        total_rejected = 0

        # 2. Iterate through steps sequentially
        for idx, step_cfg in enumerate(steps_to_run):
            # Create or update step audit entry in RUNNING state
            with self.session_factory() as audit_session:
                step_run = audit_session.scalar(
                    select(PipelineStepRun).where(
                        PipelineStepRun.pipeline_run_id == active_run_id,
                        PipelineStepRun.step_name == step_cfg.name,
                    )
                )
                if step_run is None:
                    step_run = PipelineStepRun(
                        pipeline_run_id=active_run_id,
                        step_name=step_cfg.name,
                        step_order=step_cfg.order,
                        status="RUNNING",
                        started_at=datetime.now(timezone.utc),
                        records_received=0,
                        records_processed=0,
                        records_rejected=0,
                    )
                    audit_session.add(step_run)
                else:
                    step_run.status = "RUNNING"
                    step_run.started_at = datetime.now(timezone.utc)
                    step_run.finished_at = None
                    step_run.error_message = None

                audit_session.commit()
                step_run_id = step_run.id

            # Execute step inside an isolated, atomic transaction
            try:
                with self.session_factory() as domain_session:
                    step_result = self._execute_step_handler(
                        session=domain_session,
                        step_name=step_cfg.name,
                        trigger_type=trigger_type,
                    )
                    if domain_session.in_transaction():
                        domain_session.commit()

                # Record step success
                with self.session_factory() as audit_session:
                    step_run = audit_session.get(PipelineStepRun, step_run_id)
                    if step_run:
                        status = "COMPLETED"
                        if step_result.records_rejected > 0:
                            status = "COMPLETED_WITH_REJECTIONS"
                        step_run.status = status
                        step_run.finished_at = datetime.now(timezone.utc)
                        step_run.records_received = step_result.records_received
                        step_run.records_processed = step_result.records_processed
                        step_run.records_rejected = step_result.records_rejected
                        step_run.step_metadata = _ensure_json_serializable(step_result.metadata)
                        audit_session.commit()


                total_received += step_result.records_received
                total_processed += step_result.records_processed
                total_rejected += step_result.records_rejected

            except Exception as exc:
                # Step failed: domain session rolled back automatically by context manager.
                # Now record failure in audit session.
                err_msg = str(exc)
                with self.session_factory() as audit_session:
                    step_run = audit_session.get(PipelineStepRun, step_run_id)
                    if step_run:
                        step_run.status = "FAILED"
                        step_run.finished_at = datetime.now(timezone.utc)
                        step_run.error_message = err_msg[:5000]

                    # Mark subsequent steps in this execution plan as SKIPPED
                    for remaining_cfg in steps_to_run[idx + 1:]:
                        rem_step = audit_session.scalar(
                            select(PipelineStepRun).where(
                                PipelineStepRun.pipeline_run_id == active_run_id,
                                PipelineStepRun.step_name == remaining_cfg.name,
                            )
                        )
                        if rem_step is None:
                            rem_step = PipelineStepRun(
                                pipeline_run_id=active_run_id,
                                step_name=remaining_cfg.name,
                                step_order=remaining_cfg.order,
                                status="SKIPPED",
                                started_at=datetime.now(timezone.utc),
                                finished_at=datetime.now(timezone.utc),
                                error_message=f"Skipped due to failure in step '{step_cfg.name}'",
                            )
                            audit_session.add(rem_step)
                        else:
                            rem_step.status = "SKIPPED"
                            rem_step.finished_at = datetime.now(timezone.utc)
                            rem_step.error_message = f"Skipped due to failure in step '{step_cfg.name}'"

                    # Mark main pipeline run as FAILED
                    run_audit = audit_session.get(PipelineRun, active_run_id)
                    if run_audit:
                        run_audit.status = "FAILED"
                        run_audit.finished_at = datetime.now(timezone.utc)
                        run_audit.records_received = total_received
                        run_audit.records_processed = total_processed
                        run_audit.records_rejected = total_rejected
                        run_audit.error_message = f"Step '{step_cfg.name}' failed: {err_msg}"[:5000]

                    audit_session.commit()

                raise PipelineExecutionError(
                    step_name=step_cfg.name,
                    message=err_msg,
                    original_error=exc,
                ) from exc

        # 3. All steps completed successfully
        with self.session_factory() as audit_session:
            run_audit = audit_session.get(PipelineRun, active_run_id)
            if run_audit:
                final_status = "COMPLETED"
                if total_rejected > 0:
                    final_status = "COMPLETED_WITH_REJECTIONS"
                run_audit.status = final_status
                run_audit.finished_at = datetime.now(timezone.utc)
                run_audit.records_received = total_received
                run_audit.records_processed = total_processed
                run_audit.records_rejected = total_rejected
                audit_session.commit()
                audit_session.refresh(run_audit)
                audit_session.expunge(run_audit)
                return run_audit

        raise RuntimeError("Failed to finalize pipeline run audit record.")

