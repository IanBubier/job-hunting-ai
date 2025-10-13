from backend.services.matching_service import MatchingService
from backend.services.ml_service import MLService
from backend.models.job_model import Job


def test_matching_service_rank_empty():
    ml = MLService()
    matcher = MatchingService(ml)
    res = matcher.rank_jobs({'skills': ['Python']}, [])
    assert isinstance(res, list)
    assert len(res) == 0


def test_create_job_profile():
    ml = MLService()
    matcher = MatchingService(ml)
    job = Job(
        id='1',
        title='Dev',
        company='X',
        location='Remote',
        description='Develop stuff',
    )
    profile = matcher.create_job_profile(job)
    assert 'Dev' in profile
