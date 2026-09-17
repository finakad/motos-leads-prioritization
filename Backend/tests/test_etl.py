from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import select

from app.core.database import SessionLocal
from app.etl.common import get_raw_data_path
from app.etl.conversations_loader import read_conversations_json
from app.etl.historical_closings_loader import read_historical_closings_csv
from app.etl.leads_loader import read_leads_csv
from app.models.conversation import Conversation
from app.models.history import HistoricalClosing
from app.models.lead import Lead

COLOMBIA_TZ = ZoneInfo("America/Bogota")


def test_read_leads_csv_counts():
    file_path = get_raw_data_path("leads.csv")
    valid_rows, received = read_leads_csv(file_path)

    assert received == 1503
    assert len(valid_rows) == 1500
    assert received - len(valid_rows) == 3


def test_read_conversations_json():
    file_path = get_raw_data_path("conversaciones.json")
    valid_convs, received = read_conversations_json(file_path)

    assert received == 677
    assert len(valid_convs) == 677
    for c in valid_convs:
        assert c.conversation_id.startswith("CONV-")
        if c.started_at:
            assert c.started_at.tzinfo == COLOMBIA_TZ


def test_read_historical_closings_csv():
    file_path = get_raw_data_path("historico_cierres.csv")
    valid_rows, received = read_historical_closings_csv(file_path)

    assert received == 2200
    assert len(valid_rows) == 2200

    outcomes = {r.outcome for r in valid_rows}
    assert "Cerrado" in outcomes
    assert "Perdido" in outcomes
    assert "Sin gestión" in outcomes


def test_database_persisted_counts():
    with SessionLocal() as session:
        leads_count = session.query(Lead).count()
        convs_count = session.query(Conversation).count()
        closings_count = session.query(HistoricalClosing).count()

        assert leads_count == 1500
        assert convs_count == 677
        assert closings_count == 2200
