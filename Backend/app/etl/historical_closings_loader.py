import csv
import logging
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

logger = logging.getLogger(__name__)

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
    channel_raw: str | None
    quoted_model: str | None
    list_price: int | None
    hours_to_first_contact: float | None
    contact_count: int | None
    down_payment_manifested: str | None
    down_payment_raw: str | None
    declared_payment_method: str | None
    declared_payment_method_raw: str | None
    requested_appointment: bool | None
    requested_appointment_raw: str | None
    outcome: str
    outcome_raw: str | None
    target_converted: bool | None
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


def _parse_datetime(value: str | None, row_number: int) -> datetime | None:
    cleaned = _clean_str(value)
    if not cleaned or cleaned.lower() in ("nan", "null", "none"):
        return None

    for fmt in DATE_FORMATS:
        try:
            parsed = datetime.strptime(cleaned, fmt)
            return parsed.replace(tzinfo=COLOMBIA_TIMEZONE)
        except ValueError:
            continue

    raise RowValidationError(
        f"Row {row_number}: column 'fecha_registro' contains invalid date '{cleaned}'."
    )


def _parse_price(value: str | None, row_number: int) -> int | None:
    cleaned = _clean_str(value)
    if not cleaned or cleaned.lower() in ("nan", "null", "none"):
        return None
    try:
        val = int(float(cleaned))
    except ValueError as exc:
        raise RowValidationError(
            f"Row {row_number}: column 'precio_lista' must be a valid number, got '{cleaned}'."
        ) from exc

    if val <= 0:
        raise RowValidationError(
            f"Row {row_number}: column 'precio_lista' must be strictly positive, got {val}."
        )
    return val


def _parse_hours(value: str | None, row_number: int) -> float | None:
    cleaned = _clean_str(value)
    if not cleaned or cleaned.lower() in ("nan", "null", "none"):
        return None
    try:
        val = float(cleaned.replace(",", "."))
    except ValueError as exc:
        raise RowValidationError(
            f"Row {row_number}: column 'horas_al_primer_contacto' must be a float, got '{cleaned}'."
        ) from exc

    if val < 0.0:
        raise RowValidationError(
            f"Row {row_number}: column 'horas_al_primer_contacto' cannot be negative, got {val}."
        )
    return round(val, 2)


def _parse_contact_count(value: str | None, row_number: int) -> int | None:
    cleaned = _clean_str(value)
    if not cleaned or cleaned.lower() in ("nan", "null", "none"):
        return None
    try:
        val = int(float(cleaned))
    except ValueError as exc:
        raise RowValidationError(
            f"Row {row_number}: column 'numero_contactos' must be an integer, got '{cleaned}'."
        ) from exc

    if val < 0:
        raise RowValidationError(
            f"Row {row_number}: column 'numero_contactos' cannot be negative, got {val}."
        )
    return val


def _parse_boolean_si_no(value: str | None) -> bool | None:
    cleaned = _clean_str(value).upper()
    if cleaned in ("SI", "S", "TRUE", "1"):
        return True
    if cleaned in ("NO", "N", "FALSE", "0"):
        return False
    return None


def _normalize_channel(value: str | None) -> str | None:
    cleaned = _clean_str(value)
    if not cleaned:
        return None

    clean_lower = _strip_accents(cleaned.lower())
    if "whatsapp" in clean_lower:
        return "WhatsApp"
    if "meta" in clean_lower or "face" in clean_lower or "ads" in clean_lower:
        return "Meta Ads"
    if "formulario" in clean_lower or "web" in clean_lower:
        return "Formulario Web"
    return cleaned


def _normalize_down_payment(value: str | None) -> str | None:
    cleaned = _clean_str(value)
    if not cleaned:
        return None

    upper = cleaned.upper()
    if upper in ("SI", "S", "TRUE"):
        return "SI"
    if upper in ("NO", "N", "FALSE"):
        return "NO"
    if "NO_INFORMA" in upper or "INFORMA" in upper:
        return "NO_INFORMA"
    return cleaned


def _normalize_payment_method(value: str | None) -> str | None:
    cleaned = _clean_str(value)
    if not cleaned:
        return None

    clean_lower = _strip_accents(cleaned.lower())
    if "credito" in clean_lower or "financ" in clean_lower:
        return "credito"
    if "contado" in clean_lower or "efectivo" in clean_lower:
        return "contado"
    if "no_informa" in clean_lower or "informa" in clean_lower:
        return "no_informa"
    return clean_lower


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


def _compute_target_converted(outcome: str) -> bool | None:
    """
    Computes documented explicit target label for ML conversion models:
    - True: 'Cerrado' (lead successfully converted to sale)
    - False: 'Perdido' (lead was managed but lost/declined)
    - None: 'Sin gestión' (lead uncontacted / censored observation)
    """
    if outcome == "Cerrado":
        return True
    if outcome == "Perdido":
        return False
    return None


def _normalize_row(row: dict[str, str], row_number: int) -> HistoricalClosingRow:
    raw_lead_id = row.get("lead_id")
    lead_id = _clean_str(raw_lead_id)
    if not lead_id:
        raise RowValidationError(f"Row {row_number}: 'lead_id' is required.")

    raw_company_id = row.get("empresa_id")
    company_id = _clean_str(raw_company_id)
    if not company_id:
        raise RowValidationError(f"Row {row_number}: 'empresa_id' is required.")

    raw_sp_id = row.get("punto_venta_id")
    sales_point_id = _clean_str(raw_sp_id)
    if not sales_point_id:
        raise RowValidationError(f"Row {row_number}: 'punto_venta_id' is required.")

    raw_channel = row.get("canal")
    raw_model = row.get("modelo_cotizado")
    raw_dp = row.get("manifesto_cuota_inicial")
    raw_pm = row.get("forma_pago_declarada")
    raw_appt = row.get("pidio_cita")
    raw_outcome = row.get("desenlace")

    registered_at = _parse_datetime(row.get("fecha_registro"), row_number)
    list_price = _parse_price(row.get("precio_lista"), row_number)
    hours_to_first_contact = _parse_hours(
        row.get("horas_al_primer_contacto"), row_number
    )
    contact_count = _parse_contact_count(
        row.get("numero_contactos"), row_number
    )

    channel_norm = _normalize_channel(raw_channel)
    dp_norm = _normalize_down_payment(raw_dp)
    pm_norm = _normalize_payment_method(raw_pm)
    appt_norm = _parse_boolean_si_no(raw_appt)
    outcome_norm = _normalize_outcome(raw_outcome)
    target_converted = _compute_target_converted(outcome_norm)

    return HistoricalClosingRow(
        id=lead_id,
        company_id=company_id,
        sales_point_id=sales_point_id,
        registered_at=registered_at,
        channel=channel_norm,
        channel_raw=_clean_str(raw_channel) or None,
        quoted_model=_clean_str(raw_model) or None,
        list_price=list_price,
        hours_to_first_contact=hours_to_first_contact,
        contact_count=contact_count,
        down_payment_manifested=dp_norm,
        down_payment_raw=_clean_str(raw_dp) or None,
        declared_payment_method=pm_norm,
        declared_payment_method_raw=_clean_str(raw_pm) or None,
        requested_appointment=appt_norm,
        requested_appointment_raw=_clean_str(raw_appt) or None,
        outcome=outcome_norm,
        outcome_raw=_clean_str(raw_outcome) or None,
        target_converted=target_converted,
        raw_payload=dict(row),
    )


def read_historical_closings_csv(
    file_path: Path,
) -> tuple[list[HistoricalClosingRow], int]:
    if not file_path.is_file():
        raise SourceFileError(f"Historical closings file not found: {file_path}")

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
                    f"The historical closings CSV is missing required columns: {missing_text}."
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
                    logger.warning(f"Rejected row {row_number}: {exc}")
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
                channel_raw=row.channel_raw,
                quoted_model=row.quoted_model,
                list_price=row.list_price,
                hours_to_first_contact=row.hours_to_first_contact,
                contact_count=row.contact_count,
                down_payment_manifested=row.down_payment_manifested,
                down_payment_raw=row.down_payment_raw,
                declared_payment_method=row.declared_payment_method,
                declared_payment_method_raw=row.declared_payment_method_raw,
                requested_appointment=row.requested_appointment,
                requested_appointment_raw=row.requested_appointment_raw,
                outcome=row.outcome,
                outcome_raw=row.outcome_raw,
                target_converted=row.target_converted,
                raw_payload=row.raw_payload,
            )
            session.add(record)
            existing_records[row.id] = record
        else:
            record.company_id = row.company_id
            record.sales_point_id = row.sales_point_id
            record.registered_at = row.registered_at
            record.channel = row.channel
            record.channel_raw = row.channel_raw
            record.quoted_model = row.quoted_model
            record.list_price = row.list_price
            record.hours_to_first_contact = row.hours_to_first_contact
            record.contact_count = row.contact_count
            record.down_payment_manifested = row.down_payment_manifested
            record.down_payment_raw = row.down_payment_raw
            record.declared_payment_method = row.declared_payment_method
            record.declared_payment_method_raw = row.declared_payment_method_raw
            record.requested_appointment = row.requested_appointment
            record.requested_appointment_raw = row.requested_appointment_raw
            record.outcome = row.outcome
            record.outcome_raw = row.outcome_raw
            record.target_converted = row.target_converted
            record.raw_payload = row.raw_payload


def load_historical_closings(session: Session, file_path: Path) -> LoadResult:
    """Loads historico_cierres.csv in one atomic and idempotent transaction."""

    rows, records_received = read_historical_closings_csv(file_path)
    records_rejected = records_received - len(rows)

    if session.in_transaction():
        upsert_historical_closings(session, rows)
        session.commit()
    else:
        with session.begin():
            upsert_historical_closings(session, rows)

    return LoadResult(
        records_received=records_received,
        records_processed=len(rows),
        records_rejected=records_rejected,
    )
