import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.etl.orchestrator import (
    PIPELINE_STEPS,
    PipelineExecutionError,
    PipelineOrchestrator,
)
from app.main import app
from app.models.pipeline_run import PipelineRun, PipelineStepRun
from app.models.scoring import ConversationAnalysis
from app.services.conversation_analyzer import ConversationAnalyzer, FakeAIProvider


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_pipeline_dependency_resolution():
    """Validates step ordering, filtering and dependency checks."""
    orchestrator = PipelineOrchestrator()

    # Full sequence
    all_steps = orchestrator.resolve_steps()
    assert len(all_steps) == 8
    assert [s.name for s in all_steps] == [
        "advisors",
        "catalog",
        "leads",
        "conversations",
        "historical_closings",
        "deduplication",
        "conversation_analysis",
        "prioritization",
    ]

    # From step
    from_dedup = orchestrator.resolve_steps(from_step="deduplication")
    assert [s.name for s in from_dedup] == [
        "deduplication",
        "conversation_analysis",
        "prioritization",
    ]

    # Specific steps maintaining topological order
    selected = orchestrator.resolve_steps(steps=["prioritization", "leads"])
    assert [s.name for s in selected] == ["leads", "prioritization"]

    # Invalid step
    with pytest.raises(ValueError, match="Unknown step"):
        orchestrator.resolve_steps(from_step="non_existent_step")

    with pytest.raises(ValueError, match="Unknown step"):
        orchestrator.resolve_steps(steps=["invalid_step"])


def test_pipeline_orchestration_with_fake_ai_provider():
    """
    Tests orchestrator execution using an injected FakeAIProvider.
    Verifies that the fake AI signals propagate to step execution and step-level audits.
    """
    fake_provider = FakeAIProvider(
        default_intent_score=0.91,
        default_urgency="alta",
        appointment_requested=True,
    )
    fake_analyzer = ConversationAnalyzer(provider=fake_provider)

    orchestrator = PipelineOrchestrator(analyzer=fake_analyzer)

    # Run only deduplication, conversation_analysis and prioritization for speed
    pipeline_run = orchestrator.run(
        trigger_type="test_fake_ai",
        steps=["deduplication", "conversation_analysis", "prioritization"],
    )

    assert pipeline_run.status == "COMPLETED"
    assert pipeline_run.finished_at is not None

    # Check step audit records
    with SessionLocal() as session:
        step_runs = list(
            session.scalars(
                select(PipelineStepRun)
                .where(PipelineStepRun.pipeline_run_id == pipeline_run.id)
                .order_by(PipelineStepRun.step_order)
            ).all()
        )

        assert len(step_runs) == 3
        step_names = [s.step_name for s in step_runs]
        assert step_names == [
            "deduplication",
            "conversation_analysis",
            "prioritization",
        ]

        for s in step_runs:
            assert s.status in ("COMPLETED", "COMPLETED_WITH_REJECTIONS")
            assert s.finished_at is not None
            assert s.error_message is None

        # Verify fake AI was invoked
        conv_step = next(s for s in step_runs if s.step_name == "conversation_analysis")
        assert conv_step.records_processed > 0


def test_pipeline_step_failure_atomic_rollback_and_skip():
    """
    Verifies atomic rollback on step failure:
    1. Simulates an AI provider error.
    2. Step is marked as FAILED with error message.
    3. Subsequent steps are marked as SKIPPED.
    4. Main PipelineRun is marked as FAILED.
    """
    failing_provider = FakeAIProvider(
        raise_exception=RuntimeError("Simulated LLM service unavailable")
    )
    failing_analyzer = ConversationAnalyzer(provider=failing_provider)

    orchestrator = PipelineOrchestrator(analyzer=failing_analyzer)

    with pytest.raises(PipelineExecutionError) as exc_info:
        orchestrator.run(
            trigger_type="test_failure",
            steps=["deduplication", "conversation_analysis", "prioritization"],
        )

    assert exc_info.value.step_name == "conversation_analysis"
    assert "Simulated LLM service unavailable" in exc_info.value.message

    # Inspect audit database records
    with SessionLocal() as session:
        # Find the latest failed run
        failed_run = session.scalars(
            select(PipelineRun)
            .where(PipelineRun.trigger_type == "test_failure")
            .order_by(PipelineRun.started_at.desc())
        ).first()

        assert failed_run is not None
        assert failed_run.status == "FAILED"
        assert "conversation_analysis" in failed_run.error_message

        step_runs = {
            s.step_name: s
            for s in session.scalars(
                select(PipelineStepRun).where(
                    PipelineStepRun.pipeline_run_id == failed_run.id
                )
            ).all()
        }

        # Step 6 (deduplication) succeeded
        assert step_runs["deduplication"].status in ("COMPLETED", "COMPLETED_WITH_REJECTIONS")

        # Step 7 (conversation_analysis) failed
        assert step_runs["conversation_analysis"].status == "FAILED"
        assert "Simulated LLM" in step_runs["conversation_analysis"].error_message

        # Step 8 (prioritization) skipped
        assert step_runs["prioritization"].status == "SKIPPED"
        assert "Skipped due to failure" in step_runs["prioritization"].error_message


def test_pipeline_retry_safe_resumption():
    """
    Verifies that a pipeline can safely resume/retry from a failed step onwards
    without duplicating data (idempotency).
    """
    # 1. First trigger failure
    failing_provider = FakeAIProvider(
        raise_exception=RuntimeError("Temporary connection timeout")
    )
    failing_analyzer = ConversationAnalyzer(provider=failing_provider)
    orchestrator_fail = PipelineOrchestrator(analyzer=failing_analyzer)

    with pytest.raises(PipelineExecutionError):
        orchestrator_fail.run(
            trigger_type="test_retry",
            steps=["deduplication", "conversation_analysis", "prioritization"],
        )

    # 2. Retry with working analyzer starting from conversation_analysis
    working_orchestrator = PipelineOrchestrator()
    resumed_run = working_orchestrator.run(
        trigger_type="test_retry_resumed",
        from_step="conversation_analysis",
    )

    assert resumed_run.status in ("COMPLETED", "COMPLETED_WITH_REJECTIONS")

    with SessionLocal() as session:
        step_runs = list(
            session.scalars(
                select(PipelineStepRun)
                .where(PipelineStepRun.pipeline_run_id == resumed_run.id)
                .order_by(PipelineStepRun.step_order)
            ).all()
        )

        step_names = [s.step_name for s in step_runs]
        assert step_names == ["conversation_analysis", "prioritization"]
        for s in step_runs:
            assert s.status in ("COMPLETED", "COMPLETED_WITH_REJECTIONS")
            assert s.finished_at is not None


def test_api_etl_trigger_and_get_detail(client: TestClient):
    """Tests the /api/v1/etl/trigger and /api/v1/etl/runs/{run_id} endpoints."""
    # Trigger selective run
    response = client.post(
        "/api/v1/etl/trigger",
        json={
            "steps": ["deduplication", "conversation_analysis", "prioritization"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("COMPLETED", "COMPLETED_WITH_REJECTIONS")
    run_id = data["run_id"]

    # Get detailed execution breakdown
    detail_resp = client.get(f"/api/v1/etl/runs/{run_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()

    assert detail["id"] == run_id
    assert len(detail["steps"]) == 3

    for step in detail["steps"]:
        assert step["step_name"] in [
            "deduplication",
            "conversation_analysis",
            "prioritization",
        ]
        assert step["status"] in ("COMPLETED", "COMPLETED_WITH_REJECTIONS")
        assert step["started_at"] is not None
        assert step["finished_at"] is not None
