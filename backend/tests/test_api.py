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

    payload = {
        "skills": ["Python"],
        "keywords": "Developer",
        "location": "San Francisco, CA",
        "distance": "25",
        "experience": "1",
        "max_results": 10,
    }

    resp = client.post("/search/results", json=payload)
    assert resp.status_code == 200
    content_type = (resp.headers.get("Content-Type") or "").lower()
    # Support both JSON API responses and server-rendered HTML fallback.
    if "application/json" in content_type:
        data = resp.get_json()
        assert "success" in data
        assert isinstance(data.get("results"), list)
    else:
        text = resp.get_data(as_text=True)
        # Basic sanity checks for rendered HTML
        assert "<title>Results" in text or "Search Results" in text
        assert "results-container" in text or "No job results available" in text
