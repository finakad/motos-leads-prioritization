import json
import logging
from dataclasses import dataclass
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.etl.common import LoadResult, RowValidationError, SourceFileError
from app.models.conversation import Conversation, ConversationMessage
from app.models.lead import Lead

logger = logging.getLogger(__name__)

COLOMBIA_TIMEZONE = ZoneInfo("America/Bogota")
SOURCE_FILE_NAME = "conversaciones.json"

DATE_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M",
    "%Y-%m-%d",
    "%d/%m/%Y",
)


@dataclass(frozen=True)
class MessageSourceData:
    sequence_number: int
    sender: str
    message_time: time | None
    text: str


@dataclass(frozen=True)
class ConversationSourceData:
    conversation_id: str
    source_lead_id: str | None
    channel: str | None
    company_id: str | None
    started_at: datetime | None
    messages: list[MessageSourceData]
    raw_payload: dict


def _collapse_spaces(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(value.strip().split())


def _parse_datetime(value: str | None, conv_id: str) -> datetime | None:
    if not value or not value.strip():
        return None

    clean_value = _collapse_spaces(value)

    for fmt in DATE_FORMATS:
        try:
            parsed = datetime.strptime(clean_value, fmt)
            return parsed.replace(tzinfo=COLOMBIA_TIMEZONE)
        except ValueError:
            continue

    logger.warning(
        "Conversation '%s': invalid date format or value '%s'. Preserving as None in started_at.",
        conv_id,
        clean_value,
    )
    return None


def _parse_time(value: str | None, conv_id: str, seq: int) -> time | None:
    if not value or not value.strip():
        return None

    clean_value = value.strip()

    try:
        return datetime.strptime(clean_value, "%H:%M").time()
    except ValueError:
        try:
            return datetime.strptime(clean_value, "%H:%M:%S").time()
        except ValueError:
            logger.warning(
                "Conversation '%s', message %d: invalid time '%s'. Preserving as None in message_time.",
                conv_id,
                seq,
                clean_value,
            )
            return None


def _normalize_conversation(
    raw_conv: dict,
    index: int,
) -> ConversationSourceData:
    if not isinstance(raw_conv, dict):
        raise RowValidationError(
            f"Conversation at index {index} is not a valid JSON object."
        )

    conv_id = _collapse_spaces(raw_conv.get("conversacion_id"))
    if not conv_id:
        raise RowValidationError(
            f"Conversation at index {index} is missing mandatory 'conversacion_id'."
        )

    source_lead_id = _collapse_spaces(raw_conv.get("lead_id")) or None
    channel = _collapse_spaces(raw_conv.get("canal")) or None
    if channel and len(channel) > 50:
        channel = channel[:50]

    company_id = (
        _collapse_spaces(raw_conv.get("empresa_id") or raw_conv.get("company_id"))
        or None
    )

    started_at = _parse_datetime(raw_conv.get("fecha_inicio"), conv_id)

    raw_messages = raw_conv.get("mensajes")
    if raw_messages is None or not isinstance(raw_messages, list):
        raise RowValidationError(
            f"Conversation '{conv_id}' must contain a 'mensajes' list."
        )

    normalized_messages: list[MessageSourceData] = []

    for seq, msg in enumerate(raw_messages, start=1):
        if not isinstance(msg, dict):
            raise RowValidationError(
                f"Conversation '{conv_id}', message {seq} is not a valid JSON object."
            )

        raw_text = msg.get("texto")
        if raw_text is None:
            raise RowValidationError(
                f"Conversation '{conv_id}', message {seq} is missing mandatory 'texto' field."
            )

        text = raw_text.strip()
        if not text:
            raise RowValidationError(
                f"Conversation '{conv_id}', message {seq} has empty 'texto'. Mandatory field cannot be blank."
            )

        raw_sender = _collapse_spaces(msg.get("emisor"))
        sender = raw_sender.lower() if raw_sender else "desconocido"
        if len(sender) > 30:
            sender = sender[:30]

        msg_time = _parse_time(msg.get("hora"), conv_id, seq)

        normalized_messages.append(
            MessageSourceData(
                sequence_number=seq,
                sender=sender,
                message_time=msg_time,
                text=text,
            )
        )

    return ConversationSourceData(
        conversation_id=conv_id,
        source_lead_id=source_lead_id,
        channel=channel,
        company_id=company_id,
        started_at=started_at,
        messages=normalized_messages,
        raw_payload=raw_conv,
    )


def read_conversations_json(
    file_path: Path,
) -> tuple[list[ConversationSourceData], int]:
    """
    Reads and validates conversaciones.json.
    Returns (valid_conversations, records_received).
    """
    if not file_path.is_file():
        raise SourceFileError(f"Conversations source file not found: {file_path}")

    try:
        with file_path.open(encoding="utf-8") as source_file:
            data = json.load(source_file)
    except UnicodeDecodeError as exc:
        raise SourceFileError(
            "The conversations JSON file must be encoded as UTF-8."
        ) from exc
    except json.JSONDecodeError as exc:
        raise SourceFileError(
            f"The conversations JSON file contains invalid JSON: {exc}"
        ) from exc

    if not isinstance(data, list):
        raise SourceFileError(
            "The conversations JSON file must contain a root array."
        )

    valid_conversations: list[ConversationSourceData] = []
    seen_ids: set[str] = set()
    records_received = len(data)
    incidences: list[str] = []

    for idx, raw_conv in enumerate(data):
        try:
            conv_data = _normalize_conversation(raw_conv, idx)
            if conv_data.conversation_id in seen_ids:
                raise RowValidationError(
                    f"Duplicated conversacion_id '{conv_data.conversation_id}' in source file."
                )
            seen_ids.add(conv_data.conversation_id)
            valid_conversations.append(conv_data)
        except RowValidationError as exc:
            msg = f"Rejected conversation at index {idx}: {exc}"
            logger.warning(msg)
            incidences.append(msg)
            continue

    return valid_conversations, records_received


def upsert_conversations(
    session: Session,
    conversations_data: list[ConversationSourceData],
) -> list[str]:
    """
    Idempotently creates or updates conversations and their messages.
    Enforces lead association and company isolation rules.
    Returns list of data quality incidences detected during loading.
    """
    if not conversations_data:
        return []

    incidences: list[str] = []

    # Pre-fetch existing leads with their company_id to avoid N+1 queries
    source_lead_ids = {
        c.source_lead_id for c in conversations_data if c.source_lead_id
    }
    existing_leads = {
        lead.id: lead.company_id
        for lead in session.scalars(
            select(Lead).where(Lead.id.in_(source_lead_ids))
        ).all()
    }

    # Pre-fetch existing conversations to update them cleanly
    conv_ids = [c.conversation_id for c in conversations_data]
    existing_conversations = {
        conv.id: conv
        for conv in session.scalars(
            select(Conversation).where(Conversation.id.in_(conv_ids))
        ).all()
    }

    for c_data in conversations_data:
        matched_lead_id: str | None = None

        if c_data.source_lead_id:
            lead_company_id = existing_leads.get(c_data.source_lead_id)

            if lead_company_id is None:
                msg = (
                    f"Incidence: Conversation '{c_data.conversation_id}' references lead "
                    f"'{c_data.source_lead_id}', which does not exist in 'leads'. "
                    f"Preserved with lead_id=NULL and source_lead_id."
                )
                logger.info(msg)
                incidences.append(msg)
            elif c_data.company_id and c_data.company_id != lead_company_id:
                msg = (
                    f"Incidence: Conversation '{c_data.conversation_id}' declares company "
                    f"'{c_data.company_id}', but lead '{c_data.source_lead_id}' belongs to "
                    f"'{lead_company_id}'. Association prevented for company isolation."
                )
                logger.warning(msg)
                incidences.append(msg)
            else:
                matched_lead_id = c_data.source_lead_id

        conversation = existing_conversations.get(c_data.conversation_id)

        if conversation is None:
            conversation = Conversation(
                id=c_data.conversation_id,
                lead_id=matched_lead_id,
                source_lead_id=c_data.source_lead_id,
                channel=c_data.channel,
                started_at=c_data.started_at,
                raw_payload=c_data.raw_payload,
            )
            session.add(conversation)
            session.flush()
            existing_conversations[c_data.conversation_id] = conversation
        else:
            conversation.lead_id = matched_lead_id
            conversation.source_lead_id = c_data.source_lead_id
            conversation.channel = c_data.channel
            conversation.started_at = c_data.started_at
            conversation.raw_payload = c_data.raw_payload

            # Delete old messages to reinsert fresh idempotently preserving strict order
            session.execute(
                delete(ConversationMessage).where(
                    ConversationMessage.conversation_id
                    == c_data.conversation_id
                )
            )
            session.flush()

        # Add messages with strictly sequential sequence_number
        for msg in c_data.messages:
            session.add(
                ConversationMessage(
                    conversation_id=c_data.conversation_id,
                    sequence_number=msg.sequence_number,
                    sender=msg.sender,
                    message_time=msg.message_time,
                    text=msg.text,
                )
            )

    return incidences


def load_conversations(session: Session, file_path: Path) -> LoadResult:
    """Loads conversaciones.json in one atomic and idempotent transaction."""

    conversations_data, records_received = read_conversations_json(file_path)
    records_rejected = records_received - len(conversations_data)

    if session.in_transaction():
        db_incidences = upsert_conversations(session, conversations_data)
        session.commit()
    else:
        with session.begin():
            db_incidences = upsert_conversations(session, conversations_data)

    if db_incidences:
        logger.info(
            "Conversations loader completed with %d data quality incidences tracked.",
            len(db_incidences),
        )

    return LoadResult(
        records_received=records_received,
        records_processed=len(conversations_data),
        records_rejected=records_rejected,
    )
