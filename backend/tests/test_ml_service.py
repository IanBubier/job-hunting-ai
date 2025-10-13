import numpy as np

from backend.services.ml_service import MLService


def test_ml_service_encode_shape():
    ml = MLService()
    emb = ml.encode_text('Test text')
    assert isinstance(emb, (list, np.ndarray))
    # placeholder returns 384-dim zero vector
    assert len(emb) == 384


def test_batch_similarity_returns_list():
    ml = MLService()
    q = ml.encode_text('query')
    jobs = [ml.encode_text('a'), ml.encode_text('b')]
    sims = ml.batch_similarity(q, jobs)
    assert isinstance(sims, list)
    assert len(sims) == len(jobs)
