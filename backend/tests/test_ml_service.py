import pytest
import numpy as np
from services.ml_service import MLService


@pytest.fixture
def ml_service():
    return MLService()


def test_model_loads(ml_service):
    """
    Test if the ML model loads correctly
    """
    assert ml_service.model is not None


def test_encode_shape(ml_service):
    """
    Test if text encoding returns correct shape
    """
    text = "Python developer with machine learning experience"
    embedding = ml_service.encode_text(text)
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (384,)  # Model output dimension


def test_similarity_calculation(ml_service):
    """
    Test similarity calculation between similar and dissimilar texts
    """
    text1 = "Python developer"
    text2 = "Python programmer"
    text3 = "Chef"

    emb1 = ml_service.encode_text(text1)
    emb2 = ml_service.encode_text(text2)
    emb3 = ml_service.encode_text(text3)

    sim_similar = ml_service.calculate_similarity(emb1, emb2)
    sim_different = ml_service.calculate_similarity(emb1, emb3)

    # Similar texts should have higher similarity
    assert sim_similar > sim_different
    assert 0 <= sim_similar <= 1
    assert 0 <= sim_different <= 1


def test_batch_similarity(ml_service):
    """
    Test batch similarity calculation
    """
    query = "Data scientist with Python"
    jobs = ["Python data analyst", "Java backend developer", "Data science engineer"]

    query_emb = ml_service.encode_text(query)
    job_embs = [ml_service.encode_text(job) for job in jobs]

    similarities = ml_service.batch_similarity(query_emb, job_embs)

    assert isinstance(similarities, list)
    assert len(similarities) == len(jobs)
    assert all(isinstance(s, (float, np.floating)) for s in similarities)
    assert all(0.0 <= s <= 1.0 for s in similarities)


def test_caching_works(ml_service):
    """
    Test embedding caching
    """
    text = "Test text for caching"

    # First call
    emb1 = ml_service.encode_text(text)
    cache_size_1 = len(ml_service._cache)

    # Second call (should use cache)
    emb2 = ml_service.encode_text(text)
    cache_size_2 = len(ml_service._cache)

    assert np.array_equal(emb1, emb2)
    assert cache_size_1 == cache_size_2
