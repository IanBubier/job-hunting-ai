import pytest
from backend.app import create_app
from flask import render_template


@pytest.fixture
def app():
    """
    Fixture to create test Flask app
    """
    app = create_app()
    app.config["TESTING"] = True
    return app


def test_results_template_renders(app):
    """
    Tests that results.html template successfully renders and
    includes expected job fields when provided with mock result data.
    """
    mock_results = {
        "success": True,
        "count": 3,
        "query_time_ms": 142,
        "results": [
            {
                "title": "Software Engineer (Backend)",
                "company": "OpenAI",
                "location": "San Francisco, CA",
                "salary_min": 130000,
                "salary_max": 180000,
                "description": "Work on high-performance backend systems",
                "url": "https://example.com",
                "final_score": 96,
                "posted_date": "2025-11-05",
            },
            {
                "title": "Machine Learning Engineer",
                "company": "Google DeepMind",
                "location": "Mountain View, CA",
                "salary_min": 150000,
                "salary_max": 210000,
                "description": "Develop ML algorithms",
                "url": "https://example.com",
                "final_score": 91,
                "posted_date": "2025-11-03",
            },
        ],
    }

    # Render the template within a valid request context
    with app.test_request_context():
        html = render_template("results.html", page_name="Job Results", **mock_results)

    # Test the rendering of results
    assert "Software Engineer (Backend)" in html
    assert "OpenAI" in html
    assert "Machine Learning Engineer" in html
    assert "Google DeepMind" in html
