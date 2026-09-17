from datetime import datetime, timezone
from uuid import UUID

from app.core.database import SessionLocal
from app.etl.advisors_loader import load_advisors
from app.etl.catalog_loader import load_catalog
from app.etl.common import LoadResult, get_raw_data_path
from app.etl.conversations_loader import load_conversations
from app.etl.leads_loader import load_leads
from app.models.pipeline_run import PipelineRun


def create_pipeline_run() -> UUID:
    """Creates an audit record for a new pipeline execution."""

    with SessionLocal() as session:
        pipeline_run = PipelineRun(
            trigger_type="manual",
            status="RUNNING",
            records_received=0,
            records_processed=0,
            records_rejected=0,
        )

        session.add(pipeline_run)
        session.commit()

        return pipeline_run.id


def complete_pipeline_run(
    pipeline_run_id: UUID,
    records_received: int,
    records_processed: int,
    records_rejected: int,
) -> None:
    """Marks an ETL execution as completed."""

    status = "COMPLETED"

    if records_rejected > 0:
        status = "COMPLETED_WITH_REJECTIONS"

    with SessionLocal() as session:
        pipeline_run = session.get(PipelineRun, pipeline_run_id)

        if pipeline_run is None:
            raise RuntimeError("Pipeline audit record was not found.")

        pipeline_run.status = status
        pipeline_run.finished_at = datetime.now(timezone.utc)
        pipeline_run.records_received = records_received
        pipeline_run.records_processed = records_processed
        pipeline_run.records_rejected = records_rejected

        session.commit()


def fail_pipeline_run(
    pipeline_run_id: UUID,
    error_message: str,
) -> None:
    """Marks an ETL execution as failed."""

    with SessionLocal() as session:
        pipeline_run = session.get(PipelineRun, pipeline_run_id)

        if pipeline_run is None:
            raise RuntimeError("Pipeline audit record was not found.")

        pipeline_run.status = "FAILED"
        pipeline_run.finished_at = datetime.now(timezone.utc)
        pipeline_run.error_message = error_message[:5000]

        session.commit()


def _combine_results(*results: LoadResult) -> LoadResult:
    """Combines results from all loaders executed in one pipeline run."""

    return LoadResult(
        records_received=sum(result.records_received for result in results),
        records_processed=sum(result.records_processed for result in results),
        records_rejected=sum(result.records_rejected for result in results),
    )


def run() -> None:
    """Runs the advisors, catalog, and leads ETL loaders."""

    pipeline_run_id = create_pipeline_run()

    try:
        advisors_file_path = get_raw_data_path("asesores.csv")
        catalog_file_path = get_raw_data_path("catalogo_motos.csv")
        leads_file_path = get_raw_data_path("leads.csv")
        conversations_file_path = get_raw_data_path("conversaciones.json")

        with SessionLocal() as session:
            advisors_result = load_advisors(
                session=session,
                file_path=advisors_file_path,
            )

        with SessionLocal() as session:
            catalog_result = load_catalog(
                session=session,
                file_path=catalog_file_path,
            )

        with SessionLocal() as session:
            leads_result = load_leads(
                session=session,
                file_path=leads_file_path,
            )

        with SessionLocal() as session:
            conversations_result = load_conversations(
                session=session,
                file_path=conversations_file_path,
            )

        total_result = _combine_results(
            advisors_result,
            catalog_result,
            leads_result,
            conversations_result,
        )

        complete_pipeline_run(
            pipeline_run_id=pipeline_run_id,
            records_received=total_result.records_received,
            records_processed=total_result.records_processed,
            records_rejected=total_result.records_rejected,
        )

        print("ETL completed successfully.")
        print(
            "Advisors - "
            f"received: {advisors_result.records_received}, "
            f"processed: {advisors_result.records_processed}, "
            f"rejected: {advisors_result.records_rejected}"
        )
        print(
            "Catalog - "
            f"received: {catalog_result.records_received}, "
            f"processed: {catalog_result.records_processed}, "
            f"rejected: {catalog_result.records_rejected}"
        )
        print(
            "Leads - "
            f"received: {leads_result.records_received}, "
            f"processed: {leads_result.records_processed}, "
            f"rejected: {leads_result.records_rejected}"
        )
        print(
            "Conversations - "
            f"received: {conversations_result.records_received}, "
            f"processed: {conversations_result.records_processed}, "
            f"rejected: {conversations_result.records_rejected}"
        )
        print(
            "Total - "
            f"received: {total_result.records_received}, "
            f"processed: {total_result.records_processed}, "
            f"rejected: {total_result.records_rejected}"
        )

    except Exception as exc:
        fail_pipeline_run(
            pipeline_run_id=pipeline_run_id,
            error_message=str(exc),
        )

        print(f"ETL failed: {exc}")
        raise


if __name__ == "__main__":
    run()