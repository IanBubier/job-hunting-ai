from backend.services.adzuna_service import AdzunaService


def test_adzuna_service_init():
    svc = AdzunaService(app_id="x", app_key="y")
    assert svc.app_id == "x"
    assert svc.app_key == "y"


def test_search_jobs_returns_list():
    svc = AdzunaService()
    res = svc.search_jobs("dev", "remote", "25")
    assert isinstance(res, list)


def test_search_jobs_no_results():
    svc = AdzunaService()
    res = svc.search_jobs("asdkfjaskdfjaskdfj", "Nowhere", "1000", max_results=5)
    assert res == []


def test_remote_jobs_search():
    svc = AdzunaService()
    res = svc.search_jobs("developer remote", None, None, max_results=5)
    assert isinstance(res, list)
    for job in res:
        assert "remote" in job.title.lower() or "remote" in job.description.lower()
