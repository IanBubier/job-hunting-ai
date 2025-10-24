from backend.app import create_app


def test_health_endpoint():
    app = create_app()
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("status") == "healthy"


def test_search_endpoint_basic():
    app = create_app()
    # register the jobs blueprint the same way the real app will
    client = app.test_client()

    payload = {"skills": ["Python"], "keywords": "Developer", "location": "Remote"}

    resp = client.post("/api/search", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "success" in data
    assert isinstance(data.get("results"), list)
