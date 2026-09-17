import argparse
import sys
from uuid import UUID

from app.etl.orchestrator import (
    PIPELINE_STEPS,
    PipelineExecutionError,
    PipelineOrchestrator,
)
from app.models.pipeline_run import PipelineRun
from app.services.conversation_analyzer import ConversationAnalyzer
from app.services.prioritization_engine import PrioritizationEngine


def run(
    trigger_type: str = "manual",
    from_step: str | None = None,
    steps: list[str] | None = None,
    run_id: UUID | None = None,
    analyzer: ConversationAnalyzer | None = None,
    engine: PrioritizationEngine | None = None,
) -> PipelineRun:
    """
    Main programmatic entrypoint for executing the end-to-end data and processing pipeline.
    Sequence:
    advisors -> catalog -> leads -> conversations -> historical_closings
    -> deduplication -> conversation_analysis -> prioritization
    """
    orchestrator = PipelineOrchestrator(
        analyzer=analyzer,
        engine=engine,
    )
    return orchestrator.run(
        trigger_type=trigger_type,
        from_step=from_step,
        steps=steps,
        run_id=run_id,
    )


def print_steps_table() -> None:
    """Prints the registered pipeline steps and their explicit dependencies."""
    print("\nAvailable Pipeline Steps:")
    print("-" * 75)
    print(f"{'#':<3} {'Step Name':<24} {'Dependencies':<25} {'Description'}")
    print("-" * 75)
    for s in PIPELINE_STEPS:
        deps = ", ".join(s.dependencies) if s.dependencies else "(none)"
        print(f"{s.order:<3} {s.name:<24} {deps:<25} {s.description}")
    print("-" * 75)


def main() -> None:
    """CLI entrypoint for standalone pipeline execution and operations."""
    parser = argparse.ArgumentParser(
        description="End-to-End Leads Prioritization Pipeline Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Execute full pipeline from start to finish
  python -m app.etl.runner

  # Resume/retry execution from failed step onwards
  python -m app.etl.runner --from-step conversation_analysis

  # Run only specific steps
  python -m app.etl.runner --steps deduplication,conversation_analysis,prioritization

  # Resume a previous pipeline run by ID
  python -m app.etl.runner --run-id e824982a-579e-4b6e-a3ec-8bb9d5d59a22 --from-step prioritization

  # List all steps and dependencies
  python -m app.etl.runner --list-steps
        """,
    )

    parser.add_argument(
        "--from-step",
        dest="from_step",
        type=str,
        default=None,
        help="Start execution from this step onwards (useful for retrying after a failure)",
    )
    parser.add_argument(
        "--steps",
        dest="steps",
        type=str,
        default=None,
        help="Comma-separated list of specific step names to execute",
    )
    parser.add_argument(
        "--run-id",
        dest="run_id",
        type=str,
        default=None,
        help="UUID of an existing pipeline run to resume / update",
    )
    parser.add_argument(
        "--trigger-type",
        dest="trigger_type",
        type=str,
        default="manual",
        help="Audit trigger source tag (manual, scheduled, cli, api). Default: manual",
    )
    parser.add_argument(
        "--list-steps",
        dest="list_steps",
        action="store_true",
        help="Print the configured steps and their dependency chain",
    )

    args = parser.parse_args()

    if args.list_steps:
        print_steps_table()
        sys.exit(0)

    selected_steps: list[str] | None = None
    if args.steps:
        selected_steps = [s.strip() for s in args.steps.split(",") if s.strip()]

    parsed_run_id: UUID | None = None
    if args.run_id:
        try:
            parsed_run_id = UUID(args.run_id)
        except ValueError:
            print(f"Error: Invalid UUID format for --run-id '{args.run_id}'", file=sys.stderr)
            sys.exit(1)

    print("=" * 70)
    print("STARTING MOTORCYCLE LEADS PIPELINE ORCHESTRATION")
    print(f"Trigger Type: {args.trigger_type}")
    if args.from_step:
        print(f"From Step:    {args.from_step}")
    if selected_steps:
        print(f"Steps:        {', '.join(selected_steps)}")
    if parsed_run_id:
        print(f"Run ID:       {parsed_run_id}")
    print("=" * 70)

    try:
        pipeline_run = run(
            trigger_type=args.trigger_type,
            from_step=args.from_step,
            steps=selected_steps,
            run_id=parsed_run_id,
        )

        print("\nPIPELINE EXECUTION FINISHED SUCCESSFULLY")
        print(f"Run ID:            {pipeline_run.id}")
        print(f"Status:            {pipeline_run.status}")
        print(f"Records Received:  {pipeline_run.records_received}")
        print(f"Records Processed: {pipeline_run.records_processed}")
        print(f"Records Rejected:  {pipeline_run.records_rejected}")
        print(f"Started At:        {pipeline_run.started_at}")
        print(f"Finished At:       {pipeline_run.finished_at}")
        print("=" * 70)
        sys.exit(0)

    except PipelineExecutionError as exc:
        print(f"\n[PIPELINE FAILED] in step '{exc.step_name}'", file=sys.stderr)
        print(f"Details: {exc.message}", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(2)

    except Exception as exc:
        print(f"\n[CRITICAL ERROR] Pipeline execution halted: {exc}", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()