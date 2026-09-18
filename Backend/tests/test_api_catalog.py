from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_company_motorcycles_success():
    response = client.get("/api/v1/companies/EMP-01/catalog/motorcycles")
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert "brands" in data
    assert "segments" in data
    assert data["total"] > 0
    assert len(data["items"]) == data["total"]
    assert len(data["brands"]) > 0

    first_item = data["items"][0]
    assert "sku" in first_item
    assert "brand" in first_item
    assert "line" in first_item
    assert "engine_displacement_cc" in first_item
    assert "segment" in first_item
    assert "list_price" in first_item
    assert "reported_available_units" in first_item
    assert "available_sales_points" in first_item
    # All available sales points for EMP-01 must belong to EMP-01 (PV-001 to PV-005)
    for sp in first_item["available_sales_points"]:
        assert sp in ["PV-001", "PV-002", "PV-003", "PV-004", "PV-005"]


def test_list_company_motorcycles_filter_by_brand():
    response = client.get(
        "/api/v1/companies/EMP-01/catalog/motorcycles", params={"brand": "Honda"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    for item in data["items"]:
        assert item["brand"].lower() == "honda"


def test_list_company_motorcycles_filter_by_segment():
    response = client.get(
        "/api/v1/companies/EMP-01/catalog/motorcycles", params={"segment": "Scooter"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    for item in data["items"]:
        assert item["segment"].lower() == "scooter"


def test_list_company_motorcycles_filter_by_sales_point():
    response = client.get(
        "/api/v1/companies/EMP-01/catalog/motorcycles", params={"sales_point_id": "PV-001"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    for item in data["items"]:
        assert "PV-001" in item["available_sales_points"]


def test_list_company_motorcycles_cross_company_sales_point_returns_404():
    # PV-006 belongs to EMP-02, requesting it under EMP-01 must return 404
    response = client.get(
        "/api/v1/companies/EMP-01/catalog/motorcycles", params={"sales_point_id": "PV-006"}
    )
    assert response.status_code == 404
    assert "no pertenece a la compañía" in response.json()["detail"]


def test_get_motorcycle_by_sku_success():
    # Get any valid sku first
    list_res = client.get("/api/v1/companies/EMP-01/catalog/motorcycles")
    assert list_res.status_code == 200
    valid_sku = list_res.json()["items"][0]["sku"]

    response = client.get(f"/api/v1/companies/EMP-01/catalog/motorcycles/{valid_sku}")
    assert response.status_code == 200
    data = response.json()
    assert data["sku"] == valid_sku
    assert "brand" in data
    assert "line" in data
    assert "list_price" in data
    # Availability is segregated to EMP-01
    for sp in data["available_sales_points"]:
        assert sp in ["PV-001", "PV-002", "PV-003", "PV-004", "PV-005"]


def test_get_motorcycle_by_invalid_sku_returns_404():
    response = client.get("/api/v1/companies/EMP-01/catalog/motorcycles/SKU-NON-EXISTENT-999")
    assert response.status_code == 404
