import pytest
import numpy as np
from backend.services.ml_service import MLService
import time


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture(scope="module")
def ml_service():
    """
    Fixture that creates ML service once for all tests
    Using scope="module" so model is loaded only once (faster tests)
    """
    return MLService()


# ============================================================================
# TEST MODEL LOADING
# ============================================================================


class TestModelLoading:
    """
    Test that the SBERT model loads correctly
    """

    def test_model_loads_successfully(self, ml_service):
        """
        Test that model is loaded and not None
        """
        assert ml_service.model is not None

    def test_model_name_is_correct(self, ml_service):
        """
        Test that the correct model is loaded
        """
        # The model should be 'all-MiniLM-L6-v2' or whatever model chosen
        model_name = ml_service.model._modules["0"].auto_model.name_or_path
        assert "MiniLM" in model_name or "all-MiniLM-L6-v2" in model_name

    def test_cache_initialized(self, ml_service):
        """
        Test that embedding cache is initialized
        """
        assert hasattr(ml_service, "_cache")
        assert isinstance(ml_service._cache, dict)


# ============================================================================
# TEST ENCODE_TEXT
# ============================================================================


class TestEncodeText:
    """
    Test text encoding/embedding generation
    """

    def test_encode_text_returns_numpy_array(self, ml_service):
        """
        Test that encoding returns numpy array
        """
        text = "Python developer"
        embedding = ml_service.encode_text(text)

        assert isinstance(embedding, np.ndarray)

    def test_embedding_has_correct_shape(self, ml_service):
        """
        Test that embedding has correct dimension (384 for MiniLM)
        """
        text = "Machine Learning Engineer"
        embedding = ml_service.encode_text(text)

        assert embedding.shape == (384,)

    def test_embedding_is_normalized(self, ml_service):
        """
        Test that embeddings are normalized (unit length)
        """
        text = "Data Scientist"
        embedding = ml_service.encode_text(text)

        # For normalized vectors, norm should be close to 1.0
        norm = np.linalg.norm(embedding)
        assert 0.99 <= norm <= 1.01  # Allow small floating point error

    def test_empty_string_encoding(self, ml_service):
        """
        Test encoding empty string
        """
        embedding = ml_service.encode_text("")

        # Should still return valid embedding
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (384,)

    def test_long_text_encoding(self, ml_service):
        """
        Test encoding very long text
        """
        long_text = "Python developer " * 100  # 200 words
        embedding = ml_service.encode_text(long_text)

        # Should still work (model truncates internally)
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (384,)

    def test_special_characters_encoding(self, ml_service):
        """
        Test encoding text with special characters
        """
        text = "C++ and C# developer with .NET experience!"
        embedding = ml_service.encode_text(text)

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (384,)

    def test_unicode_text_encoding(self, ml_service):
        """
        Test encoding text with unicode characters
        """
        text = "Développeur Python avec expérience en données 数据科学家"
        embedding = ml_service.encode_text(text)

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (384,)

    def test_same_text_produces_same_embedding(self, ml_service):
        """
        Test that encoding same text twice gives identical results
        """
        text = "Software Engineer"
        embedding1 = ml_service.encode_text(text)
        embedding2 = ml_service.encode_text(text)

        # Should be exactly equal (due to caching or deterministic model)
        assert np.array_equal(embedding1, embedding2)

    def test_different_text_produces_different_embeddings(self, ml_service):
        """
        Test that different texts produce different embeddings
        """
        text1 = "Python developer"
        text2 = "Java developer"

        embedding1 = ml_service.encode_text(text1)
        embedding2 = ml_service.encode_text(text2)

        # Should NOT be equal
        assert not np.array_equal(embedding1, embedding2)

    def test_case_sensitivity(self, ml_service):
        """
        Test that model handles case differences
        """
        text1 = "Python Developer"
        text2 = "python developer"

        embedding1 = ml_service.encode_text(text1)
        embedding2 = ml_service.encode_text(text2)

        # Should be very similar (high similarity)
        similarity = np.dot(embedding1, embedding2)
        assert similarity > 0.95  # Very high similarity despite case difference


# ============================================================================
# TEST CACHING
# ============================================================================


class TestCaching:
    """
    Test embedding caching functionality
    """

    def test_caching_works(self, ml_service):
        """Test that caching stores and retrieves embeddings"""
        # Clear cache first
        ml_service._cache.clear()

        text = "Test text for caching"

        # First call - should add to cache
        embedding1 = ml_service.encode_text(text)
        cache_size_after_first = len(ml_service._cache)

        # Second call - should use cache
        embedding2 = ml_service.encode_text(text)
        cache_size_after_second = len(ml_service._cache)

        assert np.array_equal(embedding1, embedding2)
        assert cache_size_after_first == cache_size_after_second  # Cache size unchanged

    def test_cache_improves_performance(self, ml_service):
        """
        Test that cached calls are faster
        """
        ml_service._cache.clear()

        text = "Performance test text for ML encoding"

        # First call (cold cache)
        start = time.time()
        ml_service.encode_text(text)
        first_call_time = time.time() - start

        # Second call (warm cache)
        start = time.time()
        ml_service.encode_text(text)
        second_call_time = time.time() - start

        # Cached call should be significantly faster
        # (At least 10x faster, usually much more)
        assert second_call_time < first_call_time / 10
        print(
            f"\nFirst call: {first_call_time*1000:.2f}ms, "
            f"Cached call: {second_call_time*1000:.4f}ms"
        )

    def test_different_texts_cached_separately(self, ml_service):
        """
        Test that different texts get separate cache entries
        """
        ml_service._cache.clear()

        text1 = "Python developer"
        text2 = "Java developer"

        ml_service.encode_text(text1)
        ml_service.encode_text(text2)

        # Should have 2 entries in cache
        assert len(ml_service._cache) == 2


# ============================================================================
# TEST CALCULATE_SIMILARITY
# ============================================================================


class TestCalculateSimilarity:
    """
    Test similarity calculation between embeddings
    """

    def test_similarity_returns_float(self, ml_service):
        """
        Test that similarity returns a float
        """
        text1 = "Python developer"
        text2 = "Python programmer"

        emb1 = ml_service.encode_text(text1)
        emb2 = ml_service.encode_text(text2)

        similarity = ml_service.calculate_similarity(emb1, emb2)

        assert isinstance(similarity, float)

    def test_similarity_range(self, ml_service):
        """
        Test that similarity is in valid range [0, 1]
        """
        text1 = "Machine Learning Engineer"
        text2 = "Data Scientist"

        emb1 = ml_service.encode_text(text1)
        emb2 = ml_service.encode_text(text2)

        similarity = ml_service.calculate_similarity(emb1, emb2)

        assert 0.0 <= similarity <= 1.0

    def test_identical_text_high_similarity(self, ml_service):
        """
        Test that identical texts have similarity close to 1.0
        """
        text = "Software Engineer"

        emb1 = ml_service.encode_text(text)
        emb2 = ml_service.encode_text(text)

        similarity = ml_service.calculate_similarity(emb1, emb2)

        # Should be very close to 1.0 (might not be exactly 1.0 due to floating point)
        assert similarity > 0.99

    def test_similar_texts_high_similarity(self, ml_service):
        """
        Test that semantically similar texts have high similarity
        """
        text1 = "Python developer"
        text2 = "Python programmer"

        emb1 = ml_service.encode_text(text1)
        emb2 = ml_service.encode_text(text2)

        similarity = ml_service.calculate_similarity(emb1, emb2)

        # Should be high similarity (> 0.7)
        assert similarity > 0.7

    def test_different_texts_lower_similarity(self, ml_service):
        """
        Test that unrelated texts have lower similarity
        """
        text1 = "Python developer"
        text2 = "Professional chef"

        emb1 = ml_service.encode_text(text1)
        emb2 = ml_service.encode_text(text2)

        similarity = ml_service.calculate_similarity(emb1, emb2)

        # Should be lower similarity (< 0.5)
        assert similarity < 0.5

    def test_similarity_comparison(self, ml_service):
        """
        Test that similarity correctly ranks semantic closeness
        """
        text_query = "Python developer"
        text_similar = "Python programmer"
        text_related = "Software engineer"
        text_unrelated = "Chef"

        emb_query = ml_service.encode_text(text_query)
        emb_similar = ml_service.encode_text(text_similar)
        emb_related = ml_service.encode_text(text_related)
        emb_unrelated = ml_service.encode_text(text_unrelated)

        sim_similar = ml_service.calculate_similarity(emb_query, emb_similar)
        sim_related = ml_service.calculate_similarity(emb_query, emb_related)
        sim_unrelated = ml_service.calculate_similarity(emb_query, emb_unrelated)

        # Similarity should decrease: similar > related > unrelated
        assert sim_similar > sim_related
        assert sim_related > sim_unrelated

    def test_similarity_is_symmetric(self, ml_service):
        """
        Test that similarity(A,B) == similarity(B,A)
        """
        text1 = "Data Scientist"
        text2 = "Machine Learning Engineer"

        emb1 = ml_service.encode_text(text1)
        emb2 = ml_service.encode_text(text2)

        sim_ab = ml_service.calculate_similarity(emb1, emb2)
        sim_ba = ml_service.calculate_similarity(emb2, emb1)

        # Should be equal
        assert abs(sim_ab - sim_ba) < 0.0001  # Allow tiny floating point error


# ============================================================================
# TEST BATCH_SIMILARITY
# ============================================================================


class TestBatchSimilarity:
    """
    Test batch similarity calculation
    """

    def test_batch_similarity_returns_list(self, ml_service):
        """
        Test that batch similarity returns a list
        """
        query = "Python developer"
        jobs = ["Python programmer", "Java developer", "Data scientist"]

        query_emb = ml_service.encode_text(query)
        job_embs = [ml_service.encode_text(job) for job in jobs]

        similarities = ml_service.batch_similarity(query_emb, job_embs)

        assert isinstance(similarities, list)

    def test_batch_similarity_correct_length(self, ml_service):
        """
        Test that batch returns correct number of similarities
        """
        query = "Python developer"
        jobs = ["Job 1", "Job 2", "Job 3", "Job 4", "Job 5"]

        query_emb = ml_service.encode_text(query)
        job_embs = [ml_service.encode_text(job) for job in jobs]

        similarities = ml_service.batch_similarity(query_emb, job_embs)

        assert len(similarities) == len(jobs)

    def test_batch_similarity_values_valid(self, ml_service):
        """
        Test that all batch similarity values are in valid range
        """
        query = "Machine Learning"
        jobs = ["ML Engineer", "Data Analyst", "Chef", "Teacher"]

        query_emb = ml_service.encode_text(query)
        job_embs = [ml_service.encode_text(job) for job in jobs]

        similarities = ml_service.batch_similarity(query_emb, job_embs)

        # All should be floats in range [0, 1]
        assert all(isinstance(s, float) for s in similarities)
        assert all(0.0 <= s <= 1.0 for s in similarities)

    def test_batch_matches_individual_calculations(self, ml_service):
        """
        Test that batch gives same results as individual calculations
        """
        query = "Python developer"
        jobs = ["Python programmer", "Java developer"]

        query_emb = ml_service.encode_text(query)
        job_embs = [ml_service.encode_text(job) for job in jobs]

        # Batch calculation
        batch_sims = ml_service.batch_similarity(query_emb, job_embs)

        # Individual calculations
        individual_sims = [
            ml_service.calculate_similarity(query_emb, job_emb) for job_emb in job_embs
        ]

        # Should be very close (allow tiny floating point differences)
        for batch_sim, indiv_sim in zip(batch_sims, individual_sims):
            assert abs(batch_sim - indiv_sim) < 0.0001

    def test_batch_with_single_job(self, ml_service):
        """
        Test batch similarity with only one job
        """
        query = "Developer"
        jobs = ["Software Engineer"]

        query_emb = ml_service.encode_text(query)
        job_embs = [ml_service.encode_text(job) for job in jobs]

        similarities = ml_service.batch_similarity(query_emb, job_embs)

        assert len(similarities) == 1
        assert isinstance(similarities[0], float)

    def test_batch_with_many_jobs(self, ml_service):
        """
        Test batch similarity with many jobs
        """
        query = "Python developer"
        jobs = [f"Job title {i}" for i in range(50)]

        query_emb = ml_service.encode_text(query)
        job_embs = [ml_service.encode_text(job) for job in jobs]

        similarities = ml_service.batch_similarity(query_emb, job_embs)

        assert len(similarities) == 50
        assert all(0.0 <= s <= 1.0 for s in similarities)


# ============================================================================
# TEST EDGE CASES
# ============================================================================


class TestEdgeCases:
    """
    Test edge cases and error handling
    """

    def test_encode_whitespace_only(self, ml_service):
        """
        Test encoding text with only whitespace
        """
        text = "     "
        embedding = ml_service.encode_text(text)

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (384,)

    def test_encode_newlines(self, ml_service):
        """
        Test encoding text with newlines
        """
        text = "Python developer\n\nExperience with ML"
        embedding = ml_service.encode_text(text)

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (384,)

    def test_encode_numbers_only(self, ml_service):
        """
        Test encoding text with only numbers
        """
        text = "12345 67890"
        embedding = ml_service.encode_text(text)

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (384,)

    def test_batch_similarity_empty_list(self, ml_service):
        """
        Test batch similarity with empty job list
        """
        query_emb = ml_service.encode_text("Python developer")
        job_embs = []

        similarities = ml_service.batch_similarity(query_emb, job_embs)

        assert similarities == []


# ============================================================================
# TEST PERFORMANCE
# ============================================================================


class TestPerformance:
    """
    Test performance characteristics
    """

    def test_single_encoding_speed(self, ml_service):
        """
        Test that single encoding completes quickly
        """
        text = "Python developer with machine learning experience"

        start = time.time()
        ml_service.encode_text(text)
        elapsed = time.time() - start

        # Should complete in under 100ms (adjust based on your hardware)
        assert elapsed < 0.1
        print(f"\nSingle encoding time: {elapsed*1000:.2f}ms")

    def test_batch_processing_speed(self, ml_service):
        """
        Test that batch processing 50 jobs completes in reasonable time
        """
        query = "Python developer"
        jobs = [f"Job description {i} with Python" for i in range(50)]

        query_emb = ml_service.encode_text(query)

        start = time.time()
        job_embs = [ml_service.encode_text(job) for job in jobs]
        ml_service.batch_similarity(query_emb, job_embs)
        elapsed = time.time() - start

        # Should complete in under 5 seconds
        assert elapsed < 5
        print(
            f"\n50 jobs processed in {elapsed:.2f}s ({elapsed/50*1000:.2f}ms per job)"
        )

    def test_cache_size_reasonable(self, ml_service):
        """
        Test that cache doesn't grow unreasonably large
        """
        ml_service._cache.clear()

        # Add 100 different texts
        for i in range(100):
            ml_service.encode_text(f"Text number {i}")

        cache_size = len(ml_service._cache)

        # Cache should have 100 entries (or less if we have max_cache_size)
        assert cache_size <= 100


# ============================================================================
# INTEGRATION TEST
# ============================================================================


class TestIntegration:
    """
    Integration tests for complete workflow
    """

    def test_complete_job_matching_workflow(self, ml_service):
        """
        Test complete workflow from encoding to ranking
        """
        # User profile
        user_profile = "Python developer with machine learning and data analysis skills"

        # Job descriptions
        jobs = [
            "Python developer needed for ML projects",
            "Java backend engineer for enterprise systems",
            "Data scientist with Python and ML experience",
            "Frontend React developer",
            "Machine learning engineer - Python required",
        ]

        # Encode user profile
        user_emb = ml_service.encode_text(user_profile)

        # Encode all jobs
        job_embs = [ml_service.encode_text(job) for job in jobs]

        # Calculate similarities
        similarities = ml_service.batch_similarity(user_emb, job_embs)

        # Rank jobs
        ranked_indices = sorted(
            range(len(similarities)), key=lambda i: similarities[i], reverse=True
        )

        # Top job should be one of the ML/Python focused ones (jobs 0, 2, or 4)
        assert ranked_indices[0] in [0, 2, 4]

        # Frontend job should be ranked low
        frontend_rank = ranked_indices.index(3)
        assert frontend_rank >= 3

        print("\nJob ranking:")
        for rank, idx in enumerate(ranked_indices, 1):
            print(f"{rank}. {jobs[idx][:50]}... (score: {similarities[idx]:.3f})")
