from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.main import app
from app.models.lead import Lead

client = TestClient(app)


def test_health_endpoints():
    r1 = client.get("/health")
    assert r1.status_code == 200
    assert r1.json()["status"] == "ok"

    r2 = client.get("/health/database")
    assert r2.status_code == 200
    assert r2.json()["database"] == "ok"


def test_cors_preflight_and_headers():
    # OPTIONS preflight request
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "X-Company-ID, Content-Type",
    }
    res_opt = client.options("/api/v1/companies/EMP-01/leads/prioritized", headers=headers)
    assert res_opt.status_code == 200
    assert res_opt.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert "x-company-id" in res_opt.headers.get("access-control-allow-headers", "").lower()

    # GET request with Origin
    res_get = client.get(
        "/api/v1/companies/EMP-01/leads/prioritized",
        headers={"Origin": "http://localhost:5173"},
    )
    assert res_get.status_code == 200
    assert res_get.headers.get("access-control-allow-origin") == "http://localhost:5173"



def test_list_prioritized_leads_segregation():
    response = client.get("/api/v1/companies/EMP-01/leads/prioritized?page_size=20")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) > 0

    for item in data["items"]:
        assert item["company_id"] == "EMP-01"


def test_nonexistent_company_returns_404():
    response = client.get("/api/v1/companies/EMP-9999/leads/prioritized")
    assert response.status_code == 404
    assert "no encontrada" in response.json()["detail"]


def test_cross_company_access_denied_404():
    # Find a lead belonging to EMP-01 and another belonging to EMP-02
    with SessionLocal() as session:
        emp01_lead = session.scalar(
            select(Lead.id).where(Lead.company_id == "EMP-01")
        )
        emp02_lead = session.scalar(
            select(Lead.id).where(Lead.company_id == "EMP-02")
        )

    assert emp01_lead is not None
    assert emp02_lead is not None

    # Valid tenant access
    r_valid = client.get(f"/api/v1/companies/EMP-01/leads/{emp01_lead}/score")
    assert r_valid.status_code == 200
    data = r_valid.json()
    assert data["company_id"] == "EMP-01"
    assert data["lead_id"] == emp01_lead
    assert "conversacion_ia" in data["factors"]
    assert "evidence" in data

    # Cross-tenant access attempt: EMP-02 trying to see EMP-01's lead
    r_invalid = client.get(f"/api/v1/companies/EMP-02/leads/{emp01_lead}/score")
    assert r_invalid.status_code == 404
    assert "no encontrado en la compañía" in r_invalid.json()["detail"]


def test_filter_by_priority_tier():
    response = client.get(
        "/api/v1/companies/EMP-01/leads/prioritized?priority_tier=ALTA&page_size=10"
    )
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) > 0
    for item in items:
        assert item["priority_tier"] == "ALTA"
        assert item["company_id"] == "EMP-01"



def test_etl_runs_audit():
    response = client.get("/api/v1/etl/runs?limit=5")
    assert response.status_code == 200
    runs = response.json()
    assert len(runs) > 0
    first_run = runs[0]
    assert "status" in first_run
    assert "records_received" in first_run
    assert "records_processed" in first_run
    assert "records_rejected" in first_run
