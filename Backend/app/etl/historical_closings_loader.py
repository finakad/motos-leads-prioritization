import csv
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.etl.common import LoadResult, RowValidationError, SourceFileError
from app.models.history import HistoricalClosing
from app.models.organization import SalesPoint

COLOMBIA_TIMEZONE = ZoneInfo("America/Bogota")
SOURCE_FILE_NAME = "historico_cierres.csv"

REQUIRED_COLUMNS = {
    "lead_id",
    "fecha_registro",
    "canal",
    "empresa_id",
    "punto_venta_id",
    "modelo_cotizado",
    "precio_lista",
    "horas_al_primer_contacto",
    "numero_contactos",
    "manifesto_cuota_inicial",
    "forma_pago_declarada",
    "pidio_cita",
    "desenlace",
}

DATE_FORMATS = (
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M:%S",
    "%d/%m/%Y",
    "%d/%m/%Y %H:%M:%S",
    "%d-%m-%Y",
)


@dataclass(frozen=True)
class HistoricalClosingRow:
    id: str
    company_id: str
    sales_point_id: str
    registered_at: datetime | None
    channel: str | None
    quoted_model: str | None
    list_price: int | None
    hours_to_first_contact: float | None
    contact_count: int | None
    down_payment_manifested: str | None
    declared_payment_method: str | None
    requested_appointment: bool | None
    outcome: str
    raw_payload: dict


def _clean_str(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(value.strip().split())


def _strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "MN"
    )


def _parse_datetime(value: str | None) -> datetime | None:
    cleaned = _clean_str(value)
    if not cleaned or cleaned.lower() in ("nan", "null", "none"):
        return None

    for fmt in DATE_FORMATS:
        try:
            parsed = datetime.strptime(cleaned, fmt)
            return parsed.replace(tzinfo=COLOMBIA_TIMEZONE)
        except ValueError:
            continue

    return None


def _parse_optional_int(value: str | None) -> int | None:
    cleaned = _clean_str(value)
    if not cleaned or cleaned.lower() in ("nan", "null", "none"):
        return None
    try:
        return int(float(cleaned))
    except ValueError:
        return None


def _parse_optional_float(value: str | None) -> float | None:
    cleaned = _clean_str(value)
    if not cleaned or cleaned.lower() in ("nan", "null", "none"):
        return None
    try:
        return float(cleaned.replace(",", "."))
    except ValueError:
        return None


def _parse_boolean_si_no(value: str | None) -> bool | None:
    cleaned = _clean_str(value).upper()
    if cleaned in ("SI", "S", "TRUE", "1"):
        return True
    if cleaned in ("NO", "N", "FALSE", "0"):
        return False
    return None


def _normalize_outcome(value: str | None) -> str:
    cleaned = _clean_str(value)
    normalized = _strip_accents(cleaned.lower())

    if "cerrad" in normalized:
        return "Cerrado"
    if "perdid" in normalized:
        return "Perdido"
    if "sin" in normalized and "gest" in normalized:
        return "Sin gestión"

    return cleaned or "Desconocido"


def _normalize_row(row: dict[str, str], row_number: int) -> HistoricalClosingRow:
    lead_id = _clean_str(row.get("lead_id"))
    if not lead_id:
        raise RowValidationError(f"Row {row_number}: 'lead_id' is required.")

    company_id = _clean_str(row.get("empresa_id"))
    if not company_id:
        raise RowValidationError(f"Row {row_number}: 'empresa_id' is required.")

    sales_point_id = _clean_str(row.get("punto_venta_id"))
    if not sales_point_id:
        raise RowValidationError(f"Row {row_number}: 'punto_venta_id' is required.")

    outcome = _normalize_outcome(row.get("desenlace"))

    return HistoricalClosingRow(
        id=lead_id,
        company_id=company_id,
        sales_point_id=sales_point_id,
        registered_at=_parse_datetime(row.get("fecha_registro")),
        channel=_clean_str(row.get("canal")) or None,
        quoted_model=_clean_str(row.get("modelo_cotizado")) or None,
        list_price=_parse_optional_int(row.get("precio_lista")),
        hours_to_first_contact=_parse_optional_float(
            row.get("horas_al_primer_contacto")
        ),
        contact_count=_parse_optional_int(row.get("numero_contactos")),
        down_payment_manifested=_clean_str(row.get("manifesto_cuota_inicial")) or None,
        declared_payment_method=_clean_str(row.get("forma_pago_declarada")) or None,
        requested_appointment=_parse_boolean_si_no(row.get("pidio_cita")),
        outcome=outcome,
        raw_payload=dict(row),
    )


def read_historical_closings_csv(
    file_path: Path,
) -> tuple[list[HistoricalClosingRow], int]:
    valid_rows: list[HistoricalClosingRow] = []
    records_received = 0
    seen_ids: set[str] = set()

    try:
        with file_path.open(encoding="utf-8-sig", newline="") as source_file:
            reader = csv.DictReader(source_file)

            if reader.fieldnames is None:
                raise SourceFileError(
                    "The historical closings CSV does not contain a header."
                )

            source_columns = {
                col.strip() for col in reader.fieldnames if col is not None
            }
            missing = REQUIRED_COLUMNS - source_columns
            if missing:
                missing_text = ", ".join(sorted(missing))
                raise SourceFileError(
                    f"The historical closings CSV is missing columns: {missing_text}."
                )

            for row_number, row in enumerate(reader, start=2):
                records_received += 1
                try:
                    normalized = _normalize_row(row, row_number)
                    if normalized.id in seen_ids:
                        raise RowValidationError(
                            f"Row {row_number}: duplicated lead_id '{normalized.id}'."
                        )
                    seen_ids.add(normalized.id)
                    valid_rows.append(normalized)
                except RowValidationError as exc:
                    print(f"Rejected row {row_number}: {exc}")
                    continue

    except UnicodeDecodeError as exc:
        raise SourceFileError(
            "The historical closings CSV must be encoded as UTF-8."
        ) from exc

    return valid_rows, records_received


def _validate_sales_points(
    session: Session,
    rows: list[HistoricalClosingRow],
) -> None:
    source_sales_point_ids = {row.sales_point_id for row in rows}
    existing_sales_points = {
        sp.id: sp.company_id
        for sp in session.scalars(
            select(SalesPoint).where(SalesPoint.id.in_(source_sales_point_ids))
        )
    }

    for row in rows:
        existing_company_id = existing_sales_points.get(row.sales_point_id)
        if existing_company_id is None:
            raise SourceFileError(
                f"Historical record '{row.id}' references sales point "
                f"'{row.sales_point_id}', which does not exist."
            )
        if existing_company_id != row.company_id:
            raise SourceFileError(
                f"Historical record '{row.id}' references sales point "
                f"'{row.sales_point_id}' for company '{row.company_id}', but "
                f"it belongs to '{existing_company_id}'."
            )


def upsert_historical_closings(
    session: Session,
    rows: list[HistoricalClosingRow],
) -> None:
    if not rows:
        return

    _validate_sales_points(session, rows)

    record_ids = {row.id for row in rows}
    existing_records = {
        r.id: r
        for r in session.scalars(
            select(HistoricalClosing).where(HistoricalClosing.id.in_(record_ids))
        )
    }

    for row in rows:
        record = existing_records.get(row.id)
        if record is None:
            record = HistoricalClosing(
                id=row.id,
                company_id=row.company_id,
                sales_point_id=row.sales_point_id,
                registered_at=row.registered_at,
                channel=row.channel,
                quoted_model=row.quoted_model,
                list_price=row.list_price,
                hours_to_first_contact=row.hours_to_first_contact,
                contact_count=row.contact_count,
                down_payment_manifested=row.down_payment_manifested,
                declared_payment_method=row.declared_payment_method,
                requested_appointment=row.requested_appointment,
                outcome=row.outcome,
                raw_payload=row.raw_payload,
            )
            session.add(record)
            existing_records[row.id] = record
        else:
            record.company_id = row.company_id
            record.sales_point_id = row.sales_point_id
            record.registered_at = row.registered_at
            record.channel = row.channel
            record.quoted_model = row.quoted_model
            record.list_price = row.list_price
            record.hours_to_first_contact = row.hours_to_first_contact
            record.contact_count = row.contact_count
            record.down_payment_manifested = row.down_payment_manifested
            record.declared_payment_method = row.declared_payment_method
            record.requested_appointment = row.requested_appointment
            record.outcome = row.outcome
            record.raw_payload = row.raw_payload


def load_historical_closings(session: Session, file_path: Path) -> LoadResult:
    """Loads historico_cierres.csv in one atomic and idempotent transaction."""

    rows, records_received = read_historical_closings_csv(file_path)
    records_rejected = records_received - len(rows)

    with session.begin():
        upsert_historical_closings(session, rows)

    return LoadResult(
        records_received=records_received,
        records_processed=len(rows),
        records_rejected=records_rejected,
    )
