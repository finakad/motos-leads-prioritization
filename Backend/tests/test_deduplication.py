from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models.deduplication import LeadDuplicateCandidate
from app.models.lead import Lead
from app.services.deduplication_service import LeadDeduplicationService
from app.utils.normalizers import (
    normalize_city,
    normalize_email,
    normalize_person_name,
    normalize_phone_e164,
    token_similarity,
)


def test_normalizers_phone_and_email():
    # Test phone normalization with diverse formats
    assert normalize_phone_e164("310 482 4081") == "+573104824081"
    assert normalize_phone_e164("+57 310 482 4081") == "+573104824081"
    assert normalize_phone_e164("573104824081") == "+573104824081"
    assert normalize_phone_e164("+573104824081") == "+573104824081"
    assert normalize_phone_e164("12345") is None

    # Test email normalization with whitespace and uppercase
    assert (
        normalize_email("  Juan.Perez@Example.Com  ")
        == "juan.perez@example.com"
    )
    assert normalize_email("invalid-email") is None


def test_normalizers_name_and_city():
    # Test name normalization removing accents and extra spaces
    assert (
        normalize_person_name("  Luz Marina  Jiménez  Ospina ")
        == "luz marina jimenez ospina"
    )
    assert (
        normalize_person_name("JUAN PÉREZ DÍAZ")
        == "juan perez diaz"
    )

    # Test token similarity
    sim = token_similarity(
        "Luz Marina Jiménez Ospina",
        "luz marina jimenez",
    )
    assert sim >= 0.80

    # Test city canonical mapping
    assert normalize_city("B/quilla") == "barranquilla"
    assert normalize_city("Bogotá D.C.") == "bogota"
    assert normalize_city("bogota dc") == "bogota"
    assert normalize_city("Cartagena de Indias") == "cartagena"


def test_matching_same_phone_different_formats():
    service = LeadDeduplicationService()

    lead_a = Lead(
        id="TEST-01",
        company_id="EMP-01",
        sales_point_id="PV-001",
        customer_name="Carlos Gomez",
        phone_raw="310 482 4081",
        phone_normalized="+573104824081",
        email="carlos@test.com",
        city="Medellin",
    )
    lead_b = Lead(
        id="TEST-02",
        company_id="EMP-01",
        sales_point_id="PV-002",
        customer_name="Carlos A. Gomez",
        phone_raw="+57 310 482 4081",
        phone_normalized="+573104824081",
        email="carlos.g@gmail.com",
        city="Medellin",
    )

    result = service.evaluate_pair(lead_a, lead_b)
    assert result is not None
    tier, score, reasons, evidence = result

    assert tier == "ALTA_CONFIANZA"
    assert score >= 0.95
    assert "SAME_PHONE_E164" in reasons
    assert evidence["phone_a"] == "+573104824081"
    assert evidence["phone_b"] == "+573104824081"


def test_matching_same_email_different_case_and_spaces():
    service = LeadDeduplicationService()

    lead_a = Lead(
        id="TEST-03",
        company_id="EMP-01",
        sales_point_id="PV-001",
        customer_name="Ana Maria Morales",
        phone_raw=None,
        phone_normalized=None,
        email="  Ana.Morales@Empresa.com ",
        city="Bogota",
    )
    lead_b = Lead(
        id="TEST-04",
        company_id="EMP-01",
        sales_point_id="PV-003",
        customer_name="Ana Morales",
        phone_raw=None,
        phone_normalized=None,
        email="ana.morales@empresa.com",
        city="Bogota",
    )

    result = service.evaluate_pair(lead_a, lead_b)
    assert result is not None
    tier, score, reasons, evidence = result

    assert tier == "ALTA_CONFIANZA"
    assert score >= 0.95
    assert "SAME_EMAIL" in reasons
    assert evidence["email_a"] == "ana.morales@empresa.com"
    assert evidence["email_b"] == "ana.morales@empresa.com"


def test_matching_similar_name_without_sufficient_evidence():
    service = LeadDeduplicationService()

    # Same name but distinct phones and different cities -> should NOT match (negative guard)
    lead_a = Lead(
        id="TEST-05",
        company_id="EMP-01",
        sales_point_id="PV-001",
        customer_name="Juan Perez",
        phone_raw="3111111111",
        phone_normalized="+573111111111",
        email="juan1@gmail.com",
        city="Medellin",
        model_interest_text="NKD 125",
    )
    lead_b = Lead(
        id="TEST-06",
        company_id="EMP-01",
        sales_point_id="PV-002",
        customer_name="Juan Perez",
        phone_raw="3222222222",
        phone_normalized="+573222222222",
        email="juan2@gmail.com",
        city="Bogota",
        model_interest_text="Pulsar NS 200",
    )

    result = service.evaluate_pair(lead_a, lead_b)
    assert result is None


def test_matching_similar_name_with_complementary_evidence():
    service = LeadDeduplicationService()

    now = datetime.now(timezone.utc)
    # Similar name, no phone conflict, same city, same model, temporal proximity
    lead_a = Lead(
        id="TEST-07",
        company_id="EMP-01",
        sales_point_id="PV-001",
        customer_name="Luz Marina Jimenez Ospina",
        phone_raw=None,
        phone_normalized=None,
        email="luz@test.com",
        city="Barranquilla",
        model_interest_text="NKD 125 2026",
        registered_at=now,
    )
    lead_b = Lead(
        id="TEST-08",
        company_id="EMP-01",
        sales_point_id="PV-002",
        customer_name="luz marina jimenez",
        phone_raw=None,
        phone_normalized=None,
        email=None,
        city="B/quilla",
        model_interest_text="AKT NKD 125",
        registered_at=now,
    )

    result = service.evaluate_pair(lead_a, lead_b)
    assert result is not None
    tier, score, reasons, evidence = result

    assert tier == "POSIBLE_COINCIDENCIA"
    assert 0.60 <= score <= 0.85
    assert "SIMILAR_NAME" in reasons
    assert "SAME_CITY" in reasons
    assert "SAME_MODEL" in reasons


def test_cross_company_apparent_match_strictly_forbidden():
    service = LeadDeduplicationService()

    # Same phone and name, but different companies: EMP-01 vs EMP-02
    lead_a = Lead(
        id="TEST-09",
        company_id="EMP-01",
        sales_point_id="PV-001",
        customer_name="Pedro Ramirez",
        phone_raw="3156610968",
        phone_normalized="+573156610968",
        email="pedro@example.com",
    )
    lead_b = Lead(
        id="TEST-10",
        company_id="EMP-02",
        sales_point_id="PV-006",
        customer_name="Pedro Ramirez",
        phone_raw="3156610968",
        phone_normalized="+573156610968",
        email="pedro@example.com",
    )

    result = service.evaluate_pair(lead_a, lead_b)
    assert result is not None
    tier, score, reasons, evidence = result

    assert tier == "NUNCA_COINCIDENCIA"
    assert score == 0.0
    assert "CROSS_COMPANY_FORBIDDEN" in reasons
    assert evidence["company_a"] == "EMP-01"
    assert evidence["company_b"] == "EMP-02"


def test_idempotent_service_execution_and_traceability():
    service = LeadDeduplicationService()

    with SessionLocal() as session:
        # Run detection for company EMP-01
        summary_first = service.detect_duplicates_for_company(session, "EMP-01")
        assert summary_first.company_id == "EMP-01"
        assert summary_first.total_candidates > 0

        count_first = session.scalar(
            select(func.count(LeadDuplicateCandidate.id)).where(
                LeadDuplicateCandidate.company_id == "EMP-01"
            )
        )

        # Run detection second time for same company
        summary_second = service.detect_duplicates_for_company(session, "EMP-01")
        assert summary_second.total_candidates == summary_first.total_candidates

        count_second = session.scalar(
            select(func.count(LeadDuplicateCandidate.id)).where(
                LeadDuplicateCandidate.company_id == "EMP-01"
            )
        )

        # Count must remain strictly identical
        assert count_first == count_second

        # Verify candidate traceability and evidence fields
        sample = session.scalars(
            select(LeadDuplicateCandidate).where(
                LeadDuplicateCandidate.company_id == "EMP-01"
            ).limit(1)
        ).first()

        assert sample is not None
        assert sample.company_id == "EMP-01"
        assert sample.primary_lead_id != sample.duplicate_lead_id
        assert sample.confidence_tier in ("ALTA_CONFIANZA", "POSIBLE_COINCIDENCIA")
        assert 0.0 <= float(sample.match_score) <= 1.0
        assert isinstance(sample.match_reasons, list)
        assert len(sample.match_reasons) > 0
        assert isinstance(sample.evidence_payload, dict)
        assert "lead_id_a" in sample.evidence_payload
        assert "lead_id_b" in sample.evidence_payload


def test_consolidation_lifecycle_without_source_mutation():
    service = LeadDeduplicationService()

    with SessionLocal() as session:
        # Fetch an existing candidate
        candidate = session.scalars(
            select(LeadDuplicateCandidate).limit(1)
        ).first()
        assert candidate is not None

        orig_primary_id = candidate.primary_lead_id
        orig_dup_id = candidate.duplicate_lead_id

        # Verify both leads exist prior to consolidation
        lead_primary = session.get(Lead, orig_primary_id)
        lead_dup = session.get(Lead, orig_dup_id)
        assert lead_primary is not None
        assert lead_dup is not None

        # Consolidate candidate virtually
        updated_candidate = service.consolidate_candidate(
            session=session,
            candidate_id=candidate.id,
            decision="FUSIONAR_VIRTUAL",
            decision_by="supervisor_test",
            decision_notes="Mismo prospecto confirmado por teléfono.",
        )

        assert updated_candidate.status == "CONSOLIDADO"
        assert updated_candidate.decision == "FUSIONAR_VIRTUAL"
        assert updated_candidate.decision_by == "supervisor_test"
        assert updated_candidate.decided_at is not None

        # Verify source leads remain completely intact
        lead_primary_after = session.get(Lead, orig_primary_id)
        lead_dup_after = session.get(Lead, orig_dup_id)
        assert lead_primary_after is not None
        assert lead_dup_after is not None
        assert lead_primary_after.id == orig_primary_id
        assert lead_dup_after.id == orig_dup_id
