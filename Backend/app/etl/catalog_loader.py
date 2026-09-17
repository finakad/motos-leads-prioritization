import csv
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.etl.common import LoadResult, RowValidationError, SourceFileError
from app.models.catalog import Motorcycle, MotorcycleAvailability
from app.models.organization import SalesPoint


REQUIRED_COLUMNS = {
    "sku",
    "marca",
    "linea",
    "cilindraje",
    "segmento",
    "precio_lista",
    "puntos_venta_disponibles",
    "unidades_disponibles",
}


@dataclass(frozen=True)
class MotorcycleSourceRow:
    """Normalized representation of one catalogo_motos.csv row."""

    sku: str
    brand: str
    line: str
    engine_displacement_cc: int
    segment: str
    list_price: int
    sales_point_ids: tuple[str, ...]
    reported_available_units: int


def _required_text(row: dict[str, str], column_name: str, row_number: int) -> str:
    """Returns a required trimmed text value."""

    value = (row.get(column_name) or "").strip()

    if not value:
        raise RowValidationError(
            f"Row {row_number}: column '{column_name}' is required."
        )

    return value


def _parse_positive_integer(
    value: str,
    column_name: str,
    row_number: int,
) -> int:
    """Parses a positive integer source value."""

    try:
        parsed_value = int(value.strip())
    except ValueError as exc:
        raise RowValidationError(
            f"Row {row_number}: column '{column_name}' must be an integer."
        ) from exc

    if parsed_value <= 0:
        raise RowValidationError(
            f"Row {row_number}: column '{column_name}' must be greater than zero."
        )

    return parsed_value


def _parse_non_negative_integer(
    value: str,
    column_name: str,
    row_number: int,
) -> int:
    """Parses a non-negative integer source value."""

    try:
        parsed_value = int(value.strip())
    except ValueError as exc:
        raise RowValidationError(
            f"Row {row_number}: column '{column_name}' must be an integer."
        ) from exc

    if parsed_value < 0:
        raise RowValidationError(
            f"Row {row_number}: column '{column_name}' cannot be negative."
        )

    return parsed_value


def _parse_sales_point_ids(value: str, row_number: int) -> tuple[str, ...]:
    """Parses the pipe-separated sales point identifiers."""

    raw_sales_point_ids = [
        sales_point_id.strip()
        for sales_point_id in value.split("|")
        if sales_point_id.strip()
    ]

    if not raw_sales_point_ids:
        raise RowValidationError(
            f"Row {row_number}: column 'puntos_venta_disponibles' is required."
        )

    unique_sales_point_ids = tuple(dict.fromkeys(raw_sales_point_ids))

    if len(unique_sales_point_ids) != len(raw_sales_point_ids):
        raise RowValidationError(
            f"Row {row_number}: column 'puntos_venta_disponibles' contains "
            "duplicated sales point identifiers."
        )

    return unique_sales_point_ids


def _normalize_row(row: dict[str, str], row_number: int) -> MotorcycleSourceRow:
    """Validates and normalizes one source CSV row."""

    return MotorcycleSourceRow(
        sku=_required_text(row, "sku", row_number),
        brand=_required_text(row, "marca", row_number),
        line=_required_text(row, "linea", row_number),
        engine_displacement_cc=_parse_positive_integer(
            _required_text(row, "cilindraje", row_number),
            "cilindraje",
            row_number,
        ),
        segment=_required_text(row, "segmento", row_number),
        list_price=_parse_positive_integer(
            _required_text(row, "precio_lista", row_number),
            "precio_lista",
            row_number,
        ),
        sales_point_ids=_parse_sales_point_ids(
            _required_text(row, "puntos_venta_disponibles", row_number),
            row_number,
        ),
        reported_available_units=_parse_non_negative_integer(
            _required_text(row, "unidades_disponibles", row_number),
            "unidades_disponibles",
            row_number,
        ),
    )


def read_catalog_csv(file_path: Path) -> tuple[list[MotorcycleSourceRow], int]:
    """
    Reads and validates catalogo_motos.csv.

    Invalid rows are excluded and included in records_rejected. File-level
    errors, such as missing required columns, stop the execution.
    """

    valid_rows: list[MotorcycleSourceRow] = []
    records_received = 0
    source_skus: set[str] = set()

    try:
        with file_path.open(encoding="utf-8-sig", newline="") as source_file:
            reader = csv.DictReader(source_file)

            if reader.fieldnames is None:
                raise SourceFileError(
                    "The motorcycle catalog CSV file does not contain a header."
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
                    "The motorcycle catalog CSV file is missing required columns: "
                    f"{missing_columns_text}."
                )

            for row_number, row in enumerate(reader, start=2):
                records_received += 1

                try:
                    normalized_row = _normalize_row(row, row_number)

                    if normalized_row.sku in source_skus:
                        raise RowValidationError(
                            f"Row {row_number}: duplicated sku "
                            f"'{normalized_row.sku}' in source file."
                        )

                    source_skus.add(normalized_row.sku)
                    valid_rows.append(normalized_row)

                except RowValidationError:
                    continue

    except UnicodeDecodeError as exc:
        raise SourceFileError(
            "The motorcycle catalog CSV file must be encoded as UTF-8."
        ) from exc

    return valid_rows, records_received


def _validate_sales_points(
    session: Session,
    rows: list[MotorcycleSourceRow],
) -> None:
    """Ensures every sales point referenced by the catalog exists."""

    source_sales_point_ids = {
        sales_point_id
        for row in rows
        for sales_point_id in row.sales_point_ids
    }

    if not source_sales_point_ids:
        return

    existing_sales_point_ids = set(
        session.scalars(
            select(SalesPoint.id).where(
                SalesPoint.id.in_(source_sales_point_ids)
            )
        )
    )

    missing_sales_point_ids = source_sales_point_ids - existing_sales_point_ids

    if missing_sales_point_ids:
        missing_ids_text = ", ".join(sorted(missing_sales_point_ids))
        raise SourceFileError(
            "The motorcycle catalog references sales points that do not exist "
            f"in the database: {missing_ids_text}."
        )


def upsert_catalog(session: Session, rows: list[MotorcycleSourceRow]) -> None:
    """
    Creates or updates motorcycles and their sales-point availability.

    The availability records are synchronized for each SKU: associations no
    longer present in the source file are removed, and new ones are added.
    """

    if not rows:
        return

    _validate_sales_points(session, rows)

    source_skus = {row.sku for row in rows}

    existing_motorcycles = {
        motorcycle.sku: motorcycle
        for motorcycle in session.scalars(
            select(Motorcycle).where(Motorcycle.sku.in_(source_skus))
        )
    }

    existing_availability_records = {
        (availability.motorcycle_sku, availability.sales_point_id)
        for availability in session.scalars(
            select(MotorcycleAvailability).where(
                MotorcycleAvailability.motorcycle_sku.in_(source_skus)
            )
        )
    }

    source_availability_records = {
        (row.sku, sales_point_id)
        for row in rows
        for sales_point_id in row.sales_point_ids
    }

    for row in rows:
        motorcycle = existing_motorcycles.get(row.sku)

        if motorcycle is None:
            motorcycle = Motorcycle(
                sku=row.sku,
                brand=row.brand,
                line=row.line,
                engine_displacement_cc=row.engine_displacement_cc,
                segment=row.segment,
                list_price=row.list_price,
                reported_available_units=row.reported_available_units,
            )
            session.add(motorcycle)
            existing_motorcycles[row.sku] = motorcycle
            continue

        motorcycle.brand = row.brand
        motorcycle.line = row.line
        motorcycle.engine_displacement_cc = row.engine_displacement_cc
        motorcycle.segment = row.segment
        motorcycle.list_price = row.list_price
        motorcycle.reported_available_units = row.reported_available_units

    records_to_add = source_availability_records - existing_availability_records

    for motorcycle_sku, sales_point_id in records_to_add:
        session.add(
            MotorcycleAvailability(
                motorcycle_sku=motorcycle_sku,
                sales_point_id=sales_point_id,
            )
        )

    records_to_remove = (
        existing_availability_records - source_availability_records
    )

    for motorcycle_sku, sales_point_id in records_to_remove:
        availability = session.get(
            MotorcycleAvailability,
            {
                "motorcycle_sku": motorcycle_sku,
                "sales_point_id": sales_point_id,
            },
        )

        if availability is not None:
            session.delete(availability)


def load_catalog(session: Session, file_path: Path) -> LoadResult:
    """Loads catalogo_motos.csv in one atomic and idempotent transaction."""

    rows, records_received = read_catalog_csv(file_path)
    records_rejected = records_received - len(rows)

    with session.begin():
        upsert_catalog(session, rows)

    return LoadResult(
        records_received=records_received,
        records_processed=len(rows),
        records_rejected=records_rejected,
    )