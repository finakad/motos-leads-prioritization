import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.etl.common import LoadResult, RowValidationError, SourceFileError
from app.models.organization import Advisor, Company, SalesPoint


REQUIRED_COLUMNS = {
    "asesor_id",
    "nombre",
    "punto_venta_id",
    "empresa_id",
    "capacidad_diaria_leads",
    "activo",
    "fecha_ingreso",
}


@dataclass(frozen=True)
class AdvisorSourceRow:
    """Normalized representation of one asesores.csv row."""

    advisor_id: str
    full_name: str
    sales_point_id: str
    company_id: str
    daily_lead_capacity: int
    is_active: bool
    hired_at: date


def _required_text(row: dict[str, str], column_name: str, row_number: int) -> str:
    """Returns a required trimmed value or raises a validation error."""

    value = (row.get(column_name) or "").strip()

    if not value:
        raise RowValidationError(
            f"Row {row_number}: column '{column_name}' is required."
        )

    return value


def _parse_boolean(value: str, row_number: int) -> bool:
    """Parses SI/NO values from the source file."""

    normalized_value = value.strip().upper()

    if normalized_value == "SI":
        return True

    if normalized_value == "NO":
        return False

    raise RowValidationError(
        f"Row {row_number}: column 'activo' must contain SI or NO."
    )


def _parse_positive_integer(value: str, row_number: int) -> int:
    """Parses a required positive integer."""

    try:
        parsed_value = int(value.strip())
    except ValueError as exc:
        raise RowValidationError(
            f"Row {row_number}: 'capacidad_diaria_leads' must be an integer."
        ) from exc

    if parsed_value <= 0:
        raise RowValidationError(
            f"Row {row_number}: 'capacidad_diaria_leads' must be greater than zero."
        )

    return parsed_value


def _parse_date(value: str, row_number: int) -> date:
    """Parses dates stored as YYYY-MM-DD."""

    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except ValueError as exc:
        raise RowValidationError(
            f"Row {row_number}: 'fecha_ingreso' must use YYYY-MM-DD format."
        ) from exc


def _normalize_row(row: dict[str, str], row_number: int) -> AdvisorSourceRow:
    """Validates and normalizes one source CSV row."""

    return AdvisorSourceRow(
        advisor_id=_required_text(row, "asesor_id", row_number),
        full_name=_required_text(row, "nombre", row_number),
        sales_point_id=_required_text(row, "punto_venta_id", row_number),
        company_id=_required_text(row, "empresa_id", row_number),
        daily_lead_capacity=_parse_positive_integer(
            _required_text(row, "capacidad_diaria_leads", row_number),
            row_number,
        ),
        is_active=_parse_boolean(
            _required_text(row, "activo", row_number),
            row_number,
        ),
        hired_at=_parse_date(
            _required_text(row, "fecha_ingreso", row_number),
            row_number,
        ),
    )


def read_advisors_csv(file_path: Path) -> tuple[list[AdvisorSourceRow], int]:
    """
    Reads and validates asesores.csv.

    Invalid rows are excluded from the load and reflected later in
    records_rejected. Structural file errors stop the complete execution.
    """

    valid_rows: list[AdvisorSourceRow] = []
    records_received = 0

    source_advisor_ids: set[str] = set()
    source_sales_point_companies: dict[str, str] = {}

    try:
        with file_path.open(encoding="utf-8-sig", newline="") as source_file:
            reader = csv.DictReader(source_file)

            if reader.fieldnames is None:
                raise SourceFileError(
                    "The advisors CSV file does not contain a header."
                )

            source_columns = {
                column.strip()
                for column in reader.fieldnames
                if column is not None
            }
            missing_columns = REQUIRED_COLUMNS - source_columns

            if missing_columns:
                missing_columns_text = ", ".join(sorted(missing_columns))
                raise SourceFileError(
                    "The advisors CSV file is missing required columns: "
                    f"{missing_columns_text}."
                )

            for row_number, row in enumerate(reader, start=2):
                records_received += 1

                try:
                    normalized_row = _normalize_row(row, row_number)

                    if normalized_row.advisor_id in source_advisor_ids:
                        raise RowValidationError(
                            f"Row {row_number}: duplicated asesor_id "
                            f"'{normalized_row.advisor_id}' in source file."
                        )

                    associated_company_id = source_sales_point_companies.get(
                        normalized_row.sales_point_id
                    )

                    if (
                        associated_company_id is not None
                        and associated_company_id != normalized_row.company_id
                    ):
                        raise RowValidationError(
                            f"Row {row_number}: punto_venta_id "
                            f"'{normalized_row.sales_point_id}' is associated with "
                            "multiple companies in the source file."
                        )

                    source_advisor_ids.add(normalized_row.advisor_id)
                    source_sales_point_companies[normalized_row.sales_point_id] = (
                        normalized_row.company_id
                    )
                    valid_rows.append(normalized_row)

                except RowValidationError:
                    # A malformed record must not prevent valid records from loading.
                    continue

    except UnicodeDecodeError as exc:
        raise SourceFileError(
            "The advisors CSV file must be encoded as UTF-8."
        ) from exc

    return valid_rows, records_received


def upsert_advisors(session: Session, rows: list[AdvisorSourceRow]) -> None:
    """
    Creates or updates companies, sales points, and advisors.

    Existing records are queried once and cached in memory. Newly created
    records are added to those caches immediately, preventing duplicate
    INSERT operations when many advisor rows share a company or sales point.
    """

    if not rows:
        return

    company_ids = {row.company_id for row in rows}
    sales_point_ids = {row.sales_point_id for row in rows}
    advisor_ids = {row.advisor_id for row in rows}

    existing_companies = {
        company.id: company
        for company in session.scalars(
            select(Company).where(Company.id.in_(company_ids))
        )
    }

    existing_sales_points = {
        sales_point.id: sales_point
        for sales_point in session.scalars(
            select(SalesPoint).where(SalesPoint.id.in_(sales_point_ids))
        )
    }

    existing_advisors = {
        advisor.id: advisor
        for advisor in session.scalars(
            select(Advisor).where(Advisor.id.in_(advisor_ids))
        )
    }

    for row in rows:
        company = existing_companies.get(row.company_id)

        if company is None:
            company = Company(id=row.company_id)
            session.add(company)
            existing_companies[row.company_id] = company

        sales_point = existing_sales_points.get(row.sales_point_id)

        if sales_point is None:
            sales_point = SalesPoint(
                id=row.sales_point_id,
                company_id=row.company_id,
            )
            session.add(sales_point)
            existing_sales_points[row.sales_point_id] = sales_point

        elif sales_point.company_id != row.company_id:
            raise SourceFileError(
                f"Sales point '{row.sales_point_id}' already belongs to company "
                f"'{sales_point.company_id}', not '{row.company_id}'."
            )

        advisor = existing_advisors.get(row.advisor_id)

        if advisor is None:
            advisor = Advisor(
                id=row.advisor_id,
                full_name=row.full_name,
                sales_point_id=row.sales_point_id,
                company_id=row.company_id,
                daily_lead_capacity=row.daily_lead_capacity,
                is_active=row.is_active,
                hired_at=row.hired_at,
            )
            session.add(advisor)
            existing_advisors[row.advisor_id] = advisor
            continue

        advisor.full_name = row.full_name
        advisor.sales_point_id = row.sales_point_id
        advisor.company_id = row.company_id
        advisor.daily_lead_capacity = row.daily_lead_capacity
        advisor.is_active = row.is_active
        advisor.hired_at = row.hired_at


def load_advisors(session: Session, file_path: Path) -> LoadResult:
    """Loads asesores.csv in one atomic and idempotent transaction."""

    rows, records_received = read_advisors_csv(file_path)
    records_rejected = records_received - len(rows)

    with session.begin():
        upsert_advisors(session, rows)

    return LoadResult(
        records_received=records_received,
        records_processed=len(rows),
        records_rejected=records_rejected,
    )