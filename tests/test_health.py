def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["product"] == "Scadova-AI-India"
    assert data["module"] == "loan_agency"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"


def test_health_endpoints(client):
    # Main health
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"success": True, "status": "healthy"}

    # Live health
    res_live = client.get("/health/live")
    assert res_live.status_code == 200
    assert res_live.json() == {"status": "alive"}

    # Ready health
    res_ready = client.get("/health/ready")
    assert res_ready.status_code == 200
    assert res_ready.json() == {"status": "ready", "database": "connected"}


def test_loan_agency_home(client):
    res = client.get("/api/loan-agency/")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["module"] == "loan_agency"
    assert "business_loan" in data["products"]
    assert "personal_loan" in data["products"]
    assert "used_car_loan" in data["products"]
