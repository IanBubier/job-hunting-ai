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
