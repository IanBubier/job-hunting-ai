from backend.utils.validators import validate_search_request


def test_valid_request():
    ok, err = validate_search_request(
        {
            "skills": ["Python"],
            "keywords": "Developer",
            "location": "Remote",
            "experience": "2",
            "max_results": 10,
        }
    )
    assert ok is True


def test_invalid_request_skills():
    ok, err = validate_search_request({"skills": []})
    assert ok is False
    assert "skills" in err["details"]
