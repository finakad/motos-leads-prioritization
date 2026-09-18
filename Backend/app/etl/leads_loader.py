def _normalize_channel(value: str | None) -> str | None:
    if not value:
        return None
    val_clean = value.strip()
    val_lower = val_clean.lower()
    if "whatsapp" in val_lower:
        return "WhatsApp"
    if "meta" in val_lower or "face" in val_lower or "ads" in val_lower:
        return "Meta Ads"
    if "formulario" in val_lower or "web" in val_lower:
        return "Formulario Web"
    return val_clean


import csv
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.etl.common import LoadResult, RowValidationError, SourceFileError
from app.models.lead import Lead, LeadSourceRecord
from app.models.organization import SalesPoint


REQUIRED_COLUMNS = {
    "lead_id",
    "fecha_registro",
    "canal",
    "empresa_id",
    "punto_venta_id",
    "nombre_cliente",
    "telefono",
    "email",
    "ciudad",
    "modelo_interes_texto",
    "estado_gestion",
    "fecha_primer_contacto",
    "campania",
}

SOURCE_FILE_NAME = "leads.csv"
COLOMBIA_TIMEZONE = ZoneInfo("America/Bogota")

DATE_FORMATS = (
    "%d-%m-%Y",
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d/%m/%Y %H:%M",
    "%d/%m/%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M",
    "%m/%d/%Y",
    "%m/%d/%Y %H:%M",
    "%m/%d/%Y %H:%M:%S",
)

EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
)


@dataclass(frozen=True)
class LeadSourceRow:
    """Normalized representation of one leads.csv row."""

    lead_id: str
    company_id: str
    sales_point_id: str
    registered_at: datetime | None
    channel: str | None
    customer_name: str | None
    phone_raw: str | None
    phone_normalized: str | None
    email: str | None
    city: str | None
    model_interest_text: str | None
    management_status: str | None
    first_contact_at: datetime | None
    campaign: str | None
    source_row_number: int
    raw_payload: dict[str, str | None]


def _collapse_spaces(value: str) -> str:
    """Trims text and reduces consecutive whitespace to one space."""

    return " ".join(value.strip().split())


def _required_text(
    row: dict[str, str | None],
    column_name: str,
    row_number: int,
) -> str:
    """Returns a required normalized text value."""

    value = _collapse_spaces(row.get(column_name) or "")

    if not value:
        raise RowValidationError(
            f"Row {row_number}: column '{column_name}' is required."
        )

    return value


def _optional_text(
    row: dict[str, str | None],
    column_name: str,
    max_length: int | None = None,
) -> str | None:
    """Returns optional normalized text, converting empty values to None."""

    value = _collapse_spaces(row.get(column_name) or "")

    if not value:
        return None

    if max_length is not None and len(value) > max_length:
        raise RowValidationError(
            f"Column '{column_name}' exceeds its maximum length of {max_length}."
        )

    return value


def _parse_datetime(
    value: str | None,
    column_name: str,
    row_number: int,
) -> datetime | None:
    """
    Parses source dates into timezone-aware Colombia datetimes.

    Empty values are allowed for date fields.
    """

    normalized_value = _collapse_spaces(value or "")

    if not normalized_value:
        return None

    for date_format in DATE_FORMATS:
        try:
            parsed_datetime = datetime.strptime(
                normalized_value,
                date_format,
            )
            return parsed_datetime.replace(tzinfo=COLOMBIA_TIMEZONE)
        except ValueError:
            continue

    raise RowValidationError(
        f"Row {row_number}: column '{column_name}' contains an invalid date "
        f"value: '{normalized_value}'."
    )


def _normalize_phone(
    value: str | None,
    row_number: int,
) -> tuple[str | None, str | None]:
    """
    Preserves the original phone value and normalizes it to Colombian E.164
    when it represents a valid Colombian mobile phone.

    Invalid optional phone values do not reject the lead:
    - phone_raw preserves the supplied value.
    - phone_normalized is returned as None.

    Valid examples:
    - 310 482 4081      -> +573104824081
    - +57 350 2258611   -> +573502258611
    - 573156610968      -> +573156610968
    """

    phone_raw = _collapse_spaces(value or "")

    if not phone_raw or phone_raw.lower() == "nan":
        return None, None

    digits = re.sub(r"\D", "", phone_raw)

    if len(digits) == 10 and digits.startswith("3"):
        return phone_raw, f"+57{digits}"

    if len(digits) == 12 and digits.startswith("57"):
        national_number = digits[2:]

        if national_number.startswith("3"):
            return phone_raw, f"+{digits}"

    return phone_raw, None

def _normalize_email(
    value: str | None,
    row_number: int,
) -> str | None:
    """Normalizes optional email values and validates their basic structure."""

    email = _collapse_spaces(value or "").lower()

    if not email:
        return None

    if len(email) > 320:
        raise RowValidationError(
            f"Row {row_number}: column 'email' exceeds 320 characters."
        )

    if not EMAIL_PATTERN.fullmatch(email):
        raise RowValidationError(
            f"Row {row_number}: column 'email' has an invalid format."
        )

    return email


def _normalize_row(
    row: dict[str, str | None],
    row_number: int,
) -> LeadSourceRow:
    """Validates and normalizes one source lead row."""

    phone_raw, phone_normalized = _normalize_phone(
        row.get("telefono"),
        row_number,
    )

    return LeadSourceRow(
        lead_id=_required_text(row, "lead_id", row_number),
        company_id=_required_text(row, "empresa_id", row_number),
        sales_point_id=_required_text(row, "punto_venta_id", row_number),
        registered_at=_parse_datetime(
            row.get("fecha_registro"),
            "fecha_registro",
            row_number,
        ),
        channel=_normalize_channel(_optional_text(row, "canal", max_length=50)),
        customer_name=_optional_text(row, "nombre_cliente", max_length=200),
        phone_raw=phone_raw,
        phone_normalized=phone_normalized,
        email=_normalize_email(row.get("email"), row_number),
        city=_optional_text(row, "ciudad", max_length=100),
        model_interest_text=_optional_text(row, "modelo_interes_texto"),
        management_status=_optional_text(
            row,
            "estado_gestion",
            max_length=100,
        ),
        first_contact_at=_parse_datetime(
            row.get("fecha_primer_contacto"),
            "fecha_primer_contacto",
            row_number,
        ),
        campaign=_optional_text(row, "campania", max_length=200),
        source_row_number=row_number,
        raw_payload=dict(row),
    )


def read_leads_csv(file_path: Path) -> tuple[list[LeadSourceRow], int]:
    """
    Reads and validates leads.csv.

    Invalid individual rows are excluded from the data load. Missing headers
    and unsupported encoding are file-level errors that stop the pipeline.
    """

    valid_rows: list[LeadSourceRow] = []
    records_received = 0
    source_lead_ids: set[str] = set()

    try:
        with file_path.open(encoding="utf-8-sig", newline="") as source_file:
            reader = csv.DictReader(source_file)

            if reader.fieldnames is None:
                raise SourceFileError(
                    "The leads CSV file does not contain a header."
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
                    "The leads CSV file is missing required columns: "
                    f"{missing_columns_text}."
                )

            for row_number, row in enumerate(reader, start=2):
                records_received += 1

                try:
                    normalized_row = _normalize_row(row, row_number)

                    if normalized_row.lead_id in source_lead_ids:
                        raise RowValidationError(
                            f"Row {row_number}: duplicated lead_id "
                            f"'{normalized_row.lead_id}' in source file."
                        )

                    source_lead_ids.add(normalized_row.lead_id)
                    valid_rows.append(normalized_row)

                except RowValidationError as exc:
                    print(f"Rejected row {row_number}: {exc}")
                    continue

    except UnicodeDecodeError as exc:
        raise SourceFileError(
            "The leads CSV file must be encoded as UTF-8."
        ) from exc

    return valid_rows, records_received


def _validate_sales_points(
    session: Session,
    rows: list[LeadSourceRow],
) -> None:
    """
    Ensures every lead references an existing sales point from the same company.
    """

    source_sales_point_ids = {
        row.sales_point_id
        for row in rows
    }

    existing_sales_points = {
        sales_point.id: sales_point.company_id
        for sales_point in session.scalars(
            select(SalesPoint).where(
                SalesPoint.id.in_(source_sales_point_ids)
            )
        )
    }

    for row in rows:
        existing_company_id = existing_sales_points.get(row.sales_point_id)

        if existing_company_id is None:
            raise SourceFileError(
                f"Lead '{row.lead_id}' references sales point "
                f"'{row.sales_point_id}', which does not exist."
            )

        if existing_company_id != row.company_id:
            raise SourceFileError(
                f"Lead '{row.lead_id}' references sales point "
                f"'{row.sales_point_id}' for company '{row.company_id}', but "
                f"that sales point belongs to company '{existing_company_id}'."
            )


def upsert_leads(
    session: Session,
    rows: list[LeadSourceRow],
) -> None:
    """
    Creates or updates leads and their traceability records idempotently.
    """

    if not rows:
        return

    _validate_sales_points(session, rows)

    source_lead_ids = {
        row.lead_id
        for row in rows
    }
    source_row_numbers = {
        row.source_row_number
        for row in rows
    }

    existing_leads = {
        lead.id: lead
        for lead in session.scalars(
            select(Lead).where(Lead.id.in_(source_lead_ids))
        )
    }

    existing_source_records = {
        source_record.source_row_number: source_record
        for source_record in session.scalars(
            select(LeadSourceRecord).where(
                LeadSourceRecord.source_file == SOURCE_FILE_NAME,
                LeadSourceRecord.source_row_number.in_(source_row_numbers),
            )
        )
    }

    for row in rows:
        lead = existing_leads.get(row.lead_id)

        if lead is None:
            lead = Lead(
                id=row.lead_id,
                company_id=row.company_id,
                sales_point_id=row.sales_point_id,
                registered_at=row.registered_at,
                channel=row.channel,
                customer_name=row.customer_name,
                phone_raw=row.phone_raw,
                phone_normalized=row.phone_normalized,
                email=row.email,
                city=row.city,
                model_interest_text=row.model_interest_text,
                management_status=row.management_status,
                first_contact_at=row.first_contact_at,
                campaign=row.campaign,
            )
            session.add(lead)
            existing_leads[row.lead_id] = lead

        else:
            lead.company_id = row.company_id
            lead.sales_point_id = row.sales_point_id
            lead.registered_at = row.registered_at
            lead.channel = row.channel
            lead.customer_name = row.customer_name
            lead.phone_raw = row.phone_raw
            lead.phone_normalized = row.phone_normalized
            lead.email = row.email
            lead.city = row.city
            lead.model_interest_text = row.model_interest_text
            lead.management_status = row.management_status
            lead.first_contact_at = row.first_contact_at
            lead.campaign = row.campaign

        source_record = existing_source_records.get(row.source_row_number)

        if source_record is None:
            session.add(
                LeadSourceRecord(
                    lead_id=row.lead_id,
                    source_file=SOURCE_FILE_NAME,
                    source_row_number=row.source_row_number,
                    source_lead_id=row.lead_id,
                    raw_payload=row.raw_payload,
                )
            )
            continue

        source_record.lead_id = row.lead_id
        source_record.source_lead_id = row.lead_id
        source_record.raw_payload = row.raw_payload


def load_leads(session: Session, file_path: Path) -> LoadResult:
    """Loads leads.csv in one atomic and idempotent transaction."""

    rows, records_received = read_leads_csv(file_path)
    records_rejected = records_received - len(rows)

    with session.begin():
        upsert_leads(session, rows)

    return LoadResult(
        records_received=records_received,
        records_processed=len(rows),
        records_rejected=records_rejected,
    )