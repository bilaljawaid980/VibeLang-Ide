from app import app


def test_health_route_reports_service_status():
    client = app.test_client()
    response = client.get("/health")
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["service"] == "vibelang-compiler"
    assert "ai" in data
