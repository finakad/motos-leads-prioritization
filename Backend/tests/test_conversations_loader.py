import json
from datetime import time
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import select

from app.core.database import SessionLocal
from app.etl.common import SourceFileError
from app.etl.conversations_loader import (
    load_conversations,
    read_conversations_json,
    upsert_conversations,
)
from app.models.conversation import Conversation, ConversationMessage
from app.models.lead import Lead

COLOMBIA_TZ = ZoneInfo("America/Bogota")


@pytest.fixture(autouse=True)
def cleanup_test_conversations():
    yield
    with SessionLocal() as session:
        session.query(Conversation).filter(
            Conversation.id.like("CONV-%-001") | Conversation.id.like("CONV-EMPTY-%")
        ).delete(synchronize_session=False)
        session.commit()


def test_valid_conversation_with_multiple_messages(tmp_path: Path):
    data = [
        {
            "conversacion_id": "CONV-TEST-001",
            "lead_id": "LD-00001",
            "canal": "WhatsApp",
            "fecha_inicio": "2026-08-01 10:30:00",
            "mensajes": [
                {"emisor": "cliente", "hora": "10:30", "texto": "Hola, precio de la Pulsar?"},
                {"emisor": "asesor", "hora": "10:32", "texto": "Buenas tardes, está en 15M."},
                {"emisor": "cliente", "hora": "10:35", "texto": "Gracias, pasaré a verla."},
            ],
        }
    ]
    file_path = tmp_path / "conv_valid.json"
    file_path.write_text(json.dumps(data), encoding="utf-8")

    convs, received = read_conversations_json(file_path)
    assert received == 1
    assert len(convs) == 1
    c = convs[0]
    assert c.conversation_id == "CONV-TEST-001"
    assert c.source_lead_id == "LD-00001"
    assert c.channel == "WhatsApp"
    assert c.started_at.hour == 10
    assert c.started_at.tzinfo == COLOMBIA_TZ
    assert len(c.messages) == 3

    # Check strictly sequential ordering
    assert [m.sequence_number for m in c.messages] == [1, 2, 3]
    assert [m.sender for m in c.messages] == ["cliente", "asesor", "cliente"]
    assert c.messages[0].message_time == time(10, 30)


def test_idempotent_reexecution(tmp_path: Path):
    data = [
        {
            "conversacion_id": "CONV-IDEMP-001",
            "lead_id": "LD-00001",
            "canal": "WhatsApp",
            "fecha_inicio": "2026-08-02 11:00:00",
            "mensajes": [
                {"emisor": "cliente", "hora": "11:00", "texto": "Mensaje 1"},
                {"emisor": "asesor", "hora": "11:05", "texto": "Mensaje 2"},
            ],
        }
    ]
    file_path = tmp_path / "conv_idemp.json"
    file_path.write_text(json.dumps(data), encoding="utf-8")

    with SessionLocal() as session:
        # First execution
        res1 = load_conversations(session, file_path)
        assert res1.records_received == 1
        assert res1.records_processed == 1
        assert res1.records_rejected == 0

        # Query messages count in DB
        msgs_count_1 = session.query(ConversationMessage).filter_by(
            conversation_id="CONV-IDEMP-001"
        ).count()
        assert msgs_count_1 == 2

        # Second execution (reexecution)
        res2 = load_conversations(session, file_path)
        assert res2.records_received == 1
        assert res2.records_processed == 1
        assert res2.records_rejected == 0

        msgs_count_2 = session.query(ConversationMessage).filter_by(
            conversation_id="CONV-IDEMP-001"
        ).count()
        assert msgs_count_2 == 2

        # Verify no duplicate conversations
        convs_count = session.query(Conversation).filter_by(
            id="CONV-IDEMP-001"
        ).count()
        assert convs_count == 1


def test_stable_message_ordering(tmp_path: Path):
    data = [
        {
            "conversacion_id": "CONV-ORDER-001",
            "lead_id": "LD-00001",
            "canal": "WhatsApp",
            "fecha_inicio": "2026-08-03 09:00:00",
            "mensajes": [
                {"emisor": "cliente", "hora": "09:00", "texto": "Paso 1"},
                {"emisor": "asesor", "hora": "09:01", "texto": "Paso 2"},
                {"emisor": "cliente", "hora": "09:02", "texto": "Paso 3"},
                {"emisor": "asesor", "hora": "09:03", "texto": "Paso 4"},
                {"emisor": "cliente", "hora": "09:04", "texto": "Paso 5"},
            ],
        }
    ]
    file_path = tmp_path / "conv_order.json"
    file_path.write_text(json.dumps(data), encoding="utf-8")

    with SessionLocal() as session:
        load_conversations(session, file_path)
        conv = session.get(Conversation, "CONV-ORDER-001")
        assert conv is not None
        assert [m.sequence_number for m in conv.messages] == [1, 2, 3, 4, 5]
        assert [m.text for m in conv.messages] == [
            "Paso 1",
            "Paso 2",
            "Paso 3",
            "Paso 4",
            "Paso 5",
        ]


def test_existing_lead_association(tmp_path: Path):
    with SessionLocal() as session:
        lead = session.scalars(select(Lead)).first()
        assert lead is not None

        data = [
            {
                "conversacion_id": "CONV-MATCH-001",
                "lead_id": lead.id,
                "canal": "WhatsApp",
                "fecha_inicio": "2026-08-04 12:00:00",
                "mensajes": [{"emisor": "cliente", "hora": "12:00", "texto": "Hola"}],
            }
        ]
        file_path = tmp_path / "conv_match.json"
        file_path.write_text(json.dumps(data), encoding="utf-8")

        load_conversations(session, file_path)
        conv = session.get(Conversation, "CONV-MATCH-001")
        assert conv is not None
        assert conv.lead_id == lead.id
        assert conv.source_lead_id == lead.id


def test_nonexistent_lead_preserved_with_null_foreign_key(tmp_path: Path):
    data = [
        {
            "conversacion_id": "CONV-ORPHAN-001",
            "lead_id": "LD-99999",
            "canal": "WhatsApp",
            "fecha_inicio": "2026-08-04 14:00:00",
            "mensajes": [{"emisor": "cliente", "hora": "14:00", "texto": "Lead fantasma"}],
        }
    ]
    file_path = tmp_path / "conv_orphan.json"
    file_path.write_text(json.dumps(data), encoding="utf-8")

    with SessionLocal() as session:
        res = load_conversations(session, file_path)
        assert res.records_processed == 1
        assert res.records_rejected == 0

        conv = session.get(Conversation, "CONV-ORPHAN-001")
        assert conv is not None
        assert conv.lead_id is None
        assert conv.source_lead_id == "LD-99999"
        assert len(conv.messages) == 1


def test_invalid_date_and_time_safe_handling(tmp_path: Path):
    data = [
        {
            "conversacion_id": "CONV-DATES-001",
            "lead_id": "LD-00001",
            "canal": "WhatsApp",
            "fecha_inicio": "2026-08-33 99:00:00",
            "mensajes": [
                {
                    "emisor": "cliente",
                    "hora": "25:99",
                    "texto": "Mensaje con hora rara",
                }
            ],
        }
    ]
    file_path = tmp_path / "conv_dates.json"
    file_path.write_text(json.dumps(data), encoding="utf-8")

    with SessionLocal() as session:
        res = load_conversations(session, file_path)
        assert res.records_processed == 1

        conv = session.get(Conversation, "CONV-DATES-001")
        assert conv is not None
        assert conv.started_at is None
        assert conv.messages[0].message_time is None
        assert conv.messages[0].text == "Mensaje con hora rara"


def test_empty_message_text_rejected(tmp_path: Path):
    data = [
        {
            "conversacion_id": "CONV-EMPTY-TXT",
            "lead_id": "LD-00001",
            "canal": "WhatsApp",
            "fecha_inicio": "2026-08-05 10:00:00",
            "mensajes": [
                {"emisor": "cliente", "hora": "10:00", "texto": "   "}
            ],
        }
    ]
    file_path = tmp_path / "conv_blank.json"
    file_path.write_text(json.dumps(data), encoding="utf-8")

    convs, received = read_conversations_json(file_path)
    assert received == 1
    assert len(convs) == 0


def test_malformed_json_file(tmp_path: Path):
    file_path = tmp_path / "malformed.json"
    file_path.write_text("{ not a valid json [", encoding="utf-8")

    with pytest.raises(SourceFileError):
        read_conversations_json(file_path)


def test_json_root_not_list(tmp_path: Path):
    file_path = tmp_path / "dict_root.json"
    file_path.write_text('{"conversacion_id": "CONV-1"}', encoding="utf-8")

    with pytest.raises(SourceFileError):
        read_conversations_json(file_path)


def test_company_isolation_enforcement(tmp_path: Path):
    with SessionLocal() as session:
        lead = session.get(Lead, "LD-00001")
        assert lead is not None

        data = [
            {
                "conversacion_id": "CONV-ISOLATION-001",
                "lead_id": "LD-00001",
                "company_id": "EMP-OTHER",
                "canal": "WhatsApp",
                "fecha_inicio": "2026-08-06 15:00:00",
                "mensajes": [{"emisor": "cliente", "hora": "15:00", "texto": "Test isolation"}],
            }
        ]
        file_path = tmp_path / "conv_iso.json"
        file_path.write_text(json.dumps(data), encoding="utf-8")

        load_conversations(session, file_path)
        conv = session.get(Conversation, "CONV-ISOLATION-001")
        assert conv is not None
        assert conv.lead_id is None
        assert conv.source_lead_id == "LD-00001"
