from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.main import app
from app.models.conversation import Conversation
from app.models.lead import Lead
from app.models.organization import Advisor

client = TestClient(app)


def test_get_lead_detail_success_and_minimization():
    with SessionLocal() as session:
        lead = session.scalars(
            select(Lead).where(Lead.company_id == "EMP-01").limit(1)
        ).first()
        assert lead is not None

    response = client.get(f"/api/v1/companies/EMP-01/leads/{lead.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["lead_id"] == lead.id
    assert data["company_id"] == "EMP-01"
    assert "sales_point_id" in data
    assert "score" in data
    # Data minimization: phone is masked, phone_raw is NOT returned
    assert "phone_raw" not in data
    assert "phone_masked" in data
    if data["phone_masked"]:
        assert "***" in data["phone_masked"]


def test_get_lead_detail_cross_company_returns_404():
    # Lead from EMP-02
    with SessionLocal() as session:
        emp02_lead = session.scalars(
            select(Lead).where(Lead.company_id == "EMP-02").limit(1)
        ).first()
        assert emp02_lead is not None

    # Requesting from EMP-01 must return 404
    response = client.get(f"/api/v1/companies/EMP-01/leads/{emp02_lead.id}")
    assert response.status_code == 404
    assert "no encontrado" in response.json()["detail"]


def test_x_company_id_header_matching_and_mismatch_403():
    # Matching header passes
    r_ok = client.get(
        "/api/v1/companies/EMP-01/leads/prioritized?page_size=5",
        headers={"X-Company-ID": "EMP-01"},
    )
    assert r_ok.status_code == 200

    # Mismatched header returns 403 Forbidden
    r_forbidden = client.get(
        "/api/v1/companies/EMP-01/leads/prioritized?page_size=5",
        headers={"X-Company-ID": "EMP-02"},
    )
    assert r_forbidden.status_code == 403
    assert "no coincide" in r_forbidden.json()["detail"]


def test_pagination_structure_and_limits():
    response = client.get(
        "/api/v1/companies/EMP-01/leads/prioritized?page=2&page_size=15"
    )
    assert response.status_code == 200
    data = response.json()

    assert data["page"] == 2
    assert data["page_size"] == 15
    assert data["total"] > 0
    assert data["total_pages"] >= 1
    assert len(data["items"]) <= 15


def test_filter_by_sales_point_and_advisor():
    with SessionLocal() as session:
        advisor = session.scalars(
            select(Advisor).where(Advisor.company_id == "EMP-01").limit(1)
        ).first()
        assert advisor is not None

    # Filter by sales point
    r_sp = client.get(
        f"/api/v1/companies/EMP-01/leads/prioritized?sales_point_id={advisor.sales_point_id}&page_size=10"
    )
    assert r_sp.status_code == 200
    data_sp = r_sp.json()
    for item in data_sp["items"]:
        assert item["sales_point_id"] == advisor.sales_point_id

    # Filter by advisor ID
    r_adv = client.get(
        f"/api/v1/companies/EMP-01/leads/prioritized?advisor_id={advisor.id}&page_size=10"
    )
    assert r_adv.status_code == 200
    data_adv = r_adv.json()
    for item in data_adv["items"]:
        assert item["sales_point_id"] == advisor.sales_point_id


def test_filter_by_channel_and_status():
    response = client.get(
        "/api/v1/companies/EMP-01/leads/prioritized?channel=WhatsApp&page_size=10"
    )
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert "whatsapp" in item["channel"].lower()


def test_filter_by_date_range():
    response = client.get(
        "/api/v1/companies/EMP-01/leads/prioritized?date_from=2026-01-01T00:00:00Z&date_to=2026-12-31T23:59:59Z&page_size=10"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0


def test_sorting_order_by_score_and_registered_at():
    # Sort by score desc
    r_score = client.get(
        "/api/v1/companies/EMP-01/leads/prioritized?order_by=score&order_direction=desc&page_size=10"
    )
    assert r_score.status_code == 200
    scores = [item["score"] for item in r_score.json()["items"]]
    assert scores == sorted(scores, reverse=True)


def test_get_lead_conversations_ordered_messages():
    # Find a lead with a conversation
    with SessionLocal() as session:
        conv = session.scalars(select(Conversation).limit(1)).first()
        assert conv is not None
        lead = session.get(Lead, conv.lead_id)
        assert lead is not None

    response = client.get(
        f"/api/v1/companies/{lead.company_id}/leads/{lead.id}/conversations"
    )
    assert response.status_code == 200
    data = response.json()

    assert data["lead_id"] == lead.id
    assert data["company_id"] == lead.company_id
    assert data["total_conversations"] >= 1
    c1 = data["conversations"][0]
    assert len(c1["messages"]) > 0

    # Verify message sequence order
    seqs = [m["sequence_number"] for m in c1["messages"]]
    assert seqs == sorted(seqs)


def test_get_lead_signals_and_evidence():
    with SessionLocal() as session:
        conv = session.scalars(select(Conversation).limit(1)).first()
        assert conv is not None
        lead = session.get(Lead, conv.lead_id)
        assert lead is not None

    response = client.get(
        f"/api/v1/companies/{lead.company_id}/leads/{lead.id}/signals"
    )
    assert response.status_code == 200
    data = response.json()

    assert data["lead_id"] == lead.id
    assert data["company_id"] == lead.company_id
    assert "purchase_intent_score" in data
    assert "urgency" in data
    assert "signals" in data
    assert "evidence" in data


def test_empty_filter_results_returns_200_with_empty_list():
    response = client.get(
        "/api/v1/companies/EMP-01/leads/prioritized?channel=CanalInexistente12345"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_validation_errors_return_422():
    # Invalid page number (ge=1)
    r1 = client.get("/api/v1/companies/EMP-01/leads/prioritized?page=0")
    assert r1.status_code == 422

    # Invalid page size (le=100)
    r2 = client.get("/api/v1/companies/EMP-01/leads/prioritized?page_size=500")
    assert r2.status_code == 422

    # Invalid priority tier
    r3 = client.get("/api/v1/companies/EMP-01/leads/prioritized?priority_tier=SUPER_ALTA")
    assert r3.status_code == 422
