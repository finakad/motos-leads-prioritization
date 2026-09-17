import json
from dataclasses import dataclass
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.etl.common import LoadResult, RowValidationError, SourceFileError
from app.models.conversation import Conversation, ConversationMessage
from app.models.lead import Lead

COLOMBIA_TIMEZONE = ZoneInfo("America/Bogota")
SOURCE_FILE_NAME = "conversaciones.json"

DATE_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M",
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
    started_at: datetime | None
    messages: list[MessageSourceData]
    raw_payload: dict


def _parse_datetime(value: str | None) -> datetime | None:
    if not value or not value.strip():
        return None

    clean_value = " ".join(value.strip().split())

    for fmt in DATE_FORMATS:
        try:
            parsed = datetime.strptime(clean_value, fmt)
            return parsed.replace(tzinfo=COLOMBIA_TIMEZONE)
        except ValueError:
            continue

    return None


def _parse_time(value: str | None) -> time | None:
    if not value or not value.strip():
        return None

    clean_value = value.strip()

    try:
        return datetime.strptime(clean_value, "%H:%M").time()
    except ValueError:
        try:
            return datetime.strptime(clean_value, "%H:%M:%S").time()
        except ValueError:
            return None


def _normalize_conversation(
    raw_conv: dict,
    index: int,
) -> ConversationSourceData:
    conv_id = (raw_conv.get("conversacion_id") or "").strip()
    if not conv_id:
        raise RowValidationError(
            f"Conversation at index {index} is missing 'conversacion_id'."
        )

    source_lead_id = (raw_conv.get("lead_id") or "").strip() or None
    channel = (raw_conv.get("canal") or "").strip() or None
    started_at = _parse_datetime(raw_conv.get("fecha_inicio"))

    raw_messages = raw_conv.get("mensajes") or []
    normalized_messages: list[MessageSourceData] = []

    for seq, msg in enumerate(raw_messages, start=1):
        sender = (msg.get("emisor") or "desconocido").strip().lower()
        msg_time = _parse_time(msg.get("hora"))
        text = (msg.get("texto") or "").strip()

        normalized_messages.append(
            MessageSourceData(
                sequence_number=seq,
                sender=sender[:30],
                message_time=msg_time,
                text=text,
            )
        )

    return ConversationSourceData(
        conversation_id=conv_id,
        source_lead_id=source_lead_id,
        channel=channel,
        started_at=started_at,
        messages=normalized_messages,
        raw_payload=raw_conv,
    )


def read_conversations_json(
    file_path: Path,
) -> tuple[list[ConversationSourceData], int]:
    try:
        with file_path.open(encoding="utf-8") as source_file:
            data = json.load(source_file)
    except UnicodeDecodeError as exc:
        raise SourceFileError(
            "The conversations JSON file must be encoded as UTF-8."
        ) from exc
    except json.JSONDecodeError as exc:
        raise SourceFileError(
            "The conversations JSON file contains invalid JSON."
        ) from exc

    if not isinstance(data, list):
        raise SourceFileError(
            "The conversations JSON file must contain a root array."
        )

    valid_conversations: list[ConversationSourceData] = []
    records_received = len(data)

    for idx, raw_conv in enumerate(data):
        try:
            conv_data = _normalize_conversation(raw_conv, idx)
            valid_conversations.append(conv_data)
        except RowValidationError as exc:
            print(f"Rejected conversation {idx}: {exc}")
            continue

    return valid_conversations, records_received


def upsert_conversations(
    session: Session,
    conversations_data: list[ConversationSourceData],
) -> None:
    if not conversations_data:
        return

    # Check which source_lead_ids actually exist in the database
    source_lead_ids = {
        c.source_lead_id for c in conversations_data if c.source_lead_id
    }
    existing_lead_ids = set(
        session.scalars(
            select(Lead.id).where(Lead.id.in_(source_lead_ids))
        ).all()
    )

    conv_ids = [c.conversation_id for c in conversations_data]
    existing_conversations = {
        conv.id: conv
        for conv in session.scalars(
            select(Conversation).where(Conversation.id.in_(conv_ids))
        ).all()
    }

    for c_data in conversations_data:
        matched_lead_id = (
            c_data.source_lead_id
            if c_data.source_lead_id in existing_lead_ids
            else None
        )

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
        else:
            conversation.lead_id = matched_lead_id
            conversation.source_lead_id = c_data.source_lead_id
            conversation.channel = c_data.channel
            conversation.started_at = c_data.started_at
            conversation.raw_payload = c_data.raw_payload

            # Delete old messages to reinsert fresh idempotently
            session.execute(
                delete(ConversationMessage).where(
                    ConversationMessage.conversation_id
                    == c_data.conversation_id
                )
            )
            session.flush()

        # Add messages
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


def load_conversations(session: Session, file_path: Path) -> LoadResult:
    """Loads conversaciones.json in one atomic and idempotent transaction."""

    conversations_data, records_received = read_conversations_json(file_path)
    records_rejected = records_received - len(conversations_data)

    with session.begin():
        upsert_conversations(session, conversations_data)

    return LoadResult(
        records_received=records_received,
        records_processed=len(conversations_data),
        records_rejected=records_rejected,
    )
