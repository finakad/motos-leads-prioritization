import csv
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import select

from app.core.database import SessionLocal
from app.etl.common import RowValidationError, SourceFileError
from app.etl.historical_closings_loader import (
    load_historical_closings,
    read_historical_closings_csv,
    upsert_historical_closings,
)
from app.models.history import HistoricalClosing

COLOMBIA_TZ = ZoneInfo("America/Bogota")


@pytest.fixture(autouse=True)
def cleanup_test_historical_closings():
    yield
    with SessionLocal() as session:
        session.query(HistoricalClosing).filter(
            HistoricalClosing.id.like("HX-TEST-%")
        ).delete(synchronize_session=False)
        session.commit()


def _create_sample_csv(file_path: Path, rows: list[dict]):
    headers = [
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
    ]
    with file_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def test_normalization_and_target_mapping(tmp_path: Path):
    rows = [
        {
            "lead_id": "HX-TEST-001",
            "fecha_registro": "2026-04-07",
            "canal": "  whatsapp  ",
            "empresa_id": "EMP-01",
            "punto_venta_id": "PV-001",
            "modelo_cotizado": "  Bajaj Pulsar NS 200  ",
            "precio_lista": "15490000",
            "horas_al_primer_contacto": "8.5",
            "numero_contactos": "4",
            "manifesto_cuota_inicial": "SI",
            "forma_pago_declarada": "credito",
            "pidio_cita": "SI",
            "desenlace": "Cerrado",
        },
        {
            "lead_id": "HX-TEST-002",
            "fecha_registro": "2026-05-10",
            "canal": "Meta Ads",
            "empresa_id": "EMP-01",
            "punto_venta_id": "PV-001",
            "modelo_cotizado": "Honda Dio 110",
            "precio_lista": "6890000",
            "horas_al_primer_contacto": "",
            "numero_contactos": "0",
            "manifesto_cuota_inicial": "NO_INFORMA",
            "forma_pago_declarada": "no_informa",
            "pidio_cita": "NO",
            "desenlace": "Sin gestión",
        },
        {
            "lead_id": "HX-TEST-003",
            "fecha_registro": "2026-05-15",
            "canal": "Formulario Web",
            "empresa_id": "EMP-01",
            "punto_venta_id": "PV-001",
            "modelo_cotizado": "AKT NKD 125",
            "precio_lista": "5290000",
            "horas_al_primer_contacto": "24",
            "numero_contactos": "2",
            "manifesto_cuota_inicial": "NO",
            "forma_pago_declarada": "contado",
            "pidio_cita": "NO",
            "desenlace": "Perdido",
        },
    ]
    file_path = tmp_path / "sample_closings.csv"
    _create_sample_csv(file_path, rows)

    parsed_rows, received = read_historical_closings_csv(file_path)
    assert received == 3
    assert len(parsed_rows) == 3

    r1, r2, r3 = parsed_rows

    # Row 1: Cerrado -> True
    assert r1.id == "HX-TEST-001"
    assert r1.channel == "WhatsApp"
    assert r1.channel_raw == "whatsapp"
    assert r1.quoted_model == "Bajaj Pulsar NS 200"
    assert r1.list_price == 15490000
    assert r1.hours_to_first_contact == 8.5
    assert r1.contact_count == 4
    assert r1.down_payment_manifested == "SI"
    assert r1.declared_payment_method == "credito"
    assert r1.requested_appointment is True
    assert r1.outcome == "Cerrado"
    assert r1.outcome_raw == "Cerrado"
    assert r1.target_converted is True
    assert r1.registered_at.tzinfo == COLOMBIA_TZ

    # Row 2: Sin gestión -> None target, null hours
    assert r2.id == "HX-TEST-002"
    assert r2.hours_to_first_contact is None
    assert r2.contact_count == 0
    assert r2.outcome == "Sin gestión"
    assert r2.target_converted is None

    # Row 3: Perdido -> False target
    assert r3.id == "HX-TEST-003"
    assert r3.declared_payment_method == "contado"
    assert r3.requested_appointment is False
    assert r3.outcome == "Perdido"
    assert r3.target_converted is False


def test_invalid_values_rejection(tmp_path: Path):
    rows = [
        # Row with negative price
        {
            "lead_id": "HX-TEST-INV-1",
            "fecha_registro": "2026-04-07",
            "canal": "WhatsApp",
            "empresa_id": "EMP-01",
            "punto_venta_id": "PV-001",
            "modelo_cotizado": "Pulsar",
            "precio_lista": "-1000",
            "horas_al_primer_contacto": "2",
            "numero_contactos": "1",
            "manifesto_cuota_inicial": "NO",
            "forma_pago_declarada": "contado",
            "pidio_cita": "NO",
            "desenlace": "Perdido",
        },
        # Row with invalid date
        {
            "lead_id": "HX-TEST-INV-2",
            "fecha_registro": "2026-02-31",
            "canal": "WhatsApp",
            "empresa_id": "EMP-01",
            "punto_venta_id": "PV-001",
            "modelo_cotizado": "Pulsar",
            "precio_lista": "5000000",
            "horas_al_primer_contacto": "2",
            "numero_contactos": "1",
            "manifesto_cuota_inicial": "NO",
            "forma_pago_declarada": "contado",
            "pidio_cita": "NO",
            "desenlace": "Perdido",
        },
        # Row with negative contact count
        {
            "lead_id": "HX-TEST-INV-3",
            "fecha_registro": "2026-04-07",
            "canal": "WhatsApp",
            "empresa_id": "EMP-01",
            "punto_venta_id": "PV-001",
            "modelo_cotizado": "Pulsar",
            "precio_lista": "5000000",
            "horas_al_primer_contacto": "2",
            "numero_contactos": "-5",
            "manifesto_cuota_inicial": "NO",
            "forma_pago_declarada": "contado",
            "pidio_cita": "NO",
            "desenlace": "Perdido",
        },
    ]
    file_path = tmp_path / "invalid_rows.csv"
    _create_sample_csv(file_path, rows)

    parsed_rows, received = read_historical_closings_csv(file_path)
    assert received == 3
    assert len(parsed_rows) == 0  # all 3 rejected


def test_duplicate_lead_id_in_source_rejected(tmp_path: Path):
    rows = [
        {
            "lead_id": "HX-TEST-DUP",
            "fecha_registro": "2026-04-07",
            "canal": "WhatsApp",
            "empresa_id": "EMP-01",
            "punto_venta_id": "PV-001",
            "modelo_cotizado": "Pulsar",
            "precio_lista": "5000000",
            "horas_al_primer_contacto": "2",
            "numero_contactos": "1",
            "manifesto_cuota_inicial": "NO",
            "forma_pago_declarada": "contado",
            "pidio_cita": "NO",
            "desenlace": "Perdido",
        },
        {
            "lead_id": "HX-TEST-DUP",  # duplicate ID
            "fecha_registro": "2026-04-08",
            "canal": "WhatsApp",
            "empresa_id": "EMP-01",
            "punto_venta_id": "PV-001",
            "modelo_cotizado": "Pulsar",
            "precio_lista": "5000000",
            "horas_al_primer_contacto": "4",
            "numero_contactos": "2",
            "manifesto_cuota_inicial": "NO",
            "forma_pago_declarada": "contado",
            "pidio_cita": "NO",
            "desenlace": "Cerrado",
        },
    ]
    file_path = tmp_path / "dup_rows.csv"
    _create_sample_csv(file_path, rows)

    parsed_rows, received = read_historical_closings_csv(file_path)
    assert received == 2
    assert len(parsed_rows) == 1
    assert parsed_rows[0].id == "HX-TEST-DUP"


def test_idempotent_load_execution(tmp_path: Path):
    rows = [
        {
            "lead_id": "HX-TEST-IDEMP-1",
            "fecha_registro": "2026-04-07",
            "canal": "WhatsApp",
            "empresa_id": "EMP-01",
            "punto_venta_id": "PV-001",
            "modelo_cotizado": "Pulsar NS 200",
            "precio_lista": "15000000",
            "horas_al_primer_contacto": "1",
            "numero_contactos": "3",
            "manifesto_cuota_inicial": "SI",
            "forma_pago_declarada": "credito",
            "pidio_cita": "SI",
            "desenlace": "Cerrado",
        }
    ]
    file_path = tmp_path / "idemp.csv"
    _create_sample_csv(file_path, rows)

    with SessionLocal() as session:
        res1 = load_historical_closings(session, file_path)
        assert res1.records_received == 1
        assert res1.records_processed == 1
        assert res1.records_rejected == 0

        record1 = session.get(HistoricalClosing, "HX-TEST-IDEMP-1")
        assert record1 is not None
        assert record1.target_converted is True

        # Re-run same file
        res2 = load_historical_closings(session, file_path)
        assert res2.records_received == 1
        assert res2.records_processed == 1
        assert res2.records_rejected == 0

        # Verify count does not increase
        count = session.query(HistoricalClosing).filter(
            HistoricalClosing.id == "HX-TEST-IDEMP-1"
        ).count()
        assert count == 1


def test_company_sales_point_isolation_mismatch(tmp_path: Path):
    # PV-001 belongs to EMP-01. Trying to insert with EMP-02 must be rejected.
    rows = [
        {
            "lead_id": "HX-TEST-MISMATCH",
            "fecha_registro": "2026-04-07",
            "canal": "WhatsApp",
            "empresa_id": "EMP-02",  # Mismatch: PV-001 is EMP-01
            "punto_venta_id": "PV-001",
            "modelo_cotizado": "Pulsar",
            "precio_lista": "10000000",
            "horas_al_primer_contacto": "1",
            "numero_contactos": "1",
            "manifesto_cuota_inicial": "NO",
            "forma_pago_declarada": "contado",
            "pidio_cita": "NO",
            "desenlace": "Perdido",
        }
    ]
    file_path = tmp_path / "mismatch.csv"
    _create_sample_csv(file_path, rows)

    with SessionLocal() as session:
        with pytest.raises(SourceFileError) as exc_info:
            load_historical_closings(session, file_path)
        assert "belongs to" in str(exc_info.value)
